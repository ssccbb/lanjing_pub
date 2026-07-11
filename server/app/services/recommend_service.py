"""推荐算法服务 - 多维度热度分计算框架"""
import json
from datetime import datetime
from typing import List, Dict, Any, Optional, Set
from collections import defaultdict

from sqlalchemy import select, func, and_, not_, or_
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.entities import Movie
from app.models.search import UserSearch
from app.models.home_page_config import HomePageConfig
from app.utils.config_loader import load_algorithm_config
from app.utils.logger import get_logger

logger = get_logger(__name__)


class RecommendService:
    """推荐算法服务"""

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """初始化推荐服务

        Args:
            config: 算法配置，为None时自动加载
        """
        self.config = config or load_algorithm_config()
        self.algo_config = self.config.get("algorithm", {})
        self.exclusion_config = self.config.get("exclusions", {})
        self.weights = self.algo_config.get("weights", {})
        self.caps = self.algo_config.get("caps", {})
        self.freshness_config = self.algo_config.get("freshness", {})

    def _get_chart_bonus_score(self, movie_id: int, chart_ranks: Dict[int, Dict[str, int]]) -> float:
        """计算榜单排名加成分数

        Args:
            movie_id: 影片ID
            chart_ranks: 榜单排名数据 {movie_id: {chart_name: rank}}

        Returns:
            float: 榜单加成分数（0-100）
        """
        # 核心算法逻辑已隐藏, 可根据实际需求实现自定义的加成算法
        # your_algorithm_here
        return 0.0

    def calculate_heat_score(
        self,
        movie: Movie,
        search_count: int = 0,
        weight_adjust: float = 1.0,
        chart_ranks: Optional[Dict[int, Dict[str, int]]] = None
    ) -> float:
        """计算影片热度分

        基于多维度加权计算综合热度分，具体算法实现已隐藏。

        Args:
            movie: 影片模型对象
            search_count: 搜索次数
            weight_adjust: 人工权重调整系数
            chart_ranks: 榜单排名数据

        Returns:
            float: 热度分（0-100）
        """
        # 核心算法逻辑已隐藏, 可根据实际需求实现自定义的评分算法
        # your_algorithm_here
        return 0.0

    def _build_exclude_tag_conditions(self):
        """构建标签排除条件"""
        excluded_tags = self.exclusion_config.get("excluded_tags", [])
        if not excluded_tags:
            return None

        conditions = []
        for tag in excluded_tags:
            # 转义 SQL LIKE 特殊字符
            escaped = tag.replace('\\', '\\\\').replace('%', '\\%').replace('_', '\\_')
            conditions.append(Movie.tags.like(f'%{escaped}%', escape='\\'))

        return not_(or_(*conditions)) if conditions else None

    async def _get_search_counts(self, session: AsyncSession) -> Dict[int, int]:
        """获取所有影片的搜索次数统计"""
        query = select(UserSearch.series_title, func.sum(UserSearch.search_count).label("total"))
        query = query.group_by(UserSearch.series_title)
        result = await session.execute(query)

        # series_title 是影片标题，需要映射到 movie_id
        search_counts = defaultdict(int)
        rows = result.all()

        if not rows:
            return {}

        # 获取所有标题对应的影片ID
        titles = [row.series_title for row in rows if row.series_title]
        if not titles:
            return {}

        # 查询标题到ID的映射
        movie_query = select(Movie.id, Movie.title).where(Movie.title.in_(titles))
        movie_result = await session.execute(movie_query)
        title_to_id = {row.title: row.id for row in movie_result.all()}

        for row in rows:
            movie_id = title_to_id.get(row.series_title)
            if movie_id:
                search_counts[movie_id] = int(row.total or 0)

        return dict(search_counts)

    async def _get_chart_ranks(self, session: AsyncSession) -> Dict[int, Dict[str, int]]:
        """获取影片在各榜单中的排名
        从 lj_ranks 表读取：
        - 热搜榜 id=1
        - 热播榜 id=2
        - 新片榜 id=3

        Returns:
            Dict[int, Dict[str, int]]: {movie_id: {"searchHot": 1, "watchHot": 5, "newMovies": 3}}
        """
        from app.models.entities import Rank

        # 榜单ID映射: rank_id -> 榜单名称
        chart_types = {
            1: "searchHot",    # 热搜榜
            2: "watchHot",     # 热播榜
            3: "newMovies"     # 新片榜
        }

        chart_ranks = defaultdict(dict)

        for rank_id, chart_name in chart_types.items():
            query = select(Rank).where(Rank.id == rank_id)
            result = await session.execute(query)
            chart_data = result.scalar_one_or_none()

            if chart_data and chart_data.movies:
                try:
                    movies_data = json.loads(chart_data.movies) if isinstance(chart_data.movies, str) else []
                    # movies 是列表，每个元素可能是 dict 或简单类型
                    # 记录每个影片在该榜单的排名（从1开始）
                    for rank, movie_item in enumerate(movies_data, start=1):
                        try:
                            # 处理不同的数据格式
                            if isinstance(movie_item, dict):
                                movie_id = int(movie_item.get("id", 0))
                            elif isinstance(movie_item, (int, str)):
                                movie_id = int(movie_item)
                            else:
                                continue

                            if movie_id > 0:
                                chart_ranks[movie_id][chart_name] = rank
                        except (ValueError, TypeError):
                            continue
                except (json.JSONDecodeError, TypeError) as e:
                    logger.warning(f"解析榜单 {chart_name} (id={rank_id}) 数据失败: {e}")
                    continue

        total_ranked = len(chart_ranks)
        total_records = sum(len(ranks) for ranks in chart_ranks.values())
        logger.info(f"榜单数据加载完成：{total_ranked} 部影片在榜，共 {total_records} 条排名记录")

        return dict(chart_ranks)

    async def get_movies_for_section(
        self,
        session: AsyncSession,
        section_name: str,
        interventions: Optional[Dict[str, Any]] = None,
        search_counts: Optional[Dict[int, int]] = None,
        chart_ranks: Optional[Dict[int, Dict[str, int]]] = None
    ) -> List[int]:
        """获取指定区块的推荐影片ID列表

        Args:
            session: 数据库会话
            section_name: 区块名称（banner, latest, hot_movies等）
            interventions: 人工干预配置
            search_counts: 搜索次数映射（预先查询好）

        Returns:
            List[int]: 影片ID列表（按推荐顺序）
        """
        from app.utils.config_loader import get_section_config

        section_config = get_section_config(self.config, section_name)
        if not section_config:
            logger.warning(f"未找到区块配置: {section_name}")
            return []

        interventions = interventions or {"pinned": [], "blocked": set(), "weight_adjust": {}}
        blocked_ids = interventions.get("blocked", set())

        data_type = section_config.get("type")
        category = section_config.get("category")
        count = section_config.get("count", 12)
        order_by = section_config.get("order_by", "heat_score")
        min_score = section_config.get("min_score", 0)
        days_window = section_config.get("days_window")

        # 构建基础查询条件
        conditions = []

        # 排除伦理片
        excluded_categories = self.exclusion_config.get("excluded_categories", [5])
        conditions.append(Movie.category.notin_(excluded_categories))

        # 分类筛选
        if category:
            conditions.append(Movie.category == category)

        # 最低评分要求
        if min_score > 0:
            conditions.append(Movie.score >= min_score)

        # 封面要求（Banner等）
        require_cover = section_config.get("require_cover", False)
        if require_cover:
            conditions.append(Movie.covers != "")
            conditions.append(Movie.covers.isnot(None))

        # 时间窗口（最新上线）
        if days_window:
            current_time = datetime.now().timestamp()
            start_time = current_time - days_window * 86400
            conditions.append(Movie.update_time >= start_time)

        # 标签排除
        tag_exclude_condition = self._build_exclude_tag_conditions()
        if tag_exclude_condition is not None:
            conditions.append(tag_exclude_condition)

        # 获取置顶列表
        pinned_ids = interventions.get("pinned", [])

        # 对于banner区块，如果有置顶影片，需要单独查询这些影片（不受筛选条件限制）
        pinned_movies = []
        if pinned_ids and section_name == "banner":
            # 构建置顶影片查询条件
            pinned_conditions = [Movie.id.in_(pinned_ids)]
            if blocked_ids:
                pinned_conditions.append(Movie.id.notin_(blocked_ids))

            pinned_query = select(Movie).where(and_(*pinned_conditions))
            pinned_result = await session.execute(pinned_query)
            pinned_movies = pinned_result.scalars().all()
            logger.info(f"Banner区块有 {len(pinned_movies)} 部置顶影片")

        # 查询符合条件的影片（用于算法推荐）
        query = select(Movie).where(and_(*conditions))
        result = await session.execute(query)
        movies = result.scalars().all()

        # 使用传入的搜索次数，如果没有则查询
        if search_counts is None:
            search_counts = await self._get_search_counts(session)

        # 计算热度分并排序
        movie_scores = []
        for movie in movies:
            # 跳过屏蔽列表
            if movie.id in blocked_ids:
                continue

            # 获取搜索次数
            search_count = search_counts.get(movie.id, 0)

            # 获取权重调整
            weight_adjust = interventions.get("weight_adjust", {}).get(movie.id, 1.0)

            # 计算热度分（传入榜单排名数据）
            heat_score = self.calculate_heat_score(movie, search_count, weight_adjust, chart_ranks)

            movie_scores.append({
                "id": movie.id,
                "heat_score": heat_score,
                "update_time": movie.update_time or 0
            })

        # 排序
        if order_by == "update_time":
            # 按更新时间倒序
            movie_scores.sort(key=lambda x: x["update_time"], reverse=True)
        else:
            # 默认按热度分倒序（包含榜单加成）
            movie_scores.sort(key=lambda x: x["heat_score"], reverse=True)

        sorted_ids = [m["id"] for m in movie_scores]

        # 构建最终结果：置顶影片 + 算法推荐影片
        final_ids = []

        # 1. 首先添加置顶影片（保持用户设置的顺序）
        pinned_id_set = set()
        for mid in pinned_ids:
            # 查找置顶影片（可能从pinned_movies或movie_scores中获取）
            if mid in [m.id for m in pinned_movies]:
                final_ids.append(mid)
                pinned_id_set.add(mid)
            elif mid in sorted_ids:
                # 如果置顶影片也满足筛选条件，使用它
                final_ids.append(mid)
                pinned_id_set.add(mid)

        # 2. 然后添加算法推荐的影片（排除已置顶的）
        for mid in sorted_ids:
            if mid not in pinned_id_set:
                final_ids.append(mid)

        # 限制数量
        return final_ids[:count]

    async def get_all_recommendations(
        self,
        session: AsyncSession
    ) -> Dict[str, List[int]]:
        """获取所有区块的推荐结果

        Returns:
            Dict[str, List[int]]: {section_name: [movie_id, ...]}
        """
        sections = self.config.get("sections", {})
        results = {}

        # 获取当前时间
        current_time = int(datetime.now().timestamp())

        # 预先获取所有搜索次数（性能优化，避免每个区块都查询）
        logger.info("正在获取搜索次数统计...")
        search_counts = await self._get_search_counts(session)
        logger.info(f"搜索次数统计完成，共 {len(search_counts)} 部影片有搜索记录")

        # 预先获取榜单排名数据（性能优化，用于热度分计算）
        logger.info("正在获取榜单排名数据...")
        chart_ranks = await self._get_chart_ranks(session)
        total_ranked = sum(len(ranks) for ranks in chart_ranks.values())
        logger.info(f"榜单排名数据完成，共 {len(chart_ranks)} 部影片在榜，总计 {total_ranked} 条排名记录")

        for section_name in sections.keys():
            data_type = sections[section_name].get("type", 0)

            # 获取该区块的人工干预
            interventions = await HomePageConfig.get_interventions(
                session, data_type, current_time
            )

            # 获取推荐列表（传入搜索次数和榜单排名避免重复查询）
            movie_ids = await self.get_movies_for_section(
                session, section_name, interventions, search_counts, chart_ranks
            )
            results[section_name] = movie_ids

            logger.info(f"区块 [{section_name}] 推荐 {len(movie_ids)} 部影片")

        return results
