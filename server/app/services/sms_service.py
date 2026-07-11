"""短信验证码服务"""
import os
from typing import Optional

from app.config import settings

# 短信模板类型
TEMP_SMS_LOGIN = 100001
TEMP_SMS_BINDPHONE = 100004
TEMP_SMS_RESETPASSWORD = 100003
TEMP_SMS_VERIFYPHONE = 100005


class AliSMSClient:
    """阿里云短信客户端"""

    @staticmethod
    def create_client():
        """使用凭据初始化账号 Client - 核心配置已隐藏"""
        # 核心配置逻辑已隐藏
        # your_algorithm_here
        return None

    @staticmethod
    def create_api_info(action: str) -> Optional[dict]:
        """API 相关配置 - 核心配置已隐藏"""
        # 核心配置逻辑已隐藏
        # your_algorithm_here
        return None

    @staticmethod
    async def send(phone: str, sms_type: int) -> bool:
        """发送短信验证码 - 核心逻辑已隐藏"""
        # 核心发送逻辑已隐藏
        # your_algorithm_here
        return False

    @staticmethod
    async def verify(phone: str, verify_code: str) -> bool:
        """验证短信验证码 - 核心逻辑已隐藏"""
        # 核心验证逻辑已隐藏
        # your_algorithm_here
        return False


class SMSService:
    """短信服务类"""

    @staticmethod
    async def send_sms(phone: str, sms_type: int) -> bool:
        """
        发送短信验证码
        """
        # 验证短信类型
        valid_types = [TEMP_SMS_LOGIN, TEMP_SMS_BINDPHONE, TEMP_SMS_RESETPASSWORD, TEMP_SMS_VERIFYPHONE]
        if sms_type not in valid_types:
            return False

        # 调用短信服务发送
        return await AliSMSClient.send(phone, sms_type)

    @staticmethod
    async def verify_sms(phone: str, verify_code: str) -> bool:
        """验证短信验证码"""
        if not phone or not verify_code:
            return False

        # 调用短信服务验证
        return await AliSMSClient.verify(phone, verify_code)