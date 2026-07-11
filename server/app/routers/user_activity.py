"""用户活动相关接口"""
import time
from typing import Optional
from pydantic import BaseModel
from fastapi import APIRouter, Depends, Request, Path, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc, func, delete, over

from app.database import get_db
from app.utils.response import Response
from app.utils.antibot import check_user_agent
from app.models.user_activity import UserPageVisit, UserWatchHistory
from app.services.user_service import UserService

router = APIRouter(dependencies=[Depends(check_user_agent)])


class PageVisitRequest(BaseModel):
    """页面访问记录请求"""
    path: str


@router.post("/visit")
async def record_page_visit(
    request: Request,
    data: PageVisitRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    记录用户页面访问
    需要在 Header 中携带 Authorization: Bearer {accesstoken}
    """
    # 从 Header 获取 accesstoken
    auth_header = request.headers.get("Authorization", "")
    if not auth_header.startswith("Bearer "):
        return Response.error("缺少有效的访问令牌")

    accesstoken = auth_header.replace("Bearer ", "")
    if not accesstoken:
        return Response.error("访问令牌不能为空")

    # 验证 accesstoken 是否有效
    user_service = UserService(db)
    user = await user_service.get_user_by_accesstoken(accesstoken)
    if not user:
        return Response.error("访问令牌无效或已过期")

    try:
        # 创建访问记录
        page_visit = UserPageVisit(
            accesstoken=accesstoken,
            path=data.path,
            timestamp=int(time.time())
        )
        db.add(page_visit)
        await db.commit()

        return Response.success({"message": "记录成功"})
    except Exception as e:
        await db.rollback()
        import logging
        logging.getLogger(__name__).error(f"记录页面访问失败: {e}")
        return Response.error("记录失败")


@router.get("/visit/list")
async def get_page_visit_list(
    request: Request,
    page: int = 1,
    page_size: int = 20,
    db: AsyncSession = Depends(get_db)
):
    """
    获取当前用户的页面访问记录
    需要在 Header 中携带 Authorization: Bearer {accesstoken}
    """
    # 从 Header 获取 accesstoken
    auth_header = request.headers.get("Authorization", "")
    if not auth_header.startswith("Bearer "):
        return Response.error("缺少有效的访问令牌")

    accesstoken = auth_header.replace("Bearer ", "")
    if not accesstoken:
        return Response.error("访问令牌不能为空")

    # 验证 accesstoken 是否有效
    user_service = UserService(db)
    user = await user_service.get_user_by_accesstoken(accesstoken)
    if not user:
        return Response.error("访问令牌无效或已过期")

    try:
        # 查询总数
        count_query = select(func.count()).where(UserPageVisit.accesstoken == accesstoken)
        count_result = await db.execute(count_query)
        total = count_result.scalar() or 0

        # 查询列表
        query = (
            select(UserPageVisit)
            .where(UserPageVisit.accesstoken == accesstoken)
            .order_by(desc(UserPageVisit.create_time))
            .offset((page - 1) * page_size)
            .limit(page_size)
        )
        result = await db.execute(query)
        visits = result.scalars().all()

        return Response.success({
            "list": [v.to_dict() for v in visits],
            "total": total,
            "page": page,
            "page_size": page_size
        })
    except Exception as e:
        import logging
        logging.getLogger(__name__).error(f"获取页面访问记录失败: {e}")
        return Response.error("获取记录失败")


# ==================== 用户观看历史管理接口 ====================

@router.get("/watch-history")
async def get_user_watch_history(
    accesstoken: str = Query(..., description="用户访问令牌"),
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页数量"),
    db: AsyncSession = Depends(get_db)
):
    """
    查询指定用户的影片观看历史记录
    同一movie_id只返回时间最新的一条

    参数:
        accesstoken: 用户访问令牌
        page: 页码，从1开始
        page_size: 每页数量，默认20，最大100
    """
    try:
        # 子查询：获取每个movie_id的最新记录的ID
        # 使用 GROUP BY 配合 MAX(create_time) 找到每个影片的最新记录
        latest_subquery = (
            select(
                UserWatchHistory.movie_id,
                func.max(UserWatchHistory.create_time).label("latest_time")
            )
            .where(UserWatchHistory.accesstoken == accesstoken)
            .group_by(UserWatchHistory.movie_id)
        ).subquery("latest")

        # 主查询：关联子查询获取完整记录
        # 通过 movie_id 和 create_time 关联，确保取到最新的那条
        filtered_query = (
            select(UserWatchHistory)
            .join(
                latest_subquery,
                (UserWatchHistory.movie_id == latest_subquery.c.movie_id) &
                (UserWatchHistory.create_time == latest_subquery.c.latest_time)
            )
            .where(UserWatchHistory.accesstoken == accesstoken)
            .order_by(desc(UserWatchHistory.create_time))
        )

        # 查询去重后的总数
        count_query = (
            select(func.count())
            .select_from(latest_subquery)
        )
        count_result = await db.execute(count_query)
        total = count_result.scalar() or 0

        # 查询列表（分页）
        paginated_query = filtered_query.offset((page - 1) * page_size).limit(page_size)
        result = await db.execute(paginated_query)
        records = result.scalars().all()

        return Response.success({
            "list": [r.to_dict() for r in records],
            "total": total,
            "page": page,
            "page_size": page_size
        })
    except Exception as e:
        import logging
        logging.getLogger(__name__).error(f"查询用户观看历史失败: {e}")
        import traceback
        traceback.print_exc()
        return Response.error("查询失败")


@router.delete("/watch-history/all")
async def delete_all_watch_history(
    accesstoken: str = Query(..., description="用户访问令牌"),
    db: AsyncSession = Depends(get_db)
):
    """
    全删指定用户的全部影片记录

    参数:
        accesstoken: 用户访问令牌
    """
    try:
        # 删除该用户的所有观看记录
        delete_query = delete(UserWatchHistory).where(UserWatchHistory.accesstoken == accesstoken)
        result = await db.execute(delete_query)
        await db.commit()

        deleted_count = result.rowcount

        return Response.success({
            "message": "删除成功",
            "deleted_count": deleted_count
        })
    except Exception as e:
        await db.rollback()
        import logging
        logging.getLogger(__name__).error(f"删除全部观看记录失败: {e}")
        return Response.error("删除失败")


@router.delete("/watch-history/{movie_id}")
async def delete_watch_history_record(
    movie_id: str = Path(..., description="影片ID"),
    accesstoken: str = Query(..., description="用户访问令牌"),
    db: AsyncSession = Depends(get_db)
):
    """
    单删指定用户的指定影片记录

    参数:
        movie_id: 影片ID（路径参数）
        accesstoken: 用户访问令牌（查询参数）
    """
    try:
        # 先查询记录是否存在且属于该用户
        query = select(UserWatchHistory).where(
            UserWatchHistory.movie_id == movie_id,
            UserWatchHistory.accesstoken == accesstoken
        )
        result = await db.execute(query)
        record = result.scalar_one_or_none()

        if not record:
            return Response.error("记录不存在或无权限删除")

        # 删除记录（根据movie_id和accesstoken删除）
        delete_query = delete(UserWatchHistory).where(
            UserWatchHistory.movie_id == movie_id,
            UserWatchHistory.accesstoken == accesstoken
        )
        await db.execute(delete_query)
        await db.commit()

        return Response.success({"message": "删除成功"})
    except Exception as e:
        await db.rollback()
        import logging
        logging.getLogger(__name__).error(f"删除观看记录失败: {e}")
        return Response.error("删除失败")
