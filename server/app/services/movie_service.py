"""影片服务 - 实现影片查询业务逻辑"""
import json
import os
import random
import time
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta

from sqlalchemy import select, or_, func, and_, not_
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.entities import Movie, Episode, Actor, Rank, Watchlist
from app.cache import cache_get, cache_set, cache_key, cache_delete_pattern
from app.utils.logger import get_logger

logger = get_logger(__name__)


class MovieService:
    """影片服务类"""

    # 排序字段映射缓存
    ORDER_MAP = {
        "update_time": Movie.update_time.desc(),
        "score": Movie.score.desc(),
        "publish_year": Movie.publish_year.desc(),
        "recommend_num": Movie.recommend_num.desc(),
        "id": Movie.id.desc(),
    }

    # 列表展示所需的最小字段（减少数据传输）
    LIST_FIELDS = [
        Movie.id, Movie.category, Movie.title, Movie.score,
        Movie.covers, Movie.tags, Movie.season, Movie.publish_year,
        Movie.update_time, Movie.recommend_num, Movie.extra, Movie.cover_tag,
        Movie.series_title
    ]

    # 年份筛选条件缓存
    YEAR_RANGES = {
        "2010s": ("2010", "2019"),
        "2000s": ("2000", "2009"),
        "1990s": ("1990", "1999"),
        "other": (None, "1989"),
    }

    # 需要过滤的标签关键词（包含这些标签的影片将被排除）
    FILTER_TAGS = ["伦理", "伦理片", "色情", "情色", "色情片", "情色片"]

    @staticmethod
    def _escape_like_pattern(value: str) -> str:
        """转义 SQL LIKE 特殊字符，防止 LIKE 注入"""
        # 转义 % 和 _ 字符，使用 \ 作为转义符
        return value.replace('\\', '\\\\').replace('%', '\\%').replace('_', '\\_')

    @staticmethod
    def _build_tag_exclude_conditions():
        """构建标签排除条件（排除包含敏感标签的影片）"""
        exclude_conditions = []
        for tag in MovieService.FILTER_TAGS:
            escaped = MovieService._escape_like_pattern(tag)
            exclude_conditions.append(Movie.tags.like(f'%{escaped}%', escape='\\'))
        if exclude_conditions:
            return not_(or_(*exclude_conditions))
        return None

    @staticmethod
    def _has_tag_exclude_conditions():
        """检查是否有标签排除条件（用于 if 判断）"""
        return len(MovieService.FILTER_TAGS) > 0

    @staticmethod
    def _build_filter_conditions(filters: Optional[List[str]]) -> List:
        """构建筛选条件列表"""
        conditions = []
        if not filters:
            return conditions

        for f in filters:
            if f.startswith("type:"):
                type_value = f[5:]  # 移除"type:"前缀
                # 限制长度，防止超长输入
                if len(type_value) <= 50:
                    escaped = MovieService._escape_like_pattern(type_value)
                    conditions.append(Movie.tags.like(f"%{escaped}%", escape='\\'))
            elif f.startswith("year:"):
                year_value = f[5:]
                # 只允许数字年份，防止注入
                if year_value.isdigit() and len(year_value) == 4:
                    if year_value in MovieService.YEAR_RANGES:
                        start, end = MovieService.YEAR_RANGES[year_value]
                        if start:
                            conditions.append(Movie.publish_year >= start)
                        conditions.append(Movie.publish_year <= end)
                    else:
                        conditions.append(Movie.publish_year == year_value)
            elif f.startswith("region:"):
                region_value = f[7:]
                # 限制长度，防止超长输入
                if len(region_value) <= 50:
                    escaped = MovieService._escape_like_pattern(region_value)
                    conditions.append(Movie.tags.like(f"%{escaped}%", escape='\\'))
            elif f.startswith("status:"):
                # is_completed字段不存在，暂时跳过
                pass
            else:
                # 兼容旧格式，限制长度
                if len(f) <= 50:
                    escaped = MovieService._escape_like_pattern(f)
                    conditions.append(Movie.tags.like(f"%{escaped}%", escape='\\'))

        return conditions

    @staticmethod
    async def get_movies_by_page(
        session: AsyncSession,
        page: int = 1,
        category: int = 1,
        filters: Optional[List[str]] = None,
        order_by: str = "id",
        page_size: int = 30,
        use_cache: bool = True
    ) -> dict:
        """
        分页查询影片列表
        :param page: 页码，从1开始
        :param category: 分类ID
        :param filters: 标签筛选列表
        :param order_by: 排序字段
        :param page_size: 每页数量
        :param use_cache: 是否使用缓存
        """
        # 仅对第一页使用缓存，提高缓存命中率
        if use_cache and page == 1:
            cache_k = cache_key("movies", "page", category, order_by, page_size, *sorted(filters or []))
            cached = await cache_get(cache_k)
            if cached:
                return cached

        order_clause = MovieService.ORDER_MAP.get(order_by, Movie.id.desc())

        # 构建基础查询条件
        conditions = [Movie.category == category, Movie.category != 5]  # 排除伦理片
        filter_conditions = MovieService._build_filter_conditions(filters)
        if filter_conditions:
            conditions.extend(filter_conditions)

        # 添加标签关键词过滤（排除包含敏感标签的影片）
        if MovieService._has_tag_exclude_conditions():
            tag_exclude_conditions = MovieService._build_tag_exclude_conditions()
            conditions.append(tag_exclude_conditions)

        # 使用单个查询同时获取总数和数据（性能优化）
        base_query = select(Movie).where(and_(*conditions))

        # 获取总数 - 优化：使用更高效的count方式
        count_query = select(func.count(Movie.id)).where(and_(*conditions))
        total = await session.scalar(count_query)

        # 分页查询
        offset = (page - 1) * page_size
        query = base_query.order_by(order_clause).offset(offset).limit(page_size)

        result = await session.execute(query)
        movies = result.scalars().all()

        # 批量转换为字典
        data = {
            "page": page,
            "page_size": page_size,
            "total": total or 0,
            "list": [m.to_dict() for m in movies]
        }

        # 仅缓存第一页，避免缓存爆炸
        if use_cache and page == 1:
            await cache_set(cache_k, data, expire=600)  # 缓存10分钟

        return data

    @staticmethod
    async def get_movies_by_page_batch(
        session: AsyncSession,
        queries: List[Dict[str, Any]]
    ) -> List[dict]:
        """
        批量查询多个分类/条件的影片（用于首页并发查询）
        :param queries: 查询参数列表，每个包含page, category, filters, order_by, page_size
        """
        results = []
        for q in queries:
            result = await MovieService.get_movies_by_page(
                session=session,
                page=q.get("page", 1),
                category=q.get("category", 1),
                filters=q.get("filters"),
                order_by=q.get("order_by", "id"),
                page_size=q.get("page_size", 12),
                use_cache=True
            )
            results.append({
                "key": q.get("key", f"cat_{q.get('category', 1)}"),
                "data": result
            })
        return results

    @staticmethod
    async def get_movies_lite(
        session: AsyncSession,
        page: int = 1,
        category: int = 1,
        order_by: str = "recommend_num",
        page_size: int = 12,
        filters: Optional[List[str]] = None
    ) -> dict:
        """
        轻量级列表查询 - 只查列表展示必需字段（性能优化）
        用于首页、分类列表等不需要完整数据的场景
        """
        # 构建缓存key（只缓存第一页，避免缓存爆炸）
        filter_key = ",".join(sorted(filters or []))
        cache_k = cache_key("movies", "lite", category, order_by, page_size, filter_key, page)
        logger.info(f"[DEBUG] page={page}, cache_key={cache_k}")
        cached = await cache_get(cache_k)
        if cached:
            logger.info(f"[DEBUG] Cache hit for page={page}")
            return cached
        logger.info(f"[DEBUG] Cache miss for page={page}")

        order_clause = MovieService.ORDER_MAP.get(order_by, Movie.recommend_num.desc())

        # 构建查询条件
        conditions = [Movie.category == category, Movie.category != 5]  # 排除伦理片
        filter_conditions = MovieService._build_filter_conditions(filters)
        if filter_conditions:
            conditions.extend(filter_conditions)

        # 添加标签关键词过滤（排除包含敏感标签的影片）
        if MovieService._has_tag_exclude_conditions():
            tag_exclude_conditions = MovieService._build_tag_exclude_conditions()
            conditions.append(tag_exclude_conditions)

        # 获取总数（必需，分页需要）
        count_query = select(func.count(Movie.id)).where(and_(*conditions))
        total = await session.scalar(count_query)

        # 只查询必需字段（大幅减少数据传输）
        query = (
            select(*MovieService.LIST_FIELDS)
            .where(and_(*conditions))
            .order_by(order_clause)
            .offset((page - 1) * page_size)
            .limit(page_size)
        )

        result = await session.execute(query)
        rows = result.all()

        # 轻量级转换（不包含大字段解析）
        movies = []
        for row in rows:
            movie_dict = {
                "id": str(row.id),
                "category": row.category,
                "title": row.title or "",
                "score": row.score or 0.0,
                "covers": MovieService._parse_json_field(row.covers),
                "tags": MovieService._parse_json_field(row.tags),
                "season": row.season or 0,
                "publish_year": row.publish_year or "",
                "update_time": row.update_time or 0.0,
                "recommend_num": row.recommend_num or 0,
                "extra": MovieService._parse_json_field(row.extra),
                "cover_tag": row.cover_tag or "",
                "episode_sources": []
            }
            movies.append(movie_dict)

        data = {
            "page": page,
            "page_size": page_size,
            "total": total or 0,
            "list": movies
        }
        await cache_set(cache_k, data, expire=300)  # 缓存5分钟
        return data

    @staticmethod
    async def get_movies_for_banner(
        session: AsyncSession,
        category: int = 1,
        page_size: int = 5
    ) -> List[dict]:
        """
        获取Banner用的影片数据 - 包含完整字段（导演、演员、简介）
        """
        cache_k = cache_key("movies", "banner", category, page_size)
        cached = await cache_get(cache_k)
        if cached:
            return cached

        # 查询完整字段（包含directors, actors, contents等大字段）
        query = (
            select(Movie)
            .where(Movie.category == category)
            .order_by(Movie.update_time.desc())
            .limit(page_size)
        )

        result = await session.execute(query)
        movies = result.scalars().all()

        # 转换为包含完整字段的字典
        data = []
        for movie in movies:
            movie_dict = {
                "id": str(movie.id),
                "category": movie.category,
                "title": movie.title or "",
                "score": movie.score or 0.0,
                "covers": MovieService._parse_json_field(movie.covers),
                "cover": movie.covers.split(',')[0] if movie.covers else "",  # 首图
                "tags": MovieService._parse_json_field(movie.tags),
                "season": movie.season or 0,
                "publish_year": movie.publish_year or "",
                "update_time": movie.update_time or 0.0,
                "recommend_num": movie.recommend_num or 0,
                "extra": MovieService._parse_json_field(movie.extra),
                # Banner需要的完整字段
                "other_titles": MovieService._parse_json_field(movie.other_titles),
                "directors": MovieService._parse_json_field(movie.directors),
                "actors": MovieService._parse_json_field(movie.actors),
                "contents": movie.contents or "",
                "episode_sources": []
            }
            data.append(movie_dict)

        await cache_set(cache_k, data, expire=300)  # 缓存5分钟
        return data

    @staticmethod
    def _parse_json_field(field_value):
        """解析JSON字段（静态方法供轻量查询使用）"""
        if not field_value:
            return []
        if isinstance(field_value, str):
            try:
                return json.loads(field_value)
            except:
                return []
        return field_value

    @staticmethod
    async def get_home_page_data_by_type(
        session: AsyncSession,
        data_type: int
    ) -> List[str]:
        """
        从首页配置表获取指定类型的影片ID列表
        :param data_type: 1=banner, 2=最新上线, 3=热门电影, 4=热播电视剧, 5=热门综艺, 6=动漫推荐
        :return: 影片ID字符串列表
        """
        from app.models.entities import HomePageData

        query = select(HomePageData).where(HomePageData.type == data_type)
        result = await session.execute(query)
        home_data = result.scalar_one_or_none()

        if not home_data or not home_data.movie_ids:
            return []

        # 解析JSON格式的ID列表
        try:
            ids = json.loads(home_data.movie_ids)
            return [str(i) for i in ids if i]
        except (json.JSONDecodeError, TypeError):
            return []

    @staticmethod
    async def get_banner_ids_from_auto_index(
        session: AsyncSession
    ) -> List[str]:
        """
        从auto_index表获取banner影片ID列表（按sort_order排序）
        :return: 按sort_order升序排序的影片ID字符串列表
        """
        from app.models.entities import AutoIndex

        # 查询所有banner类型的记录，按sort_order升序排序
        query = (
            select(AutoIndex)
            .where(AutoIndex.item_type == "banner")
            .order_by(AutoIndex.sort_order.asc())
        )
        result = await session.execute(query)
        banner_items = result.scalars().all()

        if not banner_items:
            return []

        # 从data_json中解析intent_id
        movie_ids = []
        for item in banner_items:
            if item.data_json:
                try:
                    data = json.loads(item.data_json)
                    intent_id = data.get("intent_id")
                    if intent_id:
                        movie_ids.append(str(intent_id))
                except (json.JSONDecodeError, TypeError):
                    continue

        return movie_ids

    @staticmethod
    async def get_movies_by_ids_with_full_fields(
        session: AsyncSession,
        movie_ids: List[str]
    ) -> List[dict]:
        """
        根据ID列表获取影片完整字段（用于Banner）
        """
        if not movie_ids:
            return []

        # 去重并保持顺序
        seen = set()
        unique_ids = []
        for mid in movie_ids:
            if mid not in seen and mid.isdigit():
                seen.add(mid)
                unique_ids.append(int(mid))

        if not unique_ids:
            return []

        # 查询完整字段
        query = select(Movie).where(Movie.id.in_(unique_ids))
        result = await session.execute(query)
        movies = result.scalars().all()

        # 构建ID到影片的映射
        movie_map = {}
        for movie in movies:
            movie_dict = {
                "id": str(movie.id),
                "category": movie.category,
                "title": movie.title or "",
                "score": movie.score or 0.0,
                "covers": MovieService._parse_json_field(movie.covers),
                "cover": movie.covers.split(',')[0] if movie.covers else "",
                "tags": MovieService._parse_json_field(movie.tags),
                "season": movie.season or 0,
                "publish_year": movie.publish_year or "",
                "update_time": movie.update_time or 0.0,
                "recommend_num": movie.recommend_num or 0,
                "extra": MovieService._parse_json_field(movie.extra),
                "other_titles": MovieService._parse_json_field(movie.other_titles),
                "directors": MovieService._parse_json_field(movie.directors),
                "actors": MovieService._parse_json_field(movie.actors),
                "contents": movie.contents or "",
                "oneshot_desc": movie.oneshot_desc or "",
                "episode_sources": []
            }
            movie_map[str(movie.id)] = movie_dict

        # 按传入顺序返回
        return [movie_map[str(mid)] for mid in unique_ids if str(mid) in movie_map]

    @staticmethod
    async def get_movies_by_ids_lite(
        session: AsyncSession,
        movie_ids: List[str]
    ) -> List[dict]:
        """
        根据ID列表获取影片轻量级字段（用于列表展示）
        """
        if not movie_ids:
            return []

        # 去重并保持顺序
        seen = set()
        unique_ids = []
        for mid in movie_ids:
            if mid not in seen and mid.isdigit():
                seen.add(mid)
                unique_ids.append(int(mid))

        if not unique_ids:
            return []

        # 查询轻量级字段
        query = select(*MovieService.LIST_FIELDS).where(Movie.id.in_(unique_ids))
        result = await session.execute(query)
        rows = result.all()

        # 构建ID到影片的映射
        movie_map = {}
        for row in rows:
            movie_dict = {
                "id": str(row.id),
                "category": row.category,
                "title": row.title or "",
                "score": row.score or 0.0,
                "covers": MovieService._parse_json_field(row.covers),
                "tags": MovieService._parse_json_field(row.tags),
                "season": row.season or 0,
                "publish_year": row.publish_year or "",
                "update_time": row.update_time or 0.0,
                "recommend_num": row.recommend_num or 0,
                "extra": MovieService._parse_json_field(row.extra),
                "cover_tag": row.cover_tag or "",
                "episode_sources": []
            }
            movie_map[str(row.id)] = movie_dict

        # 按传入顺序返回
        return [movie_map[str(mid)] for mid in unique_ids if str(mid) in movie_map]

    @staticmethod
    async def get_today_movies(
        session: AsyncSession,
        page: int = 1,
        page_size: int = 30,
        categories: Optional[List[int]] = None
    ) -> dict:
        """
        获取今日更新的影片列表 - 轻量级查询优化（无缓存，实时数据）
        """
        # 计算今天的时间戳范围（使用北京时间）
        from datetime import timezone
        beijing_tz = timezone(timedelta(hours=8))
        now = datetime.now(beijing_tz)
        today_start = datetime(now.year, now.month, now.day, tzinfo=beijing_tz)
        today_end = today_start + timedelta(days=1)

        start_timestamp = today_start.timestamp()
        end_timestamp = today_end.timestamp()

        # 构建查询条件
        # 排除 update_time 为 0 或 null 的无效数据
        conditions = [
            Movie.update_time >= start_timestamp,
            Movie.update_time < end_timestamp,
            Movie.update_time > 0,
            Movie.category != 5  # 排除伦理片
        ]

        if categories:
            conditions.append(Movie.category.in_(categories))

        # 添加标签关键词过滤（排除包含敏感标签的影片）
        if MovieService._has_tag_exclude_conditions():
            tag_exclude_conditions = MovieService._build_tag_exclude_conditions()
            conditions.append(tag_exclude_conditions)

        # 获取总数
        count_query = select(func.count(Movie.id)).where(and_(*conditions))
        total = await session.scalar(count_query)

        # 轻量级字段查询（只查列表必需字段）
        # 按更新时间从新到旧排序（最新的排在最前面）
        offset = (page - 1) * page_size
        query = (
            select(*MovieService.LIST_FIELDS)
            .where(and_(*conditions))
            .order_by(Movie.update_time.desc())
            .offset(offset)
            .limit(page_size)
        )

        result = await session.execute(query)
        rows = result.all()

        # 轻量级转换
        movies = []
        for row in rows:
            movie_dict = {
                "id": str(row.id),
                "category": row.category,
                "title": row.title or "",
                "score": row.score or 0.0,
                "covers": MovieService._parse_json_field(row.covers),
                "tags": MovieService._parse_json_field(row.tags),
                "season": row.season or 0,
                "publish_year": row.publish_year or "",
                "update_time": row.update_time or 0.0,
                "recommend_num": row.recommend_num or 0,
                "extra": MovieService._parse_json_field(row.extra),
                "cover_tag": row.cover_tag or "",
                "episode_sources": []
            }
            movies.append(movie_dict)

        return {
            "page": page,
            "page_size": page_size,
            "total": total or 0,
            "list": movies
        }

    @staticmethod
    async def search_movies(
        session: AsyncSession,
        keywords: List[str],
        categories: Optional[List[int]] = None,
        limit: int = 100,
        use_cache: bool = True
    ) -> List[dict]:
        """
        搜索影片 - 轻量级查询优化
        """
        if not keywords:
            return []

        # 优化：限制最大搜索词数量
        keywords = keywords[:5]

        cache_k = cache_key("movies", "search", *sorted(keywords), *sorted(categories or []))
        if use_cache:
            cached = await cache_get(cache_k)
            if cached:
                return cached

        # 构建查询条件（转义特殊字符防止 LIKE 注入）
        keyword_conditions = []
        for kw in keywords:
            # 限制单个关键词长度，并转义特殊字符
            if len(kw) <= 100:
                escaped_kw = MovieService._escape_like_pattern(kw)
                keyword_conditions.append(Movie.search_keys.like(f"%{escaped_kw}%", escape='\\'))

        conditions = [or_(*keyword_conditions)]

        # 排除伦理片分类
        conditions.append(Movie.category != 5)

        # 添加标签关键词过滤（排除包含敏感标签的影片）
        if MovieService._has_tag_exclude_conditions():
            tag_exclude_conditions = MovieService._build_tag_exclude_conditions()
            conditions.append(tag_exclude_conditions)

        if categories:
            conditions.append(Movie.category.in_(categories))

        # 轻量级字段查询
        query = (
            select(*MovieService.LIST_FIELDS)
            .where(and_(*conditions))
            .order_by(Movie.recommend_num.desc())
            .limit(limit)
        )

        result = await session.execute(query)
        rows = result.all()

        # 如果没有结果，尝试搜索title字段（转义特殊字符防止 LIKE 注入）
        if not rows and len(keywords) <= 2:
            title_conditions = []
            for kw in keywords:
                if len(kw) <= 100:
                    escaped_kw = MovieService._escape_like_pattern(kw)
                    title_conditions.append(Movie.title.like(f"%{escaped_kw}%", escape='\\'))
            if title_conditions:
                # 构建 title 查询的条件（同样需要排除 category=5 和敏感标签）
                title_where_conditions = [or_(*title_conditions), Movie.category != 5]

                # 添加标签关键词过滤
                if MovieService._has_tag_exclude_conditions():
                    tag_exclude_conditions = MovieService._build_tag_exclude_conditions()
                    title_where_conditions.append(tag_exclude_conditions)

                query = (
                    select(*MovieService.LIST_FIELDS)
                    .where(and_(*title_where_conditions))
                    .limit(limit)
                )
                result = await session.execute(query)
                rows = result.all()

        # 轻量级转换
        movies = []
        for row in rows:
            movie_dict = {
                "id": str(row.id),
                "category": row.category,
                "title": row.title or "",
                "score": row.score or 0.0,
                "covers": MovieService._parse_json_field(row.covers),
                "tags": MovieService._parse_json_field(row.tags),
                "season": row.season or 0,
                "publish_year": row.publish_year or "",
                "update_time": row.update_time or 0.0,
                "recommend_num": row.recommend_num or 0,
                "extra": MovieService._parse_json_field(row.extra),
                "cover_tag": row.cover_tag or "",
                "series_title": row.series_title or "",
                "episode_sources": []
            }
            movies.append(movie_dict)

        if use_cache:
            await cache_set(cache_k, movies, expire=180)  # 缓存3分钟

        return movies

    @staticmethod
    async def get_movie_by_id(
        session: AsyncSession,
        movie_id: str,
        contain_episodes: bool = True
    ) -> Optional[dict]:
        """
        根据ID获取影片详情
        """
        try:
            movie_id_int = int(movie_id)
        except (ValueError, TypeError):
            return None

        cache_k = cache_key("movie", movie_id_int, contain_episodes)
        cached = await cache_get(cache_k)
        if cached:
            return cached

        # 优化：根据是否需要剧集决定查询方式
        if contain_episodes:
            # 使用joinedload或selectinload优化关联查询
            from sqlalchemy.orm import selectinload
            query = select(Movie).options(selectinload(Movie.episodes)).where(Movie.id == movie_id_int)
        else:
            query = select(Movie).where(Movie.id == movie_id_int)

        result = await session.execute(query)
        movie = result.scalar_one_or_none()

        if not movie:
            return None

        data = movie.to_dict(contain_episodes=contain_episodes)
        expire = 3600 if contain_episodes else 600  # 有剧集缓存1小时，否则10分钟
        await cache_set(cache_k, data, expire=expire)
        return data

    @staticmethod
    async def get_movies_by_ids_batch(
        session: AsyncSession,
        movie_ids: List[str],
        contain_episodes: bool = False
    ) -> Dict[str, dict]:
        """
        批量根据ID列表获取影片 - 返回ID到影片的映射（轻量级查询）
        """
        if not movie_ids:
            return {}

        # 去重并转换ID
        unique_ids = list(set(movie_ids))
        try:
            movie_ids_int = [int(mid) for mid in unique_ids if mid.isdigit()]
        except (ValueError, TypeError):
            return {}

        if not movie_ids_int:
            return {}

        # 轻量级字段查询
        query = select(*MovieService.LIST_FIELDS).where(Movie.id.in_(movie_ids_int))
        result = await session.execute(query)
        rows = result.all()

        # 轻量级转换
        movie_map = {}
        for row in rows:
            movie_dict = {
                "id": str(row.id),
                "category": row.category,
                "title": row.title or "",
                "score": row.score or 0.0,
                "covers": MovieService._parse_json_field(row.covers),
                "tags": MovieService._parse_json_field(row.tags),
                "season": row.season or 0,
                "publish_year": row.publish_year or "",
                "update_time": row.update_time or 0.0,
                "recommend_num": row.recommend_num or 0,
                "extra": MovieService._parse_json_field(row.extra),
                "cover_tag": row.cover_tag or "",
                "episode_sources": []
            }
            movie_map[str(row.id)] = movie_dict

        return movie_map

    @staticmethod
    async def get_movies_by_ids(
        session: AsyncSession,
        movie_ids: List[str],
        contain_episodes: bool = False
    ) -> List[dict]:
        """根据ID列表获取影片（保持原有接口兼容性）"""
        movie_map = await MovieService.get_movies_by_ids_batch(session, movie_ids, contain_episodes)
        # 按传入顺序返回
        return [movie_map.get(mid) for mid in movie_ids if mid in movie_map and movie_map.get(mid)]

    @staticmethod
    async def get_recommend_movies(
        session: AsyncSession,
        title: str,
        category: Optional[int] = None,
        search_keywords: Optional[List[str]] = None,
        limit: int = 24
    ) -> List[dict]:
        """
        获取推荐影片 - 优化版本
        """
        keywords = list(search_keywords or [])[:3]  # 限制关键词数量
        keywords.append(title)

        categories = [category] if category else [1, 2, 3, 4, 6]

        # 搜索相关影片
        movies = await MovieService.search_movies(session, keywords, categories, limit=limit + 10)

        # 排除当前影片并限制数量
        results = [m for m in movies if m.get("title") != title][:limit]

        # 如果数量不足，从同分类的最新影片中补充
        if len(results) < limit:
            existing_ids = {m.get("id") for m in results}
            more = await MovieService.get_movies_by_page(
                session, page=1, category=category or 1, order_by="update_time", page_size=limit * 2
            )
            for m in more.get("list", []):
                if m.get("title") != title and m.get("id") not in existing_ids:
                    results.append(m)
                    existing_ids.add(m.get("id"))
                if len(results) >= limit:
                    break

        return results

    @staticmethod
    async def get_movies_by_series(
        session: AsyncSession,
        series_title: str
    ) -> List[dict]:
        """根据系列名获取影片"""
        if not series_title:
            return []

        cache_k = cache_key("movies", "series", series_title)
        cached = await cache_get(cache_k)
        if cached:
            return cached

        query = select(Movie).where(Movie.series_title == series_title).order_by(Movie.publish_year.desc())
        result = await session.execute(query)
        movies = result.scalars().all()

        data = [m.to_dict() for m in movies]
        await cache_set(cache_k, data, expire=1800)  # 缓存30分钟
        return data

    @staticmethod
    async def preload_movie_cache(
        session: AsyncSession,
        movie_ids: List[str]
    ) -> None:
        """预加载影片缓存"""
        for mid in movie_ids:
            await MovieService.get_movie_by_id(session, mid, contain_episodes=False)

    @staticmethod
    async def update_movie_count(
        session: AsyncSession,
        movie_id: str,
        recommend: Optional[bool] = None
    ) -> bool:
        """
        更新影片计数
        :param movie_id: 影片ID
        :param recommend: True=推荐+1, False=不推荐+1, None=观看+1
        :return: 是否更新成功
        """
        try:
            movie_id_int = int(movie_id)
        except (ValueError, TypeError):
            return False

        # 获取影片当前extra数据
        query = select(Movie).where(Movie.id == movie_id_int)
        result = await session.execute(query)
        movie = result.scalar_one_or_none()

        if not movie:
            return False

        # 解析extra字段
        extra = {}
        if movie.extra:
            try:
                extra = json.loads(movie.extra) if isinstance(movie.extra, str) else movie.extra
            except (json.JSONDecodeError, TypeError):
                extra = {}

        # 确保字段存在
        if "watch_count" not in extra:
            extra["watch_count"] = 0
        if "recommend_count" not in extra:
            extra["recommend_count"] = 0
        if "unrecommend_count" not in extra:
            extra["unrecommend_count"] = 0

        # 根据参数更新对应计数
        if recommend is None:
            # 不传参数，观看数+1
            extra["watch_count"] = int(extra["watch_count"]) + 1
        elif recommend is True:
            # 推荐+1
            extra["recommend_count"] = int(extra["recommend_count"]) + 1
        else:
            # 不推荐+1
            extra["unrecommend_count"] = int(extra["unrecommend_count"]) + 1

        # 更新数据库
        movie.extra = json.dumps(extra, ensure_ascii=False)
        await session.commit()

        # 清除相关缓存
        cache_k = cache_key("movie", movie_id_int, True)
        await cache_delete_pattern(cache_k)
        cache_k2 = cache_key("movie", movie_id_int, False)
        await cache_delete_pattern(cache_k2)

        return True


class ActorService:
    """演员服务类"""

    @staticmethod
    async def get_actors_by_names(
        session: AsyncSession,
        names: List[str]
    ) -> List[dict]:
        """根据名称列表获取演员信息"""
        if not names:
            return []

        # 限制查询数量
        names = names[:20]

        query = select(Actor).where(Actor.name.in_(names))
        result = await session.execute(query)
        actors = result.scalars().all()

        # 构建名称到演员的映射
        actor_map = {a.name: a for a in actors}

        # 按传入顺序返回
        return [{
            "id": actor_map[name].id,
            "name": actor_map[name].name,
            "eng_name": actor_map[name].eng_name,
            "avatar": actor_map[name].avatar,
            "sex": actor_map[name].sex,
            "birth": actor_map[name].birth,
            "address": actor_map[name].address,
            "profassion": actor_map[name].profassion,
        } for name in names if name in actor_map]


class RankService:
    """排行榜服务类"""

    @staticmethod
    async def get_ranks_by_ids(
        session: AsyncSession,
        rank_ids: List[str],
        use_cache: bool = True
    ) -> List[dict]:
        """
        根据ID列表获取排行榜 - 优化版本（解决N+1问题）
        """
        if not rank_ids:
            return []

        # 构建缓存key
        cache_k = cache_key("rank", *sorted(rank_ids))

        # 尝试从缓存获取
        if use_cache:
            cached = await cache_get(cache_k)
            if cached:
                return cached

        # 1. 批量获取排行榜数据
        query = select(Rank).where(Rank.id.in_(rank_ids))
        result = await session.execute(query)
        ranks = result.scalars().all()

        if not ranks:
            return []

        # 构建ID到排行榜的映射
        rank_map = {str(r.id): r for r in ranks}

        # 2. 收集所有需要查询的影片ID
        all_movie_ids = set()
        rank_movie_ids = {}  # rank_id -> {position: movie_id}

        for rank in ranks:
            if rank.movies:
                try:
                    movies_dict = json.loads(rank.movies) if isinstance(rank.movies, str) else rank.movies
                    if isinstance(movies_dict, dict):
                        # 只取前10个（按排名位置排序后截取）
                        sorted_items = sorted(
                            movies_dict.items(),
                            key=lambda x: int(x[0]) if str(x[0]).isdigit() else 0
                        )[:10]
                        filtered_dict = dict(sorted_items)
                        rank_movie_ids[str(rank.id)] = filtered_dict
                        all_movie_ids.update(str(v) for v in filtered_dict.values() if v)
                except (json.JSONDecodeError, TypeError):
                    continue

        # 3. 批量获取所有影片数据（解决N+1问题）
        movie_map = {}
        if all_movie_ids:
            movie_map = await MovieService.get_movies_by_ids_batch(
                session, list(all_movie_ids), contain_episodes=False
            )

        # 4. 组装结果
        results = []
        for rid in rank_ids:
            rank = rank_map.get(str(rid))
            if not rank:
                continue

            movies_data = rank_movie_ids.get(str(rid), {})
            movies = []

            for position, movie_id in movies_data.items():
                movie_data = movie_map.get(str(movie_id))
                if movie_data:
                    movie_data = movie_data.copy()
                    movie_data["rank_position"] = int(position) if position.isdigit() else 0
                    movies.append(movie_data)

            # 按排名位置排序
            movies.sort(key=lambda x: x.get("rank_position", 0))

            results.append({
                "id": rank.id,
                "name": rank.name,
                "description": rank.description,
                "cover": rank.cover,
                "movies": movies
            })

        # 缓存结果（5分钟）
        if use_cache:
            await cache_set(cache_k, results, expire=300)

        return results

    @staticmethod
    async def get_all_ranks(
        session: AsyncSession,
        use_cache: bool = True
    ) -> List[dict]:
        """
        获取所有排行榜数据
        """
        cache_k = cache_key("rank", "all")

        # 尝试从缓存获取
        if use_cache:
            cached = await cache_get(cache_k)
            if cached:
                return cached

        # 1. 获取所有排行榜数据
        query = select(Rank).order_by(Rank.id.asc())
        result = await session.execute(query)
        ranks = result.scalars().all()

        if not ranks:
            return []

        # 2. 收集所有需要查询的影片ID
        all_movie_ids = set()
        rank_movie_ids = {}  # rank_id -> {position: movie_id}

        for rank in ranks:
            if rank.movies:
                try:
                    movies_dict = json.loads(rank.movies) if isinstance(rank.movies, str) else rank.movies
                    if isinstance(movies_dict, dict):
                        # 取全部数据
                        sorted_items = sorted(
                            movies_dict.items(),
                            key=lambda x: int(x[0]) if str(x[0]).isdigit() else 0
                        )
                        filtered_dict = dict(sorted_items)
                        rank_movie_ids[str(rank.id)] = filtered_dict
                        all_movie_ids.update(str(v) for v in filtered_dict.values() if v)
                except (json.JSONDecodeError, TypeError):
                    continue

        # 3. 批量获取所有影片数据
        movie_map = {}
        if all_movie_ids:
            movie_map = await MovieService.get_movies_by_ids_batch(
                session, list(all_movie_ids), contain_episodes=False
            )

        # 4. 组装结果
        results = []
        for rank in ranks:
            movies_data = rank_movie_ids.get(str(rank.id), {})
            movies = []

            for position, movie_id in movies_data.items():
                movie_data = movie_map.get(str(movie_id))
                if movie_data:
                    movie_data = movie_data.copy()
                    movie_data["rank_position"] = int(position) if position.isdigit() else 0
                    movies.append(movie_data)

            # 按排名位置排序
            movies.sort(key=lambda x: x.get("rank_position", 0))

            results.append({
                "id": rank.id,
                "name": rank.name,
                "description": rank.description,
                "cover": rank.cover,
                "movies": movies
            })

        # 缓存结果（5分钟）
        if use_cache:
            await cache_set(cache_k, results, expire=300)

        return results


class WatchlistService:
    """片单服务类"""

    @staticmethod
    async def get_watchlists_by_ids(
        session: AsyncSession,
        watchlist_ids: List[str],
        use_cache: bool = True
    ) -> List[dict]:
        """
        根据ID列表获取片单 - 优化版本（解决N+1问题）
        """
        if not watchlist_ids:
            return []

        # 构建缓存key
        cache_k = cache_key("watchlist", *sorted(watchlist_ids))

        # 尝试从缓存获取
        if use_cache:
            cached = await cache_get(cache_k)
            if cached:
                return cached

        # 1. 批量获取片单数据
        query = select(Watchlist).where(Watchlist.id.in_(watchlist_ids))
        result = await session.execute(query)
        watchlists = result.scalars().all()

        if not watchlists:
            return []

        # 构建ID到片单的映射
        wl_map = {str(w.id): w for w in watchlists}

        # 2. 收集所有需要查询的影片ID
        all_movie_ids = set()
        wl_movie_ids = {}  # wl_id -> [movie_id]

        for wl in watchlists:
            if wl.movies:
                try:
                    movies_list = json.loads(wl.movies) if isinstance(wl.movies, str) else wl.movies
                    if isinstance(movies_list, list):
                        wl_movie_ids[str(wl.id)] = [str(m) for m in movies_list if m]
                        all_movie_ids.update(str(m) for m in movies_list if m)
                except (json.JSONDecodeError, TypeError):
                    continue

        # 3. 批量获取所有影片数据（解决N+1问题）
        movie_map = {}
        if all_movie_ids:
            movie_map = await MovieService.get_movies_by_ids_batch(
                session, list(all_movie_ids), contain_episodes=False
            )

        # 4. 组装结果
        results = []
        for wid in watchlist_ids:
            wl = wl_map.get(str(wid))
            if not wl:
                continue

            movie_ids = wl_movie_ids.get(str(wid), [])
            movies = [movie_map.get(mid) for mid in movie_ids if mid in movie_map and movie_map.get(mid)]

            results.append({
                "id": wl.id,
                "name": wl.name,
                "description": wl.description,
                "cover": wl.cover,
                "movies": movies
            })

        # 缓存结果（5分钟）
        if use_cache:
            await cache_set(cache_k, results, expire=300)

        return results

    @staticmethod
    async def get_all_watchlists_paginated(
        session: AsyncSession,
        page: int = 1,
        page_size: int = 6,
        use_cache: bool = True
    ) -> dict:
        """
        分页获取所有片单数据
        :param page: 页码，从1开始
        :param page_size: 每页数量
        :param use_cache: 是否使用缓存
        :return: 包含list、total、page、page_size的字典
        """
        from math import ceil

        # 构建缓存key
        cache_k = cache_key("watchlist", "all", page, page_size)

        # 尝试从缓存获取
        if use_cache:
            cached = await cache_get(cache_k)
            if cached:
                return cached

        # 1. 获取片单总数
        count_query = select(func.count(Watchlist.id))
        total = await session.scalar(count_query) or 0

        # 2. 分页获取片单数据
        offset = (page - 1) * page_size
        query = (
            select(Watchlist)
            .order_by(Watchlist.id.desc())
            .offset(offset)
            .limit(page_size)
        )
        result = await session.execute(query)
        watchlists = result.scalars().all()

        if not watchlists:
            return {
                "list": [],
                "total": total,
                "page": page,
                "page_size": page_size,
                "total_pages": ceil(total / page_size) if page_size > 0 else 0
            }

        # 3. 收集所有需要查询的影片ID
        all_movie_ids = set()
        wl_movie_ids = {}  # wl_id -> [movie_id]

        for wl in watchlists:
            if wl.movies:
                try:
                    movies_list = json.loads(wl.movies) if isinstance(wl.movies, str) else wl.movies
                    if isinstance(movies_list, list):
                        # 取全部影片
                        full_list = [str(m) for m in movies_list if m]
                        wl_movie_ids[str(wl.id)] = full_list
                        all_movie_ids.update(full_list)
                except (json.JSONDecodeError, TypeError):
                    continue

        # 4. 批量获取影片数据（轻量级字段）
        movie_map = {}
        if all_movie_ids:
            movie_map = await MovieService.get_movies_by_ids_batch(
                session, list(all_movie_ids), contain_episodes=False
            )

        # 5. 组装结果
        results = []
        for wl in watchlists:
            movie_ids = wl_movie_ids.get(str(wl.id), [])
            movies = [movie_map.get(mid) for mid in movie_ids if mid in movie_map and movie_map.get(mid)]

            results.append({
                "id": wl.id,
                "name": wl.name,
                "description": wl.description,
                "cover": wl.cover,
                "movies": movies
            })

        result = {
            "list": results,
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": ceil(total / page_size) if page_size > 0 else 0
        }

        # 缓存结果（5分钟）
        if use_cache:
            await cache_set(cache_k, result, expire=300)

        return result
