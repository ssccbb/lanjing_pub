"""用户接口"""
from typing import Optional

from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.utils.response import Response, Status
from app.services.user_service import UserService, is_phone_number, sha3_256_hash
from app.services.sms_service import SMSService, TEMP_SMS_LOGIN, TEMP_SMS_RESETPASSWORD, TEMP_SMS_BINDPHONE, TEMP_SMS_VERIFYPHONE

# 公开路由（无需签名）
pub_router = APIRouter()
# 需要签名的路由
router = APIRouter()


class LoginRequest(BaseModel):
    """登录请求"""
    account: str  # 账号
    password: str  # 密码（明文）


class RegisterRequest(BaseModel):
    """注册请求"""
    account: str   # 账号（用户名）
    phone: str     # 手机号
    password: str  # 密码（明文）
    sms_code: str  # 短信验证码
    name: str      # 昵称


class SendSMSRequest(BaseModel):
    """发送短信验证码请求"""
    account: str           # 手机号
    sms_for: Optional[str] = "login"  # 用途: login/register/bindphone/verify


class VerifySMSRequest(BaseModel):
    """验证短信验证码请求"""
    account: str   # 手机号
    sms_code: str  # 验证码


class ResetPasswordRequest(BaseModel):
    """重置密码请求"""
    phone: str      # 手机号
    old_password: str  # 旧密码
    new_password: str  # 新密码
    sms_code: str   # 短信验证码


# 登录注册接口禁用缓存的响应头
NO_CACHE_HEADERS = {
    "Cache-Control": "no-store, no-cache, must-revalidate, max-age=0",
    "Pragma": "no-cache",
    "Expires": "0",
}


@pub_router.post("/login")
async def user_login(
    data: LoginRequest,
    session: AsyncSession = Depends(get_db)
):
    """
    登录接口 - 仅用于已注册用户登录（仅限手机号）

    参数:
        account: 手机号
        password: 密码
    """
    account = data.account
    password = data.password

    # 参数验证
    if not account or not password:
        return JSONResponse(
            content=Response.error("手机号和密码不能为空！"),
            headers=NO_CACHE_HEADERS
        )

    # 校验手机号格式
    if not is_phone_number(account):
        return JSONResponse(
            content=Response.error("请输入正确的手机号！"),
            headers=NO_CACHE_HEADERS
        )

    user_service = UserService(session)

    # 查询用户（同时查 account 和 phone）
    user_by_account = await user_service.get_user_by_account(account)
    user_by_phone = await user_service.get_user_by_phone(account)
    user = user_by_account or user_by_phone

    if user is None:
        return JSONResponse(
            content=Response.response(
                Status.LOGIN_PASSWORD_ERROR,
                {},
                "账号不存在！"
            ),
            headers=NO_CACHE_HEADERS
        )

    # 检查用户是否被禁用
    if user.status == 1:
        return JSONResponse(
            content=Response.response(
                Status.USER_BANNED,
                {},
                "账号已被禁用，请联系客服"
            ),
            headers=NO_CACHE_HEADERS
        )

    # 校验密码
    if not user.password:
        return JSONResponse(
            content=Response.response(
                Status.LOGIN_PASSWORD_EMPTY,
                {},
                "未设置密码，请先设置密码！"
            ),
            headers=NO_CACHE_HEADERS
        )

    if not await user_service.verify_password(user, password):
        return JSONResponse(
            content=Response.response(
                Status.LOGIN_PASSWORD_ERROR,
                {},
                "密码错误！"
            ),
            headers=NO_CACHE_HEADERS
        )

    # 更新最后登录时间
    user.login_time = int(time.time())
    await session.commit()

    # 清理敏感字段后返回
    user_data = user.to_dict(exclude_sensitive=True)

    return JSONResponse(
        content=Response.success({
            "user": user_data,
            "timestamps": time.time()
        }),
        headers=NO_CACHE_HEADERS
    )


@pub_router.post("/register")
async def user_register(
    data: RegisterRequest,
    session: AsyncSession = Depends(get_db)
):
    """
    注册接口 - 仅用于新用户注册

    参数:
        account: 账号（用户名）
        phone: 手机号
        password: 密码
        sms_code: 短信验证码
        name: 昵称
    """
    account = data.account
    phone = data.phone
    password = data.password
    sms_code = data.sms_code
    name = data.name

    # 参数验证
    if not account or not phone or not password or not sms_code or not name:
        return JSONResponse(
            content=Response.error("请填写完整信息！"),
            headers=NO_CACHE_HEADERS
        )

    # 校验手机号格式
    if not is_phone_number(phone):
        return JSONResponse(
            content=Response.error("请输入正确的手机号！"),
            headers=NO_CACHE_HEADERS
        )

    user_service = UserService(session)

    # 查询用户（同时查 account 和 phone）
    user_by_account = await user_service.get_user_by_account(account)
    user_by_phone = await user_service.get_user_by_phone(phone)

    if user_by_account is not None:
        return JSONResponse(
            content=Response.response(
                Status.ACCOUNT_ALREADY_EXISTS,
                {},
                "该账号已存在！"
            ),
            headers=NO_CACHE_HEADERS
        )

    if user_by_phone is not None:
        return JSONResponse(
            content=Response.response(
                Status.PHONE_ALREADY_BOUND,
                {},
                "该手机号已被绑定！"
            ),
            headers=NO_CACHE_HEADERS
        )

    # 校验短信验证码
    verify_success = await SMSService.verify_sms(phone, sms_code)
    if not verify_success:
        return JSONResponse(
            content=Response.response(
                Status.LOGIN_SMS_ERROR,
                {},
                "短信验证码错误或已过期！"
            ),
            headers=NO_CACHE_HEADERS
        )

    # 注册用户
    try:
        user = await user_service.create_user(
            account=account,
            phone=phone,
            password=password,
            name=name
        )
    except Exception as e:
        return JSONResponse(
            content=Response.error(f"注册失败: {str(e)}"),
            headers=NO_CACHE_HEADERS
        )

    # 清理敏感字段后返回
    user_data = user.to_dict(exclude_sensitive=True)

    return JSONResponse(
        content=Response.success({
            "user": user_data,
            "new_user": True,
            "timestamps": time.time()
        }),
        headers=NO_CACHE_HEADERS
    )


@pub_router.post("/sendSMSCode")
async def send_sms_code(data: SendSMSRequest):
    """
    发送短信验证码
    """
    account = data.account
    sms_for = data.sms_for

    if not account:
        return JSONResponse(
            content=Response.error("参数错误！"),
            headers=NO_CACHE_HEADERS
        )

    # 校验手机号格式
    if not is_phone_number(account):
        return JSONResponse(
            content=Response.error("手机号格式错误！"),
            headers=NO_CACHE_HEADERS
        )

    # 确定短信类型
    sms_type = TEMP_SMS_LOGIN
    if sms_for:
        if sms_for == "login":
            sms_type = TEMP_SMS_LOGIN
        elif sms_for == "register":
            sms_type = TEMP_SMS_RESETPASSWORD
        elif sms_for == "bindphone":
            sms_type = TEMP_SMS_BINDPHONE
        elif sms_for == "verify":
            sms_type = TEMP_SMS_VERIFYPHONE

    # 发送短信
    success = await SMSService.send_sms(account, sms_type)
    if not success:
        return JSONResponse(
            content=Response.error("发送短信验证码失败！"),
            headers=NO_CACHE_HEADERS
        )

    return JSONResponse(
        content=Response.success({"results": success}),
        headers=NO_CACHE_HEADERS
    )


@pub_router.post("/verifySMSCode")
async def verify_sms_code(data: VerifySMSRequest):
    """
    验证短信验证码
    """
    account = data.account
    sms_code = data.sms_code

    if not account or not sms_code:
        return JSONResponse(
            content=Response.error("参数错误！"),
            headers=NO_CACHE_HEADERS
        )

    # 校验手机号格式
    if not is_phone_number(account):
        return JSONResponse(
            content=Response.error("手机号格式错误！"),
            headers=NO_CACHE_HEADERS
        )

    # 验证验证码
    verify_success = await SMSService.verify_sms(account, sms_code)

    return JSONResponse(
        content=Response.success({"results": verify_success}),
        headers=NO_CACHE_HEADERS
    )


@pub_router.post("/resetPassword")
async def reset_password(
    data: ResetPasswordRequest,
    session: AsyncSession = Depends(get_db)
):
    """
    重置密码接口

    参数:
        phone: 手机号
        old_password: 旧密码
        new_password: 新密码
        sms_code: 短信验证码

    验证流程:
        1. 验证手机号是否存在
        2. 验证旧密码是否正确
        3. 验证短信验证码是否正确
        4. 三个都验证通过则修改密码
    """
    phone = data.phone
    old_password = data.old_password
    new_password = data.new_password
    sms_code = data.sms_code

    # 参数验证
    if not phone or not old_password or not new_password or not sms_code:
        return JSONResponse(
            content=Response.error("请填写完整信息！"),
            headers=NO_CACHE_HEADERS
        )

    # 校验手机号格式
    if not is_phone_number(phone):
        return JSONResponse(
            content=Response.error("请输入正确的手机号！"),
            headers=NO_CACHE_HEADERS
        )

    # 新密码长度验证
    if len(new_password) < 6:
        return JSONResponse(
            content=Response.error("新密码长度不能少于6位！"),
            headers=NO_CACHE_HEADERS
        )

    user_service = UserService(session)

    # 1. 验证手机号是否存在
    user = await user_service.get_user_by_phone(phone)
    if user is None:
        return JSONResponse(
            content=Response.error("该手机号未注册！"),
            headers=NO_CACHE_HEADERS
        )

    # 2. 验证旧密码是否正确
    if not user.password:
        return JSONResponse(
            content=Response.error("该账号未设置密码！"),
            headers=NO_CACHE_HEADERS
        )

    if not await user_service.verify_password(user, old_password):
        return JSONResponse(
            content=Response.error("旧密码错误！"),
            headers=NO_CACHE_HEADERS
        )

    # 3. 验证短信验证码
    verify_success = await SMSService.verify_sms(phone, sms_code)
    if not verify_success:
        return JSONResponse(
            content=Response.error("短信验证码错误或已过期！"),
            headers=NO_CACHE_HEADERS
        )

    # 4. 三个验证都通过，修改密码
    try:
        await user_service.update_password(user, new_password)
        return JSONResponse(
            content=Response.success({}, "密码重置成功！"),
            headers=NO_CACHE_HEADERS
        )
    except Exception as e:
        return JSONResponse(
            content=Response.error(f"密码重置失败: {str(e)}"),
            headers=NO_CACHE_HEADERS
        )


@router.get("/profile")
async def get_profile():
    """获取用户信息（预留）"""
    return Response.success({"id": 1, "name": "用户"})


# 导入 time 模块
import time
