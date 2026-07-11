"""搜索相关模型"""
from datetime import datetime
from typing import Optional

from sqlalchemy import String, Integer, BigInteger, Index
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class UserSearch(Base):
    """用户搜索历史表"""
    __tablename__ = "user_searchs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    series_title: Mapped[str] = mapped_column(String(500), default="", comment="影片名称")
    search_count: Mapped[int] = mapped_column(Integer, default=1, comment="搜索次数")
    update_time: Mapped[int] = mapped_column(BigInteger, default=0, comment="更新时间戳")

    def __repr__(self):
        return f"<UserSearch(id={self.id}, series_title={self.series_title}, count={self.search_count})>"
