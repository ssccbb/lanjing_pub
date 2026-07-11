"""SQLAlchemy 实体模型 - 对应现有数据库表结构"""
from datetime import datetime
from typing import List, Optional

from sqlalchemy import String, Float, Integer, DateTime, Text, BigInteger, ForeignKey, select
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Movie(Base):
    """影片主表 - 对应 lj_movies 表"""
    __tablename__ = "lj_movies"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    category: Mapped[int] = mapped_column(Integer, default=0)
    title: Mapped[str] = mapped_column(String(2550), default="")
    other_titles: Mapped[str] = mapped_column(Text, default="")
    score: Mapped[float] = mapped_column(Float, default=0.0)
    covers: Mapped[str] = mapped_column(Text, default="")
    cover_tag: Mapped[str] = mapped_column(String(255), default="")
    contents: Mapped[str] = mapped_column(Text, default="")
    tags: Mapped[str] = mapped_column(Text, default="")
    season: Mapped[int] = mapped_column(Integer, default=0)
    directors: Mapped[str] = mapped_column(Text, default="")
    actors: Mapped[str] = mapped_column(Text, default="")
    series_title: Mapped[str] = mapped_column(String(255), default="")
    oneshot_desc: Mapped[str] = mapped_column(String(255), default="")
    douban_id: Mapped[str] = mapped_column(String(255), default="")
    imdb_id: Mapped[str] = mapped_column(String(255), default="")
    publish_year: Mapped[str] = mapped_column(String(255), default="")
    upload_time: Mapped[str] = mapped_column(String(255), default="")
    update_time: Mapped[float] = mapped_column(Float, default=0.0)
    search_keys: Mapped[str] = mapped_column(Text, default="")
    extra: Mapped[str] = mapped_column(Text, default="")
    recommend_num: Mapped[int] = mapped_column(Integer, default=0)

    # 关联剧集
    episodes: Mapped[List["Episode"]] = relationship(
        "Episode",
        primaryjoin="Movie.id == Episode.movie_id",
        lazy="selectin"
    )

    def to_dict(self, contain_episodes: bool = False) -> dict:
        """转换为响应字典"""
        import json

        def parse_json_field(field_value):
            """解析 JSON 字符串字段"""
            if not field_value:
                return []
            if isinstance(field_value, str):
                try:
                    return json.loads(field_value)
                except:
                    return []
            return field_value

        # 解析列表字段
        other_titles = parse_json_field(self.other_titles)
        covers = parse_json_field(self.covers)
        tags = parse_json_field(self.tags)
        directors = parse_json_field(self.directors)
        actors = parse_json_field(self.actors)
        extra = parse_json_field(self.extra)
        if isinstance(extra, list):
            extra = {}

        data = {
            "id": str(self.id),
            "category": self.category,
            "title": self.title or "",
            "other_titles": other_titles,
            "score": self.score or 0.0,
            "covers": covers,
            "cover_tag": self.cover_tag or "",
            "contents": self.contents or "",
            "tags": tags,
            "season": self.season or 0,
            "directors": directors,
            "actors": actors,
            "series_title": self.series_title or "",
            "oneshot_desc": self.oneshot_desc or "",
            "publish_year": self.publish_year or "",
            "upload_time": self.upload_time or "",
            "update_time": self.update_time or 0.0,
            "extra": self._parse_extra(extra, covers),
            "recommend_num": self.recommend_num or 0,
            "link_douban": f"https://movie.douban.com/subject/{self.douban_id}/" if self.douban_id else "",
            "link_imdb": f"https://www.imdb.com/name/{self.imdb_id}/" if self.imdb_id else "",
        }

        # 剧集信息
        if contain_episodes and self.episodes:
            data["episode_sources"] = self._parse_episodes(self.episodes)
        else:
            data["episode_sources"] = []

        return data

    def _parse_episodes(self, episodes: List["Episode"]) -> List[dict]:
        """解析剧集列表，按播放源分组"""
        from collections import defaultdict

        # 按 source_from 分组
        source_groups = defaultdict(list)
        for ep in episodes:
            source_name = ep.source_from or "默认线路"
            source_groups[source_name].append({
                "id": str(ep.id),
                "title": ep.title or f"第{ep.id}集",
                "m3u8_link": ep.m3u8_link or "",
                "link_type": ep.link_type or 0,
                "duration": ep.duration or 0,
                "source_link": ep.source_link or "",
                "source_limit": ep.source_limit or 0  # 播放限制: 0=无限制, 1=需登录, 2=需付费
            })

        # 转换为 episode_sources 格式
        result = []
        for source_name, eps in source_groups.items():
            result.append({
                "source_name": source_name,
                "episodes": eps
            })

        return result

    def _parse_extra(self, extra: dict, covers: list) -> dict:
        """解析 extra 字段"""
        if not isinstance(extra, dict):
            extra = {}
        return {
            "watch_count": extra.get("watch_count", 0),
            "recommend_count": extra.get("recommend_count", 0),
            "unrecommend_count": extra.get("unrecommend_count", 0),
            "main_share_cover": extra.get("main_share_cover", covers[0] if covers else ""),
            "horizontal_cover": extra.get("horizontal_cover", ""),
            **extra
        }


class Episode(Base):
    """剧集表 - 对应 lj_episodes 表"""
    __tablename__ = "lj_episodes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    movie_id: Mapped[int] = mapped_column(ForeignKey("lj_movies.id"), default=0)
    title: Mapped[str] = mapped_column(String(2550), default="")
    m3u8_link: Mapped[str] = mapped_column(String(255), default="")
    link_type: Mapped[int] = mapped_column(Integer, default=0)
    duration: Mapped[int] = mapped_column(Integer, default=0)
    source_from: Mapped[str] = mapped_column(String(255), default="")
    source_link: Mapped[str] = mapped_column(String(255), default="")
    source_limit: Mapped[int] = mapped_column(Integer, default=0)  # 播放限制: 0=无限制, 1=需登录, 2=需付费


class Actor(Base):
    """演员表 - 对应 actors 表"""
    __tablename__ = "actors"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(255), default="")
    eng_name: Mapped[str] = mapped_column(String(255), default="")
    sex: Mapped[str] = mapped_column(String(255), default="")
    birth: Mapped[str] = mapped_column(String(255), default="")
    address: Mapped[str] = mapped_column(String(255), default="")
    link_imdb: Mapped[str] = mapped_column(String(255), default="")
    profassion: Mapped[str] = mapped_column(String(255), default="")
    link: Mapped[str] = mapped_column(String(255), default="")
    avatar: Mapped[str] = mapped_column(String(255), default="")
    contents: Mapped[str] = mapped_column(Text, default="")
    movies: Mapped[str] = mapped_column(Text, default="")


class Rank(Base):
    """排行榜表 - 对应 lj_ranks 表"""
    __tablename__ = "lj_ranks"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(255), default="")
    description: Mapped[str] = mapped_column(Text, default="")
    cover: Mapped[str] = mapped_column(String(555), default="")
    movies: Mapped[str] = mapped_column(Text, default="")  # JSON字符串，需要解析
    rank_type: Mapped[int] = mapped_column(Integer, default=0)
    create_time: Mapped[str] = mapped_column(String(555), default="")
    update_time: Mapped[str] = mapped_column(String(555), default="")
    marks: Mapped[str] = mapped_column(String(255), default="")


class Watchlist(Base):
    """片单表 - 对应 lj_watchlist 表"""
    __tablename__ = "lj_watchlist"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(255), default="")
    description: Mapped[str] = mapped_column(Text, default="")
    cover: Mapped[str] = mapped_column(Text, default="")
    movies: Mapped[str] = mapped_column(Text, default="")  # JSON字符串，需要解析
    create_time: Mapped[str] = mapped_column(String(555), default="")
    update_time: Mapped[str] = mapped_column(String(555), default="")
    marks: Mapped[str] = mapped_column(String(255), default="")


class User(Base):
    """用户表"""
    __tablename__ = "user"

    uid: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    account: Mapped[str] = mapped_column(String(255), default="")
    accesstoken: Mapped[str] = mapped_column(String(255), default="")
    name: Mapped[str] = mapped_column(String(255), default="")
    password: Mapped[str] = mapped_column(String(255), default="")
    phone: Mapped[str] = mapped_column(String(255), default="")
    avatar: Mapped[str] = mapped_column(String(255), default="")
    status: Mapped[int] = mapped_column(Integer, default=0)  # 0=正常, 1=禁用
    role: Mapped[int] = mapped_column(Integer, default=0)    # 0=普通用户, 1=管理员, 2=付费用户
    create_time: Mapped[int] = mapped_column(BigInteger, default=0)  # 创建时间戳
    login_time: Mapped[int] = mapped_column(BigInteger, default=0)   # 最后登录时间戳

    def to_dict(self, exclude_sensitive: bool = True) -> dict:
        """转换为字典"""
        data = {
            "uid": self.uid,
            "account": self.account,
            "accesstoken": self.accesstoken,
            "name": self.name,
            "phone": self.phone,
            "avatar": self.avatar,
            "status": self.status,
            "role": self.role,
            "create_time": self.create_time,
            "login_time": self.login_time,
        }

        if exclude_sensitive:
            data.pop("password", None)

        return data


class HomePageData(Base):
    """首页数据配置表 - 对应 home_page_data 表"""
    __tablename__ = "home_page_data"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    type: Mapped[int] = mapped_column(Integer, default=0)  # 1=banner, 2=最新上线, 3=热门电影, 4=热播电视剧, 5=热门综艺, 6=动漫推荐
    movie_ids: Mapped[str] = mapped_column(Text, default="")  # JSON格式的影片ID列表
    update_time: Mapped[int] = mapped_column(BigInteger, default=0)

    @staticmethod
    async def update_movie_ids(
        session,
        data_type: int,
        movie_ids: List[str]
    ) -> bool:
        """更新指定类型的影片ID列表

        Args:
            session: 数据库会话
            data_type: 数据类型 (1-6)
            movie_ids: 影片ID字符串列表

        Returns:
            bool: 是否成功
        """
        import json
        from datetime import datetime

        # 查询现有记录
        query = select(HomePageData).where(HomePageData.type == data_type)
        result = await session.execute(query)
        home_data = result.scalar_one_or_none()

        movie_ids_json = json.dumps(movie_ids, ensure_ascii=False)
        current_time = int(datetime.now().timestamp())

        if home_data:
            # 更新现有记录
            home_data.movie_ids = movie_ids_json
            home_data.update_time = current_time
        else:
            # 创建新记录
            home_data = HomePageData(
                type=data_type,
                movie_ids=movie_ids_json,
                update_time=current_time
            )
            session.add(home_data)

        await session.commit()
        return True


class AutoIndex(Base):
    """首页索引配置表 - 对应 auto_index 表"""
    __tablename__ = "auto_index"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    item_key: Mapped[str] = mapped_column(String(100), default="")
    item_type: Mapped[str] = mapped_column(String(20), default="")  # banner, category等
    data_json: Mapped[str] = mapped_column(Text, default="")  # JSON格式数据
    sort_order: Mapped[int] = mapped_column(Integer, default=0)  # 排序顺序，越小越靠前
