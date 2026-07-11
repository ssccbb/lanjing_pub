"""页面聚合接口 - 为前端SSR提供数据"""
import asyncio
from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import AsyncSessionLocal, get_db
from app.services.movie_service import MovieService, RankService, WatchlistService
from app.cache import cache_get, cache_set, cache_key
from app.utils.response import Response

router = APIRouter()


async def _fetch_category_movies(cat_id: int, cat_name: str) -> tuple:
    """获取单个分类的电影数据（用于并发）"""
    async with AsyncSessionLocal() as session:
        try:
            result = await MovieService.get_movies_by_page(
                session=session, page=1, category=cat_id, order_by="recommend_num"
            )
            return (cat_name, result.get("list", [])[:12])
        except Exception:
            return (cat_name, [])
        finally:
            await session.close()


async def _fetch_newest_movies() -> dict:
    """获取最新影片（用于并发）"""
    async with AsyncSessionLocal() as session:
        try:
            return await MovieService.get_movies_by_page(
                session=session, page=1, category=1, order_by="update_time"
            )
        except Exception:
            return {"list": []}
        finally:
            await session.close()


@router.get("")
async def get_home_data():
    """
    获取首页数据 - 从home_page_data表获取配置
    数据库type定义: 1=banner, 2=最新上线, 3=热门电影, 4=热播电视剧, 5=热门综艺, 6=动漫推荐
    """
    # 检查缓存
    cache_k = cache_key("page", "home")
    cached = await cache_get(cache_k)
    if cached:
        return Response.success(cached)

    # 1. 获取Banner数据（从home_page_data表type=1获取，按数据库顺序）
    async with AsyncSessionLocal() as session:
        try:
            banner_ids = await MovieService.get_home_page_data_by_type(session, data_type=1)
            banners = await MovieService.get_movies_by_ids_with_full_fields(session, banner_ids)
        finally:
            await session.close()

    # 2. 获取最新上线（轻量级字段）- type=2
    async with AsyncSessionLocal() as session:
        try:
            newest_ids = await MovieService.get_home_page_data_by_type(session, data_type=2)
            newest = await MovieService.get_movies_by_ids_lite(session, newest_ids[:9])
        finally:
            await session.close()

    # 3. 各分类推荐（轻量级字段）
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

    # 组装响应数据（去掉recommends，只保留banners/newest/categories）
    data = {
        "banners": banners,      # 完整字段（导演、演员、简介）
        "newest": newest,        # 轻量级字段
        "categories": categories # 轻量级字段
    }

    # 缓存结果（5分钟）
    await cache_set(cache_k, data, expire=300)

    return Response.success(data)


@router.get("/list/{category_id}")
async def get_category_data(
    category_id: int,
    page: int = Query(1, ge=1),
    page_size: int = Query(30, ge=1, le=100),
    order_by: str = Query("id", enum=["id", "update_time", "score", "publish_year", "recommend_num"]),
    type: Optional[str] = Query(None, description="类型筛选"),
    year: Optional[str] = Query(None, description="年份筛选"),
    region: Optional[str] = Query(None, description="地区筛选"),
    status: Optional[str] = Query(None, description="状态筛选"),
    db: AsyncSession = Depends(get_db)
):
    """
    获取分类页数据 - 优化版本（轻量级字段查询）
    :param category_id: 分类ID (1=电影, 2=电视剧, 3=综艺, 4=动漫, 6=短剧)
    :param page: 页码
    :param page_size: 每页数量
    :param order_by: 排序方式
    :param type: 类型筛选
    :param year: 年份筛选
    :param region: 地区筛选
    :param status: 状态筛选
    """
    # 限制页大小
    page_size = min(page_size, 100)

    # 构建筛选条件
    filters = []
    if type and type != 'all':
        filters.append(f"type:{type}")
    if year and year != 'all':
        filters.append(f"year:{year}")
    if region and region != 'all':
        filters.append(f"region:{region}")
    if status and status != 'all':
        filters.append(f"status:{status}")

    # 使用轻量级查询（只查列表必需字段）
    result = await MovieService.get_movies_lite(
        session=db,
        page=page,
        category=category_id,
        order_by=order_by,
        page_size=page_size,
        filters=filters if filters else None
    )

    return Response.success(result)


@router.get("/detail/{movie_id}")
async def get_movie_detail(
    movie_id: str,
    db: AsyncSession = Depends(get_db)
):
    """
    获取影片详情 - 优化版本（并发获取推荐）
    """
    import asyncio

    # 1. 先获取影片详情
    movie = await MovieService.get_movie_by_id(
        session=db,
        movie_id=movie_id,
        contain_episodes=True
    )

    if not movie:
        return Response.not_found("影片不存在")

    # 2. 并发获取相关推荐和系列影片
    async def fetch_recommends():
        return await MovieService.get_recommend_movies(
            session=db,
            title=movie.get("title"),
            category=movie.get("category"),
            search_keywords=movie.get("actors", [])[:3]
        )

    async def fetch_series():
        series_title = movie.get("series_title")
        if series_title:
            return await MovieService.get_movies_by_series(db, series_title)
        return []

    recommends, series_movies = await asyncio.gather(
        fetch_recommends(),
        fetch_series()
    )

    movie["recommends"] = recommends[:6]
    if series_movies and len(series_movies) > 1:
        movie["series_movies"] = series_movies

    return Response.success(movie)


@router.get("/rank/{rank_id}")
async def get_rank_by_id(
    rank_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    获取单个排行榜数据（带影片详细信息）
    :param rank_id: 排行榜ID，如 1=热搜榜, 2=热播榜
    """
    ranks = await RankService.get_ranks_by_ids(db, [str(rank_id)])
    if not ranks:
        return Response.not_found("排行榜不存在")
    return Response.success(ranks[0])


@router.get("/ranks")
async def get_ranks(
    ids: str = Query(..., description="排行榜ID列表，逗号分隔"),
    db: AsyncSession = Depends(get_db)
):
    """
    获取排行榜数据（批量）
    :param ids: 排行榜ID列表，如 "1,2,3"
    """
    rank_ids = [rid.strip() for rid in ids.split(",") if rid.strip()]
    ranks = await RankService.get_ranks_by_ids(db, rank_ids)
    return Response.success({"ranks": ranks})


@router.get("/ranks/all")
async def get_all_ranks(
    db: AsyncSession = Depends(get_db)
):
    """
    获取所有排行榜数据
    """
    ranks = await RankService.get_all_ranks(db)
    return Response.success({"ranks": ranks})


@router.get("/watchlists")
async def get_watchlists(
    ids: str = Query(..., description="片单ID列表，逗号分隔"),
    db: AsyncSession = Depends(get_db)
):
    """
    获取片单数据
    :param ids: 片单ID列表，如 "1,2,3"
    """
    watchlist_ids = [wid.strip() for wid in ids.split(",") if wid.strip()]
    watchlists = await WatchlistService.get_watchlists_by_ids(db, watchlist_ids)
    return Response.success({"watchlists": watchlists})


@router.get("/watchlists/all")
async def get_all_watchlists(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(6, ge=1, le=20, description="每页数量"),
    db: AsyncSession = Depends(get_db)
):
    """
    分页获取所有片单数据
    :param page: 页码，从1开始
    :param page_size: 每页数量，默认6，最大20
    """
    result = await WatchlistService.get_all_watchlists_paginated(db, page=page, page_size=page_size)
    return Response.success(result)


@router.get("/today")
async def get_today_movies(
    page: int = Query(1, ge=1),
    page_size: int = Query(30, ge=1, le=100),
    categories: Optional[str] = Query(None, description="分类ID列表，逗号分隔，如'1,2,3'"),
    db: AsyncSession = Depends(get_db)
):
    """
    获取今日更新的影片列表
    :param page: 页码
    :param page_size: 每页数量
    :param categories: 分类ID列表，逗号分隔，如'1,2,3'，为空则查询所有分类（除伦理片）
    """
    # 解析分类列表
    category_list = None
    if categories:
        try:
            category_list = [int(c.strip()) for c in categories.split(",") if c.strip()]
        except ValueError:
            category_list = None

    result = await MovieService.get_today_movies(
        session=db,
        page=page,
        page_size=page_size,
        categories=category_list
    )
    return Response.success(result)
