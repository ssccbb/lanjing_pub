"""内容接口"""
import time
import asyncio
from typing import Optional

from fastapi import APIRouter, Depends, Request, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.database import get_db
from app.services.movie_service import MovieService, ActorService
from app.cache import cache_get, cache_set, cache_key
from app.utils.response import Response
from app.models.entities import Movie
from app.models.user_activity import UserWatchHistory

router = APIRouter()


@router.get("/{movie_id}")
async def get_movie(
    movie_id: str,
    db: AsyncSession = Depends(get_db)
):
    """获取影片信息（不含剧集）- 优化版本（添加缓存）"""
    movie = await MovieService.get_movie_by_id(
        session=db,
        movie_id=movie_id,
        contain_episodes=False
    )

    if not movie:
        return Response.not_found("影片不存在")

    return Response.success(movie)


@router.get("/{movie_id}/episodes")
async def get_episodes(
    movie_id: str,
    db: AsyncSession = Depends(get_db)
):
    """获取影片剧集列表"""
    movie = await MovieService.get_movie_by_id(
        session=db,
        movie_id=movie_id,
        contain_episodes=True
    )

    if not movie:
        return Response.not_found("影片不存在")

    return Response.success({
        "movie_id": movie_id,
        "episode_sources": movie.get("episode_sources", [])
    })


@router.get("/{movie_id}/related")
async def get_related(
    movie_id: str,
    db: AsyncSession = Depends(get_db)
):
    """获取相关推荐影片 - 优化版本"""
    # 先获取当前影片信息
    movie = await MovieService.get_movie_by_id(
        session=db,
        movie_id=movie_id,
        contain_episodes=False
    )

    if not movie:
        return Response.not_found("影片不存在")

    # 检查缓存
    cache_k = cache_key("movie", movie_id, "related")
    cached = await cache_get(cache_k)
    if cached:
        return Response.success(cached)

    # 获取推荐
    recommends = await MovieService.get_recommend_movies(
        session=db,
        title=movie.get("title"),
        category=movie.get("category"),
        search_keywords=movie.get("actors", [])[:3]
    )

    result = recommends[:24]
    await cache_set(cache_k, result, expire=1800)  # 缓存30分钟

    return Response.success(result)


@router.get("/actor/{actor_name}")
async def get_actor_detail(
    actor_name: str,
    db: AsyncSession = Depends(get_db)
):
    """获取演员详情及作品 - 优化版本（添加缓存）"""
    cache_k = cache_key("actor", actor_name)
    cached = await cache_get(cache_k)
    if cached:
        return Response.success(cached)

    # 获取演员信息
    actors = await ActorService.get_actors_by_names(db, [actor_name])
    actor = actors[0] if actors else None

    # 搜索该演员的影片（限制数量）
    movies = await MovieService.search_movies(
        session=db,
        keywords=[actor_name],
        limit=30
    )

    result = {
        "actor": actor,
        "movies": movies
    }

    await cache_set(cache_k, result, expire=3600)  # 缓存1小时
    return Response.success(result)


@router.get("/series/{series_title}")
async def get_series_movies(
    series_title: str,
    db: AsyncSession = Depends(get_db)
):
    """获取系列影片"""
    movies = await MovieService.get_movies_by_series(db, series_title)
    return Response.success({
        "series_title": series_title,
        "movies": movies
    })


@router.post("/{movie_id}/count")
async def update_movie_count(
    request: Request,
    background_tasks: BackgroundTasks,
    movie_id: str,
    recommend: Optional[bool] = None,
    db: AsyncSession = Depends(get_db)
):
    """
    更新影片计数
    :param movie_id: 影片ID
    :param recommend: True=推荐+1, False=不推荐+1, 不传=观看+1
    """
    success = await MovieService.update_movie_count(db, movie_id, recommend)

    if not success:
        return Response.error("影片不存在")

    # 如果是观看数+1，记录观看历史
    if recommend is None:
        # 获取影片详情（包含剧集信息）
        try:
            movie_id_int = int(movie_id)
            query = select(Movie).where(Movie.id == movie_id_int)
            result = await db.execute(query)
            movie = result.scalar_one_or_none()

            if movie:
                # 异步记录观看历史（不阻塞响应，使用 BackgroundTasks）
                accesstoken = request.headers.get("Authorization", "").replace("Bearer ", "")
                if accesstoken:
                    background_tasks.add_task(_save_watch_history, accesstoken, movie)
        except Exception as e:
            # 记录历史失败不影响主流程
            import logging
            logging.getLogger(__name__).error(f"记录观看历史失败: {e}")

    # 返回操作类型
    action = "watch"
    if recommend is True:
        action = "recommend"
    elif recommend is False:
        action = "unrecommend"

    return Response.success({
        "movie_id": movie_id,
        "action": action,
        "message": "计数更新成功"
    })


async def _save_watch_history(accesstoken: str, movie: Movie):
    """
    保存用户观看历史（后台任务执行，不影响主流程）
    使用数据库 upsert 语法，确保同一用户同一影片只有一条记录
    """
    try:
        import json
        from sqlalchemy.dialects.mysql import insert

        # 辅助函数：解析可能为JSON字符串的字段
        def parse_json_field(field_value):
            if not field_value:
                return []
            if isinstance(field_value, str):
                try:
                    return json.loads(field_value)
                except:
                    return []
            return field_value if isinstance(field_value, list) else []

        # 准备数据
        covers = parse_json_field(movie.covers)
        tags = parse_json_field(movie.tags)

        # 使用新的会话以避免影响主会话
        from app.database import AsyncSessionLocal
        async with AsyncSessionLocal() as session:
            # 使用 MySQL 的 INSERT ... ON DUPLICATE KEY UPDATE 语法
            stmt = insert(UserWatchHistory).values(
                accesstoken=accesstoken,
                movie_id=str(movie.id),
                episode_id="",
                timestamp=int(time.time()),
                covers=covers,
                title=movie.title or "",
                tags=tags
            )

            # 冲突时更新字段
            update_stmt = stmt.on_duplicate_key_update(
                timestamp=int(time.time()),
                covers=covers,
                title=movie.title or "",
                tags=tags
            )

            await session.execute(update_stmt)
            await session.commit()
    except Exception as e:
        import logging
        logging.getLogger(__name__).error(f"保存观看历史失败: {e}")
