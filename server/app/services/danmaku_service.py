"""
弹幕系统 - 业务逻辑层（简化版）
"""
import time as time_module
import random
import string
from datetime import datetime
from typing import Optional, List

from sqlalchemy import select, and_, func, asc, text
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.danmaku import Danmaku, DanmakuStats
from app.models.schemas.danmaku import (
    DanmakuItem, GetDanmakuListResponse, PaginationInfo,
    SendDanmakuResponse, LikeDanmakuResponse, DanmakuTimelineResponse,
    DanmakuTimelineMarker,
)


class DanmakuService:
    """弹幕服务"""

    @staticmethod
    def generate_id() -> str:
        """生成短ID"""
        timestamp = int(time_module.time() * 1000)
        random_part = ''.join(random.choices(string.ascii_lowercase + string.digits, k=4))
        return f"dk_{timestamp:x}{random_part}"

    @staticmethod
    async def get_danmaku_list(
        db: AsyncSession,
        video_id: int,
        start_time: Optional[float] = None,
        end_time: Optional[float] = None,
        cursor: Optional[str] = None,
        limit: int = 100,
    ) -> GetDanmakuListResponse:
        """获取弹幕列表"""

        conditions = [Danmaku.video_id == video_id, Danmaku.status == 1]

        if start_time is not None:
            conditions.append(Danmaku.position_time >= start_time)
        if end_time is not None:
            conditions.append(Danmaku.position_time <= end_time)

        if cursor:
            try:
                cursor_time = float(cursor)
                conditions.append(Danmaku.position_time > cursor_time)
            except ValueError:
                pass

        query = select(Danmaku).where(and_(*conditions))
        query = query.order_by(asc(Danmaku.position_time))
        query = query.limit(limit + 1)

        result = await db.execute(query)
        rows = result.scalars().all()

        has_more = len(rows) > limit
        items = list(rows[:limit])

        danmaku_items = [DanmakuService._entity_to_item(row) for row in items]

        next_cursor = None
        if has_more and items:
            next_cursor = str(float(items[-1].position_time))

        total = None
        if not cursor:
            count_result = await db.execute(
                select(func.count(Danmaku.id))
                .where(and_(Danmaku.video_id == video_id, Danmaku.status == 1))
            )
            total = count_result.scalar()

        return GetDanmakuListResponse(
            items=danmaku_items,
            pagination=PaginationInfo(
                hasMore=has_more,
                nextCursor=next_cursor,
                total=total,
            ),
        )

    @staticmethod
    def get_role_color(role: Optional[int] = None, user_color: Optional[str] = None) -> str:
        """
        根据用户角色获取弹幕颜色
        优先级：用户自定义颜色 > 管理员红色 > 付费用户金色 > 默认白色
        """
        # 如果用户有自定义颜色（不是默认白色），优先使用
        # 注意：忽略大小写比较
        if user_color and user_color.upper() != "#FFFFFF":
            return user_color

        # 根据角色设置颜色：1=管理员(红色), 2=付费用户(金色)
        if role == 1:
            return "#FF0000"  # 管理员 - 红色
        elif role == 2:
            return "#FFD700"  # 付费用户 - 金色

        return "#FFFFFF"  # 普通用户 - 白色

    @staticmethod
    async def send_danmaku(
        db: AsyncSession,
        video_id: int,
        text: str,
        time: float,
        mode: str = "scroll",
        color: Optional[str] = None,
        user_id: Optional[str] = None,
        user_name: Optional[str] = None,
        user_role: Optional[int] = None,
        client_type: str = "web",
    ) -> SendDanmakuResponse:
        """发送弹幕"""

        if len(text) > 200:
            return SendDanmakuResponse(success=False, error="弹幕内容超过200字符")

        danmaku_id = DanmakuService.generate_id()
        now = datetime.utcnow()
        timestamp = int(time_module.time() * 1000)

        mode_map = {"scroll": 1, "top": 2, "bottom": 3}

        # 根据角色确定弹幕颜色
        final_color = DanmakuService.get_role_color(user_role, color)

        danmaku = Danmaku(
            id=danmaku_id,
            video_id=video_id,
            sender_user_id=user_id,
            sender_name=user_name or "匿名用户",
            content_text=text,
            style_color=final_color,
            position_time=time,
            position_mode=mode_map.get(mode, 1),
            meta_timestamp=timestamp,
            meta_client_type={"web": 1, "ios": 2, "android": 3, "miniapp": 4, "pc": 5}.get(client_type, 1),
            status=1,
            likes=0,
            created_at=now,
            updated_at=now,
        )

        db.add(danmaku)
        await db.commit()

        return SendDanmakuResponse(success=True, id=danmaku_id, timestamp=timestamp, color=final_color)

    @staticmethod
    async def like_danmaku(
        db: AsyncSession,
        danmaku_id: str,
        user_id: str,
    ) -> LikeDanmakuResponse:
        """点赞/取消点赞弹幕"""

        from app.models.danmaku import DanmakuLike

        existing = await db.execute(
            select(DanmakuLike).where(
                and_(DanmakuLike.danmaku_id == danmaku_id, DanmakuLike.user_id == user_id)
            )
        )
        liked = existing.scalar_one_or_none()

        if liked:
            await db.delete(liked)
            await db.execute(
                text("UPDATE danmaku SET likes = GREATEST(likes - 1, 0) WHERE id = :id"),
                {"id": danmaku_id}
            )
            is_liked = False
        else:
            new_like = DanmakuLike(
                danmaku_id=danmaku_id,
                user_id=user_id,
                created_at=datetime.utcnow(),
            )
            db.add(new_like)
            await db.execute(
                text("UPDATE danmaku SET likes = likes + 1 WHERE id = :id"),
                {"id": danmaku_id}
            )
            is_liked = True

        await db.commit()

        result = await db.execute(
            select(Danmaku.likes).where(Danmaku.id == danmaku_id)
        )
        likes = result.scalar() or 0

        return LikeDanmakuResponse(success=True, likes=likes, isLiked=is_liked)

    @staticmethod
    async def get_timeline(
        db: AsyncSession,
        video_id: int,
    ) -> DanmakuTimelineResponse:
        """获取弹幕时间轴"""

        stats_result = await db.execute(
            select(DanmakuStats).where(DanmakuStats.video_id == video_id)
        )
        stats = stats_result.scalar_one_or_none()
        total = stats.total_count if stats else 0

        result = await db.execute(
            select(
                (func.floor(Danmaku.position_time / 10) * 10).label("time"),
                func.count().label("count"),
            )
            .where(and_(Danmaku.video_id == video_id, Danmaku.status == 1))
            .group_by(func.floor(Danmaku.position_time / 10))
            .order_by("time")
        )

        rows = result.all()
        max_count = max([row.count for row in rows], default=1)

        markers = [
            DanmakuTimelineMarker(
                time=float(row.time),
                count=row.count,
                heat=min(100, int((row.count / max_count) * 100)),
            )
            for row in rows
        ]

        return DanmakuTimelineResponse(
            videoId=video_id,
            markers=markers,
            total=total,
        )

    @staticmethod
    def _entity_to_item(entity: Danmaku) -> DanmakuItem:
        """实体转换为API响应格式"""
        mode_map = {1: "scroll", 2: "top", 3: "bottom", 4: "reverse"}

        return DanmakuItem(
            id=entity.id,
            text=entity.content_text,
            time=float(entity.position_time),
            mode=mode_map.get(entity.position_mode, "scroll"),
            color=entity.style_color,
            userId=entity.sender_user_id,
            userName=entity.sender_name,
            likes=entity.likes,
            createdAt=entity.meta_timestamp,
        )
