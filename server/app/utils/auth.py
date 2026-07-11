"""
用户认证工具模块
基于项目的 accesstoken 机制
"""
from fastapi import Request, HTTPException, status
from typing import Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.database import get_db
from app.models.entities import User


async def get_current_user(request: Request) -> Dict[str, Any]:
    """
    获取当前登录用户
    从 Authorization: Bearer {accesstoken} Header 中获取 token
    """
    # 从 Header 获取 accesstoken
    auth_header = request.headers.get("Authorization", "")
    if not auth_header.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="缺少有效的访问令牌",
            headers={"WWW-Authenticate": "Bearer"},
        )

    accesstoken = auth_header.replace("Bearer ", "").strip()
    if not accesstoken:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="访问令牌不能为空",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # 从数据库验证 accesstoken
    from app.database import AsyncSessionLocal
    async with AsyncSessionLocal() as db:
        result = await db.execute(
            select(User).where(User.accesstoken == accesstoken)
        )
        user = result.scalar_one_or_none()

        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="访问令牌无效或已过期",
                headers={"WWW-Authenticate": "Bearer"},
            )

        user_data = {
            "user_id": str(user.uid),
            "nickname": user.name or "匿名用户",
            "avatar": user.avatar,
            "accesstoken": accesstoken,
            "role": user.role,  # 0=普通用户, 1=管理员, 2=付费用户
        }
        return user_data


async def get_optional_user(request: Request) -> Optional[Dict[str, Any]]:
    """可选的用户认证，未登录返回 None 而不是报错"""
    try:
        return await get_current_user(request)
    except HTTPException:
        return None
