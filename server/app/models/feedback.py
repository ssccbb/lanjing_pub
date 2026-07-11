"""反馈/留言模型"""
from datetime import datetime
from sqlalchemy import String, Text, DateTime, Integer, func
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class Feedback(Base):
    """用户反馈/求片留言表 - 对应 lj_feedback 表"""
    __tablename__ = "lj_feedback"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    content: Mapped[str] = mapped_column(Text, default="")
    email: Mapped[str] = mapped_column(String(255), default="")
    contact: Mapped[str] = mapped_column(String(255), default="")  # 联系方式（手机/微信等）
    feedback_type: Mapped[int] = mapped_column(Integer, default=1)  # 1=求片留言, 2=意见反馈, 3=问题报告
    status: Mapped[int] = mapped_column(Integer, default=0)  # 0=待处理, 1=已处理, 2=已忽略
    create_time: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    update_time: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())
    remark: Mapped[str] = mapped_column(Text, default="")  # 管理员备注

    def to_dict(self) -> dict:
        """转换为字典"""
        return {
            "id": self.id,
            "content": self.content,
            "email": self.email,
            "contact": self.contact,
            "feedback_type": self.feedback_type,
            "status": self.status,
            "create_time": self.create_time.isoformat() if self.create_time else "",
            "update_time": self.update_time.isoformat() if self.update_time else "",
            "remark": self.remark
        }
