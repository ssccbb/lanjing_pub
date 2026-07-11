"""FastAPI 应用入口"""
import asyncio
import os
import time
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware

from app.config import settings
from app.database import close_db, AsyncSessionLocal
from app.cache import init_redis, close_redis, cache_key, cache_set
from app.routers import page, content, search, user, config, feedback, user_activity, danmaku
from app.utils.logger import get_logger, get_access_logger
from app.utils.crypto import decrypt_with_author
from app.utils.antibot import is_crawler, get_crawler_info

logger = get_logger(__name__)
access_logger = get_access_logger()

# 加载 author-key（从 pydantic settings 或环境变量）
from app.config import settings
AUTHOR_KEY = getattr(settings, 'NUXT_PUBLIC_AUTHOR_KEY', '') or os.environ.get('NUXT_PUBLIC_AUTHOR_KEY') or os.environ.get('AUTHOR_KEY', '')
if AUTHOR_KEY:
    AUTHOR_KEY = AUTHOR_KEY.strip()
    logger.info("Author key loaded from environment variable")
else:
    logger.warning("AUTHOR_KEY not configured in environment variables")


async def verify_signature(request: Request):
    """
    验证请求签名
    读取 header 中的 signature，解密后与 author-key 比对
    """
    # 获取真实客户端IP
    client_ip = get_client_ip(request)

    # # 如果 author-key 未配置，跳过鉴权（开发模式）
    # if not AUTHOR_KEY:
    #     logger.debug(f"Author key not configured, skipping signature verification for {client_ip}")
    #     return True

    # 获取 signature header
    signature = request.headers.get('signature')

    if not signature:
        logger.warning(f"Missing signature header from {client_ip}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing signature"
        )

    # 检查是否为 32 位
    if len(signature) != 32:
        logger.warning(f"Invalid signature length: {len(signature)} from {client_ip}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid signature format"
        )

    try:
        # 解密签名（使用 author-key 作为种子）
        decrypted = decrypt_with_author(signature)
    except Exception as e:
        logger.warning(f"Failed to decrypt signature from {client_ip}: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid signature"
        )

    # 比对 author-key
    if decrypted != AUTHOR_KEY:
        logger.warning(f"Signature mismatch from {client_ip}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid signature"
        )

    return True


async def refresh_home_cache():
    """后台任务：定期刷新首页缓存"""
    from app.services.movie_service import MovieService

    while True:
        try:
            logger.info("[Cache Refresh] Starting home cache refresh...")

            # 1. 刷新Banner数据（完整字段）- type=1
            async with AsyncSessionLocal() as session:
                try:
                    banner_ids = await MovieService.get_home_page_data_by_type(session, data_type=1)
                    banners = await MovieService.get_movies_by_ids_with_full_fields(session, banner_ids)
                finally:
                    await session.close()

            # 2. 刷新最新上线（轻量级）- type=2
            async with AsyncSessionLocal() as session:
                try:
                    newest_ids = await MovieService.get_home_page_data_by_type(session, data_type=2)
                    newest = await MovieService.get_movies_by_ids_lite(session, newest_ids[:9])
                finally:
                    await session.close()

            # 3. 刷新各分类推荐（轻量级）
            # type: 3=热门电影, 4=热播电视剧, 5=热门综艺, 6=动漫推荐
            categories = {}
            type_mapping = {
                3: "movies",    # 热门电影
                4: "tv",        # 热播电视剧
                5: "series",    # 热门综艺
                6: "cartoon"    # 动漫推荐
            }
            for type_id, cat_name in type_mapping.items():
                async with AsyncSessionLocal() as session:
                    try:
                        cat_ids = await MovieService.get_home_page_data_by_type(session, data_type=type_id)
                        categories[cat_name] = await MovieService.get_movies_by_ids_lite(session, cat_ids[:12])
                    finally:
                        await session.close()

            # 组装并写入缓存（去掉recommends）
            data = {
                "banners": banners,      # 完整字段
                "newest": newest,        # 轻量级
                "categories": categories # 轻量级
            }
            cache_k = cache_key("page", "home")
            await cache_set(cache_k, data, expire=300)
            logger.info("[Cache Refresh] Home cache refreshed successfully")

        except Exception as e:
            logger.error(f"[Cache Refresh] Failed: {e}")

        # 每3分钟刷新一次（小于5分钟过期时间，确保缓存不过期）
        await asyncio.sleep(180)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    logger.info(f"Starting {settings.app_name} v{settings.app_version}")

    # 初始化Redis（失败不影响主应用）
    try:
        await init_redis()
        logger.info("Redis connected")
    except Exception as e:
        logger.warning(f"Redis connection failed: {e}. Running without cache.")

    # 预热首页缓存（从home_page_data表获取配置）
    try:
        from app.services.movie_service import MovieService

        logger.info("Preheating cache...")

        # 1. 预热Banner（完整字段）- type=1
        async with AsyncSessionLocal() as session:
            try:
                banner_ids = await MovieService.get_home_page_data_by_type(session, data_type=1)
                await MovieService.get_movies_by_ids_with_full_fields(session, banner_ids)
            finally:
                await session.close()

        # 2. 预热最新上线（轻量级）- type=2
        async with AsyncSessionLocal() as session:
            try:
                newest_ids = await MovieService.get_home_page_data_by_type(session, data_type=2)
                await MovieService.get_movies_by_ids_lite(session, newest_ids[:9])
            finally:
                await session.close()

        # 3. 预热各分类列表（轻量级）- type=3,4,5,6
        # 3=热门电影, 4=热播电视剧, 5=热门综艺, 6=动漫推荐
        for type_id in [3, 4, 5, 6]:
            async with AsyncSessionLocal() as session:
                try:
                    cat_ids = await MovieService.get_home_page_data_by_type(session, data_type=type_id)
                    await MovieService.get_movies_by_ids_lite(session, cat_ids[:12])
                finally:
                    await session.close()

        logger.info("Cache preheated successfully")
    except Exception as e:
        logger.warning(f"Cache preheat failed: {e}")

    # 启动后台定时刷新任务
    tasks = [
        asyncio.create_task(refresh_home_cache()),
    ]
    logger.info("Background cache refresh tasks started")

    yield

    # 关闭时取消后台任务
    for task in tasks:
        task.cancel()
        try:
            await task
        except asyncio.CancelledError:
            pass

    logger.info("Shutting down...")
    try:
        await close_redis()
    except Exception as e:
        logger.debug(f"Close redis failed: {e}")

    try:
        await close_db()
    except Exception as e:
        logger.debug(f"Close db failed: {e}")

    logger.info("Cleanup completed")


app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="影视模版网站后端API服务",
    docs_url="/docs" if settings.debug else None,
    redoc_url="/redoc" if settings.debug else None,
    lifespan=lifespan,
)

# GZip压缩中间件（提升传输效率）
app.add_middleware(
    GZipMiddleware,
    minimum_size=1000,  # 只对大于1KB的响应进行压缩
)

# CORS中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "DELETE", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization", "Signature", "X-Requested-With", "Accept", "Origin"],
    expose_headers=["X-Process-Time"],
    max_age=600,
)


# 可信代理IP列表（生产环境应配置为实际反向代理IP）
TRUSTED_PROXIES = []  # 例如: ['127.0.0.1', '10.0.0.1']


def get_client_ip(request: Request) -> str:
    """获取客户端真实IP（支持反向代理）

    安全注意：只在配置了可信代理时信任 X-Forwarded-For 头，
    否则直接使用连接IP，防止客户端伪造IP
    """
    # 获取直接连接的客户端IP
    client_host = request.client.host if request.client else "unknown"

    # 如果没有配置可信代理，直接使用连接IP
    if not TRUSTED_PROXIES:
        return client_host

    # 检查是否来自可信代理
    if client_host not in TRUSTED_PROXIES:
        return client_host

    # 从可信代理获取真实IP
    forwarded_for = request.headers.get("x-forwarded-for")
    if forwarded_for:
        # X-Forwarded-For: client, proxy1, proxy2
        # 取第一个作为客户端真实IP
        return forwarded_for.split(",")[0].strip()

    real_ip = request.headers.get("x-real-ip")
    if real_ip:
        return real_ip

    return client_host


# 敏感参数列表，日志中需要过滤
SENSITIVE_PARAMS = {'password', 'token', 'secret', 'signature', 'key', 'auth', 'credential'}


def _sanitize_query_params(query_string: str) -> str:
    """过滤敏感参数，防止泄露到日志中"""
    if not query_string:
        return ""

    import re
    params = []
    for param in query_string.split('&'):
        if '=' in param:
            key, value = param.split('=', 1)
            # 检查参数名是否包含敏感关键词
            if any(sensitive in key.lower() for sensitive in SENSITIVE_PARAMS):
                params.append(f"{key}=***")
            else:
                # 截断过长的参数值
                if len(value) > 100:
                    value = value[:100] + "..."
                params.append(f"{key}={value}")
        else:
            params.append(param)
    return '&'.join(params)


@app.middleware("http")
async def performance_middleware(request: Request, call_next):
    """性能监控中间件 - 记录所有请求耗时和访问日志"""
    start_time = time.perf_counter()
    client_ip = get_client_ip(request)
    method = request.method
    path = request.url.path

    # 获取并过滤 query 参数
    raw_query = str(request.query_params) if request.query_params else ""
    safe_query = _sanitize_query_params(raw_query)
    full_path = f"{path}{f'?{safe_query}' if safe_query else ''}"

    # 获取请求头信息
    user_agent = request.headers.get("user-agent", "-")
    referer = request.headers.get("referer", "-")
    accept_lang = request.headers.get("accept-language", "-")
    origin = request.headers.get("origin", "-")

    # 获取真实客户端IP（考虑反向代理）
    forwarded_for = request.headers.get("x-forwarded-for", "-")
    real_ip = request.headers.get("x-real-ip", "-")

    # 反爬虫检查：检测爬虫 User-Agent 并拦截
    crawler_type = get_crawler_info(user_agent if user_agent != "-" else None)
    if crawler_type:
        logger.warning(f"🤖 [Crawler Blocked] {crawler_type} | IP: {client_ip} | Path: {path}")
        # 构造 403 响应
        from fastapi.responses import JSONResponse
        return JSONResponse(
            status_code=403,
            content={"code": 403, "message": "Access denied", "data": None}
        )

    # 记录请求开始（使用安全的路径）
    logger.info(f"➡️  [{method}] {path}{'?...' if raw_query else ''} - Client: {client_ip}")

    try:
        response = await call_next(request)
        process_time = time.perf_counter() - start_time

        status_code = response.status_code

        # 根据耗时选择日志级别
        if process_time > 1.0:
            level = "warning"
            emoji = "🔴"
        elif process_time > 0.5:
            level = "info"
            emoji = "🟡"
        else:
            level = "info"
            emoji = "🟢"

        # 格式化耗时显示
        if process_time < 0.001:
            time_str = f"{process_time * 1000:.3f}ms"
        elif process_time < 1:
            time_str = f"{process_time * 1000:.1f}ms"
        else:
            time_str = f"{process_time:.2f}s"

        # 记录请求完成
        getattr(logger, level)(
            f"{emoji} [{method}] {path} - Status: {status_code} - Time: {time_str}"
        )

        # 记录详细访问日志（单独文件，使用过滤后的路径）
        # 格式: IP | Method | URL | Status | Time | User-Agent | Referer | Language
        access_logger.info(
            f"{client_ip} | {method} | {full_path} | {status_code} | {time_str} | "
            f"{user_agent} | {referer} | {accept_lang}"
        )

        # 添加响应头
        response.headers["X-Process-Time"] = str(process_time)
        # 只对 API 响应禁用缓存，静态资源不由 FastAPI 处理
        if path.startswith("/web/") or path.startswith("/pub/"):
            response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate"

        return response

    except Exception as e:
        process_time = time.perf_counter() - start_time
        logger.error(
            f"❌ [{method}] {path} - Error: {str(e)} - Time: {process_time:.3f}s"
        )
        # 记录异常访问日志
        access_logger.info(
            f"{client_ip} | {method} | {full_path} | ERROR | {process_time:.3f}s | "
            f"{user_agent} | {referer} | {accept_lang} | Error: {str(e)}"
        )
        raise

# 注册公开路由（无需签名）
app.include_router(user.pub_router, prefix="/pub/user", tags=["用户-公开接口"])
app.include_router(danmaku.pub_router, prefix="/pub", tags=["弹幕-公开接口"])

# 注册路由（添加签名鉴权）
app.include_router(page.router, prefix="/web/home", tags=["首页"], dependencies=[Depends(verify_signature)])
app.include_router(content.router, prefix="/web/movies", tags=["影片"], dependencies=[Depends(verify_signature)])
app.include_router(search.router, prefix="/web/search", tags=["搜索"], dependencies=[Depends(verify_signature)])
app.include_router(user.router, prefix="/web/user", tags=["用户"], dependencies=[Depends(verify_signature)])
app.include_router(config.router, prefix="/web/config", tags=["配置管理"], dependencies=[Depends(verify_signature)])
app.include_router(feedback.router, prefix="/web/feedback", tags=["反馈留言"], dependencies=[Depends(verify_signature)])
app.include_router(user_activity.router, prefix="/web/history", tags=["观看历史"], dependencies=[Depends(verify_signature)])
app.include_router(danmaku.web_router, prefix="/web", tags=["弹幕-用户接口"], dependencies=[Depends(verify_signature)])


@app.get("/")
async def root():
    """根路径"""
    return {
        "name": settings.app_name,
        "version": settings.app_version,
        "docs": "/docs"
    }


@app.get("/health")
async def health_check():
    """健康检查"""
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
    )
