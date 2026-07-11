"""用户活动相关模型"""
from datetime import datetime
from sqlalchemy import String, Text, DateTime, Integer, BigInteger, func, JSON, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class UserWatchHistory(Base):
    """用户观看历史记录表"""
    __tablename__ = "user_watch_history"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    accesstoken: Mapped[str] = mapped_column(String(255), default="", index=True)
    movie_id: Mapped[str] = mapped_column(String(50), default="", index=True)

    # 添加唯一约束：同一用户的同一影片只能有一条记录
    __table_args__ = (
        UniqueConstraint('accesstoken', 'movie_id', name='uq_watch_history_accesstoken_movie'),
    )
    episode_id: Mapped[str] = mapped_column(String(50), default="")
    timestamp: Mapped[int] = mapped_column(BigInteger, default=0)
    covers: Mapped[list] = mapped_column(JSON, default=list)  # JSON类型存储封面列表
    title: Mapped[str] = mapped_column(String(500), default="")
    tags: Mapped[list] = mapped_column(JSON, default=list)  # JSON类型存储标签列表
    create_time: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    def to_dict(self) -> dict:
        """转换为字典"""
        return {
            "id": self.id,
            "movie_id": self.movie_id,
            "episode_id": self.episode_id,
            "timestamp": self.timestamp,
            "covers": self.covers if self.covers else [],
            "title": self.title,
            "tags": self.tags if self.tags else [],
            "create_time": self.create_time.isoformat() if self.create_time else ""
        }


class UserPageVisit(Base):
    """用户页面访问记录表"""
    __tablename__ = "user_page_visit"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    accesstoken: Mapped[str] = mapped_column(String(255), default="", index=True)
    path: Mapped[str] = mapped_column(String(500), default="")
    timestamp: Mapped[int] = mapped_column(BigInteger, default=0)
    create_time: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    def to_dict(self) -> dict:
        """转换为字典"""
        return {
            "id": self.id,
            "path": self.path,
            "timestamp": self.timestamp,
            "create_time": self.create_time.isoformat() if self.create_time else ""
        }


class UserFeedback(Base):
    """用户反馈记录表"""
    __tablename__ = "user_feedback"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    accesstoken: Mapped[str] = mapped_column(String(255), default="", index=True)
    content: Mapped[str] = mapped_column(Text, default="")
    email: Mapped[str] = mapped_column(String(255), default="")
    contact: Mapped[str] = mapped_column(String(255), default="")
    feedback_type: Mapped[int] = mapped_column(Integer, default=1)  # 1=求片留言, 2=意见反馈, 3=问题报告
    status: Mapped[int] = mapped_column(Integer, default=0)  # 0=待处理, 1=已处理, 2=已忽略
    client_ip: Mapped[str] = mapped_column(String(100), default="")
    remark: Mapped[str] = mapped_column(Text, default="")
    create_time: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    update_time: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())

    def to_dict(self) -> dict:
        """转换为字典"""
        return {
            "id": self.id,
            "content": self.content,
            "email": self.email,
            "contact": self.contact,
            "feedback_type": self.feedback_type,
            "status": self.status,
            "client_ip": self.client_ip,
            "remark": self.remark,
            "create_time": self.create_time.isoformat() if self.create_time else "",
            "update_time": self.update_time.isoformat() if self.update_time else ""
        }
