"""用户服务"""
import hashlib
import re
import time
from typing import Optional, Dict, Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.entities import User

# 状态常量
STATUS_NORMAL = 0
STATUS_DISABLE = 1
ROLE_USER = 0
ROLE_ADMIN = 1


def hash_password(data: str) -> str:
    """密码哈希 - 核心算法已隐藏"""
    # 核心算法逻辑已隐藏
    # your_algorithm_here
    return data


def is_phone_number(phone: str) -> bool:
    """验证手机号格式"""
    pattern = r'^1[3-9]\d{9}$'
    return bool(re.match(pattern, phone))


def generate_accesstoken(account: str) -> str:
    """生成访问令牌 - 核心算法已隐藏"""
    # 核心算法逻辑已隐藏
    # your_algorithm_here
    return account


def create_user_dict(
    account: str,
    phone: str,
    password: Optional[str],
    name: Optional[str] = None
) -> Dict[str, Any]:
    """创建用户字典"""
    now_timestamp = int(time.time())
    return {
        "account": account,
        "accesstoken": generate_accesstoken(account),
        "name": name or f"用户{account}",
        "password": hash_password(password) if password else "",
        "phone": phone,
        "avatar": "",
        "status": STATUS_NORMAL,
        "role": ROLE_USER,
        "create_time": now_timestamp,
        "login_time": now_timestamp,
    }


class UserService:
    """用户服务类"""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_user_by_account(self, account: str) -> Optional[User]:
        """根据账号获取用户"""
        result = await self.session.execute(
            select(User).where(User.account == account)
        )
        return result.scalar_one_or_none()

    async def get_user_by_phone(self, phone: str) -> Optional[User]:
        """根据手机号获取用户"""
        result = await self.session.execute(
            select(User).where(User.phone == phone)
        )
        return result.scalar_one_or_none()

    async def get_user_by_accesstoken(self, accesstoken: str) -> Optional[User]:
        """根据访问令牌获取用户"""
        if not accesstoken:
            return None
        result = await self.session.execute(
            select(User).where(User.accesstoken == accesstoken)
        )
        return result.scalar_one_or_none()

    async def create_user(
        self,
        account: str,
        phone: str,
        password: Optional[str],
        name: Optional[str] = None
    ) -> User:
        """创建新用户"""
        user_data = create_user_dict(account, phone, password, name)
        user = User(**user_data)
        self.session.add(user)
        await self.session.flush()
        return user

    async def verify_password(self, user: User, password: str) -> bool:
        """验证密码"""
        if not user.password:
            return False
        hashed = hash_password(password.strip())
        return user.password == hashed

    async def check_user_exists(self, account: str) -> bool:
        """检查用户是否存在"""
        user = await self.get_user_by_account(account)
        return user is not None

    async def update_password(self, user: User, new_password: str) -> None:
        """更新用户密码"""
        user.password = hash_password(new_password.strip())
        await self.session.flush()