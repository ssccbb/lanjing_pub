"""
弹幕系统 - API 路由
拆分为公开路由(pub_router)和需要鉴权的路由(web_router)
响应格式统一使用 Response.success() / Response.error()
"""
from typing import Optional

from fastapi import APIRouter, Depends, Query, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.services.danmaku_service import DanmakuService
from app.models.schemas.danmaku import (
    SendDanmakuRequest,
)
from app.utils.auth import get_current_user
from app.utils.response import Response


# ==================== 公开路由（无需鉴权）====================
pub_router = APIRouter(prefix="/danmaku", tags=["弹幕-公开接口"])


@pub_router.get("/{video_id}")
async def get_danmaku_list(
    video_id: int,
    start_time: Optional[float] = Query(None, alias="startTime", ge=0),
    end_time: Optional[float] = Query(None, alias="endTime", ge=0),
    cursor: Optional[str] = None,
    limit: int = Query(100, ge=1, le=1000),
    db: AsyncSession = Depends(get_db),
):
    """获取弹幕列表 - 公开接口"""
    try:
        result = await DanmakuService.get_danmaku_list(
            db=db,
            video_id=video_id,
            start_time=start_time,
            end_time=end_time,
            cursor=cursor,
            limit=limit,
        )
        return Response.success({
            "items": result.items,
            "pagination": result.pagination.model_dump()
        })
    except Exception as e:
        return Response.error(f"获取弹幕列表失败: {str(e)}")


@pub_router.get("/{video_id}/timeline")
async def get_danmaku_timeline(
    video_id: int,
    db: AsyncSession = Depends(get_db),
):
    """获取弹幕时间轴（热度分布）- 公开接口"""
    try:
        result = await DanmakuService.get_timeline(db, video_id)
        return Response.success({
            "videoId": result.videoId,
            "markers": [m.model_dump() for m in result.markers],
            "total": result.total
        })
    except Exception as e:
        return Response.error(f"获取弹幕时间轴失败: {str(e)}")


# ==================== 需要鉴权的路由 ====================
web_router = APIRouter(prefix="/danmaku", tags=["弹幕-用户接口"])


@web_router.post("/{video_id}")
async def send_danmaku(
    video_id: int,
    request: SendDanmakuRequest,
    http_request: Request,
    db: AsyncSession = Depends(get_db),
    user_info: dict = Depends(get_current_user),
):
    """发送弹幕 - 需要登录"""
    try:
        result = await DanmakuService.send_danmaku(
            db=db,
            video_id=video_id,
            text=request.text,
            time=request.time,
            mode=request.mode,
            color=request.color,
            user_id=user_info.get("user_id"),
            user_name=user_info.get("nickname"),
            user_role=user_info.get("role"),  # 传递用户角色
            client_type=request.clientType,
        )

        if result.success:
            return Response.success({
                "id": result.id,
                "timestamp": result.timestamp,
                "color": result.color  # 返回实际使用的颜色
            }, message="弹幕发送成功")
        else:
            return Response.error(result.error or "发送失败", code=400)
    except Exception as e:
        return Response.error(f"发送弹幕失败: {str(e)}")


@web_router.post("/{danmaku_id}/like")
async def like_danmaku(
    danmaku_id: str,
    db: AsyncSession = Depends(get_db),
    user_info: dict = Depends(get_current_user),
):
    """点赞/取消点赞弹幕 - 需要登录"""
    try:
        user_id = user_info.get("user_id")
        if not user_id:
            return Response.error("用户未登录", code=401)

        result = await DanmakuService.like_danmaku(db, danmaku_id, user_id)

        if result.success:
            return Response.success({
                "likes": result.likes,
                "isLiked": result.isLiked
            }, message="点赞成功" if result.isLiked else "取消点赞成功")
        else:
            return Response.error("操作失败", code=400)
    except Exception as e:
        return Response.error(f"点赞操作失败: {str(e)}")


# ==================== 兼容旧版：保留 router 变量 ====================
# 如果需要使用原来的方式（单一路由器），可以使用这个
router = pub_router
