"""
弹幕系统 - Pydantic 数据模型（简化版）
"""
from typing import Optional, List, Literal
from pydantic import BaseModel, Field


# ==================== 弹幕项（简化后，前后端一致）====================

class DanmakuItem(BaseModel):
    """弹幕项 - 前后端统一格式"""
    id: str
    text: str = Field(..., max_length=200, description="弹幕内容")
    time: float = Field(..., ge=0, description="视频时间（秒）")
    mode: Literal["scroll", "top", "bottom"] = Field(default="scroll", description="显示模式")
    color: Optional[str] = Field(default="#FFFFFF", description="字体颜色")
    userId: Optional[str] = Field(default=None, description="发送者用户ID")
    userName: Optional[str] = Field(default=None, description="发送者昵称")
    likes: int = Field(default=0, description="点赞数")
    createdAt: int = Field(description="创建时间戳（毫秒）")


# ==================== 请求模型 ====================

class GetDanmakuListRequest(BaseModel):
    """获取弹幕列表请求"""
    startTime: Optional[float] = Field(default=None, ge=0, description="开始时间（秒）")
    endTime: Optional[float] = Field(default=None, ge=0, description="结束时间（秒）")
    cursor: Optional[str] = Field(default=None, description="分页游标")
    limit: int = Field(default=100, ge=1, le=1000, description="每页数量")


class SendDanmakuRequest(BaseModel):
    """发送弹幕请求"""
    text: str = Field(..., max_length=200, description="弹幕内容")
    time: float = Field(..., ge=0, description="视频时间（秒）")
    mode: Literal["scroll", "top", "bottom"] = Field(default="scroll", description="显示模式")
    color: Optional[str] = Field(default="#FFFFFF", description="字体颜色")
    clientType: Literal["web", "ios", "android", "miniapp", "pc"] = Field(default="web")


class LikeDanmakuRequest(BaseModel):
    """点赞弹幕请求"""
    danmakuId: str


# ==================== 响应模型 ====================

class PaginationInfo(BaseModel):
    """分页信息"""
    hasMore: bool
    nextCursor: Optional[str] = None
    total: Optional[int] = None


class GetDanmakuListResponse(BaseModel):
    """获取弹幕列表响应"""
    items: List[DanmakuItem]
    pagination: PaginationInfo


class SendDanmakuResponse(BaseModel):
    """发送弹幕响应"""
    success: bool
    id: Optional[str] = None
    timestamp: Optional[int] = None
    color: Optional[str] = None  # 实际使用的弹幕颜色
    error: Optional[str] = None


class LikeDanmakuResponse(BaseModel):
    """点赞弹幕响应"""
    success: bool
    likes: int
    isLiked: bool


class DanmakuTimelineMarker(BaseModel):
    """时间轴标记点"""
    time: float
    count: int
    heat: int = Field(..., ge=0, le=100)


class DanmakuTimelineResponse(BaseModel):
    """弹幕时间轴响应"""
    videoId: int
    markers: List[DanmakuTimelineMarker]
    total: int
