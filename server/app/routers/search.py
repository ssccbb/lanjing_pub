"""搜索接口"""
import asyncio
import time
from typing import List, Dict, Tuple
from datetime import datetime

from fastapi import APIRouter, Query, Depends, Request, Body
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.database import get_db
from app.services.movie_service import MovieService
from app.models.search import UserSearch
from app.cache import cache_get, cache_set, cache_key
from app.utils.response import Response
from app.utils.logger import get_logger
from app.utils.antibot import check_user_agent

logger = get_logger(__name__)
router = APIRouter(dependencies=[Depends(check_user_agent)])

# 搜索频率限制存储: {ip: (count, first_request_time)}
_search_rate_limit: Dict[str, Tuple[int, float]] = {}


def _check_search_rate_limit(ip: str, max_requests: int = 30, window_seconds: int = 60) -> bool:
    """
    检查搜索频率限制
    :param ip: 客户端IP
    :param max_requests: 时间窗口内最大请求数
    :param window_seconds: 时间窗口（秒）
    :return: True 表示允许请求，False 表示超过限制
    """
    now = time.time()

    if ip in _search_rate_limit:
        count, first_time = _search_rate_limit[ip]

        # 检查是否在时间窗口内
        if now - first_time < window_seconds:
            if count >= max_requests:
                return False
            _search_rate_limit[ip] = (count + 1, first_time)
        else:
            # 重置时间窗口
            _search_rate_limit[ip] = (1, now)
    else:
        _search_rate_limit[ip] = (1, now)

    return True


def _get_client_ip(request: Request) -> str:
    """获取客户端IP"""
    forwarded = request.headers.get("x-forwarded-for")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.client.host if request.client else "unknown"


@router.get("/suggest")
async def search_suggest(
    request: Request,
    q: str = Query(..., min_length=1, description="搜索关键词"),
    limit: int = Query(10, ge=1, le=20)
):
    """搜索建议"""
    client_ip = _get_client_ip(request)

    # 检查频率限制（每分钟最多60次）
    if not _check_search_rate_limit(client_ip, max_requests=60, window_seconds=60):
        return Response.success([])  # 超过限制返回空，不报错

    if not q or len(q.strip()) < 1:
        return Response.success([])

    cache_k = cache_key("search", "suggest", q.lower().strip())
    cached = await cache_get(cache_k)
    if cached:
        return Response.success(cached)

    # TODO: 从搜索历史中匹配热门建议
    # 临时返回示例
    suggests = [
        f"{q} 电影",
        f"{q} 电视剧",
        f"{q} 动漫",
        f"{q} 高清",
    ][:limit]

    await cache_set(cache_k, suggests, expire=600)  # 缓存10分钟
    return Response.success(suggests)


@router.get("")
async def search(
    request: Request,
    q: str = Query(..., min_length=1, description="搜索关键词"),
    page: int = Query(1, ge=1),
    page_size: int = Query(30, ge=1, le=100),
    category: int = Query(None, description="分类筛选"),
    db: AsyncSession = Depends(get_db)
):
    """
    搜索影片 - 优化版本
    :param q: 搜索关键词（支持多个，用空格分隔）
    :param page: 页码
    :param page_size: 每页数量
    :param category: 分类筛选（可选）
    """
    client_ip = _get_client_ip(request)

    # 检查搜索频率限制（每分钟最多30次）
    if not _check_search_rate_limit(client_ip, max_requests=30, window_seconds=60):
        logger.warning(f"Search rate limit exceeded for IP: {client_ip}")
        return Response.error("搜索太频繁，请稍后再试")

    # 限制最大页大小
    page_size = min(page_size, 100)

    # 解析关键词（限制最大关键词数量）
    keywords = [k.strip() for k in q.split() if k.strip()][:5]

    if not keywords:
        return Response.error("请输入有效的搜索关键词")

    # 分类
    categories = [category] if category else None

    # 计算实际需要查询的数量（根据页码）
    limit = min(page * page_size, 500)  # 最大返回500条

    # 搜索
    movies = await MovieService.search_movies(
        session=db,
        keywords=keywords,
        categories=categories,
        limit=limit
    )

    # 分页
    total = len(movies)
    start = (page - 1) * page_size
    end = start + page_size
    page_movies = movies[start:end]

    return Response.success({
        "keyword": q,
        "page": page,
        "page_size": page_size,
        "total": total,
        "list": page_movies
    })


@router.get("/hot")
async def hot_keywords():
    """热门搜索词"""
    cache_k = cache_key("search", "hot")
    cached = await cache_get(cache_k)
    if cached:
        return Response.success(cached)

    # TODO: 从数据库或Redis获取真实的热门搜索
    hot_words = [
        "动作片", "科幻", "爱情", "喜剧", "恐怖",
        "悬疑", "动画", "漫威", "国产剧", "韩剧"
    ]

    await cache_set(cache_k, hot_words, expire=3600)  # 缓存1小时
    return Response.success(hot_words)


@router.get("/history")
async def search_history():
    """搜索历史（热门）"""
    cache_k = cache_key("search", "history")
    cached = await cache_get(cache_k)
    if cached:
        return Response.success(cached)

    # TODO: 从数据库获取真实的搜索历史
    history = ["海贼王", "火影忍者", "复仇者联盟", "流浪地球"]

    await cache_set(cache_k, history, expire=1800)  # 缓存30分钟
    return Response.success(history)


@router.post("/record")
async def record_search(
    series_titles: List[str] = Body(..., description="影片名称列表，格式: [\"影片名1\", \"影片名2\"]")
):
    """
    记录搜索历史
    - 有记录则 search_count + 1
    - 无记录则新增（默认 count=1）
    - 异步处理，不阻塞响应
    """
    # 立即返回成功，后台异步处理（使用新会话）
    asyncio.create_task(_update_search_records(series_titles))

    return Response.success({"message": "搜索记录已提交"})


async def _update_search_records(series_titles: List[str]):
    """后台更新搜索记录（使用独立的数据库会话）"""
    from app.database import AsyncSessionLocal

    async with AsyncSessionLocal() as db:
        try:
            now_timestamp = int(datetime.now().timestamp())

            for series_title in series_titles:
                if not series_title:
                    continue

                # 先查询是否已存在
                result = await db.execute(
                    select(UserSearch).where(UserSearch.series_title == series_title)
                )
                existing = result.scalar_one_or_none()

                if existing:
                    # 更新搜索次数
                    existing.search_count += 1
                    existing.update_time = now_timestamp
                else:
                    # 新增记录
                    new_record = UserSearch(
                        series_title=series_title,
                        search_count=1,
                        update_time=now_timestamp
                    )
                    db.add(new_record)

            await db.commit()
        except Exception:
            await db.rollback()


@router.get("/hot-records")
async def get_hot_search_records(
    limit: int = Query(10, ge=1, le=100),
    db: AsyncSession = Depends(get_db)
):
    """
    从搜索记录表获取热门搜索
    :param limit: 返回数量，默认10条
    """
    # 缓存键
    cache_k = cache_key("search", "hot-records", limit)
    cached = await cache_get(cache_k)
    if cached:
        return Response.success({"list": cached})

    result = await db.execute(
        select(UserSearch)
        .order_by(UserSearch.search_count.desc())
        .limit(limit)
    )
    searches = result.scalars().all()

    data = [
        {
            "id": s.id,
            "series_title": s.series_title,
            "search_count": s.search_count
        }
        for s in searches
    ]

    # 缓存 30 分钟
    await cache_set(cache_k, data, expire=1800)
    return Response.success({"list": data})
