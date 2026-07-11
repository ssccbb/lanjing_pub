"""
弹幕系统 - SQLAlchemy 实体模型（简化版）
"""
from datetime import datetime
from typing import Optional

from sqlalchemy import String, Text, BigInteger, Integer, SmallInteger, DateTime, DECIMAL, Index
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class Danmaku(Base):
    """弹幕主表（简化版）"""
    __tablename__ = "danmaku"

    # 主键
    id: Mapped[str] = mapped_column(String(32), primary_key=True)
    video_id: Mapped[int] = mapped_column(BigInteger, nullable=False, index=True)

    # 发送者信息（简化）
    sender_user_id: Mapped[Optional[str]] = mapped_column(String(32), nullable=True, index=True)
    sender_name: Mapped[str] = mapped_column(String(64), nullable=False)

    # 内容
    content_text: Mapped[str] = mapped_column(Text, nullable=False)

    # 样式（只保留颜色）
    style_color: Mapped[str] = mapped_column(String(8), default="#FFFFFF")

    # 位置
    position_time: Mapped[float] = mapped_column(DECIMAL(10, 3), nullable=False)
    position_mode: Mapped[int] = mapped_column(SmallInteger, default=1)  # 1滚动 2顶部 3底部

    # 元数据
    meta_timestamp: Mapped[int] = mapped_column(BigInteger, nullable=False)
    meta_client_type: Mapped[int] = mapped_column(SmallInteger, default=1)

    # 状态与互动
    status: Mapped[int] = mapped_column(SmallInteger, default=1)  # 0待审核 1通过 2拒绝 3删除
    likes: Mapped[int] = mapped_column(Integer, default=0)

    # 时间戳
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # 索引
    __table_args__ = (
        Index("idx_video_time", "video_id", "position_time"),
        Index("idx_video_status", "video_id", "status"),
    )

    def to_item(self) -> dict:
        """转换为API响应格式"""
        mode_map = {1: "scroll", 2: "top", 3: "bottom"}
        return {
            "id": self.id,
            "text": self.content_text,
            "time": float(self.position_time),
            "mode": mode_map.get(self.position_mode, "scroll"),
            "color": self.style_color,
            "userId": self.sender_user_id,
            "userName": self.sender_name,
            "likes": self.likes,
            "createdAt": self.meta_timestamp,
        }


class DanmakuLike(Base):
    """弹幕点赞表"""
    __tablename__ = "danmaku_likes"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    danmaku_id: Mapped[str] = mapped_column(String(32), nullable=False, index=True)
    user_id: Mapped[str] = mapped_column(String(32), nullable=False, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    __table_args__ = (
        Index("uk_danmaku_user", "danmaku_id", "user_id", unique=True),
    )


class DanmakuStats(Base):
    """弹幕统计表"""
    __tablename__ = "danmaku_stats"

    video_id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    total_count: Mapped[int] = mapped_column(Integer, default=0)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
