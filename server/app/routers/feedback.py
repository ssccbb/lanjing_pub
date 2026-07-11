"""反馈/留言接口"""
import time
import asyncio
from typing import Optional, Dict, Tuple, List
from pydantic import BaseModel
from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc, func

from app.database import get_db
from app.utils.response import Response
from app.utils.logger import get_logger
from app.utils.antibot import check_user_agent
from app.models.user_activity import UserFeedback
from app.services.user_service import UserService

logger = get_logger(__name__)
router = APIRouter(dependencies=[Depends(check_user_agent)])

# 简单的内存频率限制器
# 格式: {ip: (count, first_request_time)}
_rate_limit_store: Dict[str, Tuple[int, float]] = {}


def _check_rate_limit(ip: str, max_requests: int = 5, window_seconds: int = 60) -> bool:
    """
    检查 IP 是否超过频率限制
    :param ip: 客户端IP
    :param max_requests: 时间窗口内最大请求数
    :param window_seconds: 时间窗口（秒）
    :return: True 表示允许请求，False 表示超过限制
    """
    now = time.time()

    if ip in _rate_limit_store:
        count, first_time = _rate_limit_store[ip]

        # 检查是否在时间窗口内
        if now - first_time < window_seconds:
            if count >= max_requests:
                return False
            _rate_limit_store[ip] = (count + 1, first_time)
        else:
            # 重置时间窗口
            _rate_limit_store[ip] = (1, now)
    else:
        _rate_limit_store[ip] = (1, now)

    return True


def _get_client_ip(request: Request) -> str:
    """获取客户端IP"""
    forwarded = request.headers.get("x-forwarded-for")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.client.host if request.client else "unknown"


class FeedbackCreate(BaseModel):
    """创建反馈请求"""
    content: str
    email: Optional[str] = ""
    contact: Optional[str] = ""
    feedback_type: int = 1  # 1=求片留言, 2=意见反馈, 3=问题报告


@router.post("/create")
async def create_feedback(
    request: Request,
    data: FeedbackCreate,
    db: AsyncSession = Depends(get_db)
):
    """
    创建反馈/留言
    频率限制：每个IP每分钟最多5次提交
    """
    client_ip = _get_client_ip(request)

    # 检查频率限制
    if not _check_rate_limit(client_ip, max_requests=5, window_seconds=60):
        logger.warning(f"Rate limit exceeded for IP: {client_ip}")
        return Response.error("提交太频繁，请稍后再试")

    try:
        # 内容长度校验
        if len(data.content.strip()) < 5:
            return Response.error("内容至少需要5个字符")
        if len(data.content) > 1000:
            return Response.error("内容不能超过1000个字符")

        # 邮箱格式校验（如果提供）
        if data.email:
            email = data.email.strip()
            if len(email) > 100:
                return Response.error("邮箱地址过长")
            # 简单邮箱格式检查
            if '@' not in email or '.' not in email.split('@')[-1]:
                return Response.error("邮箱格式不正确")

        # 联系方式长度限制
        if data.contact and len(data.contact.strip()) > 100:
            return Response.error("联系方式过长")

        # 从 Header 获取 accesstoken（可选）
        auth_header = request.headers.get("Authorization", "")
        accesstoken = ""
        if auth_header.startswith("Bearer "):
            accesstoken = auth_header.replace("Bearer ", "")

        # 如果有 accesstoken，验证其有效性
        if accesstoken:
            user_service = UserService(db)
            user = await user_service.get_user_by_accesstoken(accesstoken)
            if not user:
                return Response.error("访问令牌无效或已过期")

        # 创建反馈记录（存入数据库）
        feedback = UserFeedback(
            accesstoken=accesstoken,
            content=data.content.strip(),
            email=data.email.strip() if data.email else "",
            contact=data.contact.strip() if data.contact else "",
            feedback_type=data.feedback_type,
            status=0,  # 待处理
            client_ip=client_ip,
            remark=""
        )
        db.add(feedback)
        await db.commit()
        await db.refresh(feedback)

        logger.info(f"Feedback created: id={feedback.id}, type={data.feedback_type}, ip={client_ip}, has_token={bool(accesstoken)}")

        return Response.success({
            "id": feedback.id,
            "message": "提交成功，我们会尽快处理"
        })

    except Exception as e:
        await db.rollback()
        import traceback
        logger.error(f"Create feedback failed: {e}")
        logger.error(traceback.format_exc())
        return Response.error(f"提交失败: {str(e)}")


@router.get("/list")
async def list_feedback(
    feedback_type: Optional[int] = None,
    status: Optional[int] = None,
    page: int = 1,
    page_size: int = 20,
    db: AsyncSession = Depends(get_db)
):
    """
    获取反馈列表（管理后台用）
    """
    try:
        # 构建查询
        query = select(UserFeedback)

        # 按类型筛选
        if feedback_type:
            query = query.where(UserFeedback.feedback_type == feedback_type)

        # 按状态筛选
        if status is not None:
            query = query.where(UserFeedback.status == status)

        # 查询总数
        count_query = select(func.count()).select_from(query.subquery())
        count_result = await db.execute(count_query)
        total = count_result.scalar() or 0

        # 按时间倒序排序并分页
        query = query.order_by(desc(UserFeedback.create_time))
        query = query.offset((page - 1) * page_size).limit(page_size)

        result = await db.execute(query)
        feedback_list = result.scalars().all()

        return Response.success({
            "list": [f.to_dict() for f in feedback_list],
            "page": page,
            "page_size": page_size,
            "total": total
        })

    except Exception as e:
        logger.error(f"List feedback failed: {e}")
        return Response.error("获取列表失败")


@router.post("/update/{feedback_id}")
async def update_feedback(
    feedback_id: int,
    status: int,
    remark: Optional[str] = "",
    db: AsyncSession = Depends(get_db)
):
    """
    更新反馈状态（管理后台用）
    """
    try:
        # 查找反馈
        query = select(UserFeedback).where(UserFeedback.id == feedback_id)
        result = await db.execute(query)
        feedback = result.scalar_one_or_none()

        if not feedback:
            return Response.not_found("反馈不存在")

        # 更新字段
        feedback.status = status
        if remark:
            feedback.remark = remark

        await db.commit()
        await db.refresh(feedback)

        return Response.success({"message": "更新成功"})

    except Exception as e:
        await db.rollback()
        logger.error(f"Update feedback failed: {e}")
        return Response.error("更新失败")


@router.get("/stats")
async def feedback_stats(
    db: AsyncSession = Depends(get_db)
):
    """
    获取反馈统计（管理后台用）
    """
    try:
        # 统计总数
        total_query = select(func.count()).select_from(UserFeedback)
        total_result = await db.execute(total_query)
        total = total_result.scalar() or 0

        # 统计各状态数量
        pending_query = select(func.count()).where(UserFeedback.status == 0)
        pending_result = await db.execute(pending_query)
        pending = pending_result.scalar() or 0

        processed_query = select(func.count()).where(UserFeedback.status == 1)
        processed_result = await db.execute(processed_query)
        processed = processed_result.scalar() or 0

        ignored_query = select(func.count()).where(UserFeedback.status == 2)
        ignored_result = await db.execute(ignored_query)
        ignored = ignored_result.scalar() or 0

        # 统计各类型数量
        type_movie_query = select(func.count()).where(UserFeedback.feedback_type == 1)
        type_movie_result = await db.execute(type_movie_query)
        type_movie = type_movie_result.scalar() or 0

        type_feedback_query = select(func.count()).where(UserFeedback.feedback_type == 2)
        type_feedback_result = await db.execute(type_feedback_query)
        type_feedback = type_feedback_result.scalar() or 0

        type_bug_query = select(func.count()).where(UserFeedback.feedback_type == 3)
        type_bug_result = await db.execute(type_bug_query)
        type_bug = type_bug_result.scalar() or 0

        return Response.success({
            "total": total,
            "pending": pending,
            "processed": processed,
            "ignored": ignored,
            "by_type": {
                "movie_request": type_movie,
                "feedback": type_feedback,
                "bug_report": type_bug
            }
        })

    except Exception as e:
        logger.error(f"Feedback stats failed: {e}")
        return Response.error("获取统计失败")
