"""首页推荐人工干预配置表"""
from datetime import datetime
from typing import Optional, List

from sqlalchemy import String, Integer, Float, BigInteger, select, and_, or_
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class HomePageConfig(Base):
    """首页推荐人工干预配置表

    用于存储人工置顶、屏蔽、权重调整等干预操作
    """
    __tablename__ = "home_page_config"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    data_type: Mapped[int] = mapped_column(Integer, default=0, comment="对应home_page_data.type (1-6)")
    movie_id: Mapped[int] = mapped_column(Integer, default=0, comment="影片ID")
    action: Mapped[str] = mapped_column(String(20), default="", comment="操作类型: pin=置顶, block=屏蔽, boost=加权, reduce=降权")
    priority: Mapped[int] = mapped_column(Integer, default=0, comment="优先级，越小越靠前")
    weight_adjust: Mapped[float] = mapped_column(Float, default=1.0, comment="权重调整值（0.5-2.0）")
    expire_time: Mapped[int] = mapped_column(BigInteger, default=0, comment="过期时间戳（0=永不过期）")
    create_time: Mapped[int] = mapped_column(BigInteger, default=0, comment="创建时间戳")

    @staticmethod
    async def get_interventions(
        session,
        data_type: int,
        current_time: Optional[int] = None
    ) -> dict:
        """获取某区块的所有干预配置

        Returns:
            dict: {
                "pinned": [movie_id, ...],      # 置顶列表（按priority排序）
                "blocked": set(movie_id, ...),  # 屏蔽集合
                "weight_adjust": {movie_id: factor, ...}  # 权重调整映射
            }
        """
        if current_time is None:
            current_time = int(datetime.now().timestamp())

        query = select(HomePageConfig).where(
            and_(
                HomePageConfig.data_type == data_type,
                or_(
                    HomePageConfig.expire_time == 0,
                    HomePageConfig.expire_time > current_time
                )
            )
        ).order_by(HomePageConfig.priority.asc())

        result = await session.execute(query)
        configs = result.scalars().all()

        interventions = {
            "pinned": [],
            "blocked": set(),
            "weight_adjust": {}
        }

        for config in configs:
            if config.action == "pin":
                interventions["pinned"].append(config.movie_id)
            elif config.action == "block":
                interventions["blocked"].add(config.movie_id)
            elif config.action in ("boost", "reduce"):
                interventions["weight_adjust"][config.movie_id] = config.weight_adjust

        return interventions

    def to_dict(self) -> dict:
        """转换为字典"""
        return {
            "id": self.id,
            "data_type": self.data_type,
            "movie_id": self.movie_id,
            "action": self.action,
            "priority": self.priority,
            "weight_adjust": self.weight_adjust,
            "expire_time": self.expire_time,
            "create_time": self.create_time
        }
