"""统一API响应格式"""
from typing import Any, Optional


class Status:
    """状态码"""
    OK = 200
    FAIL = 500
    TASK_RUNNING = 9000
    LOGIN_SMS_ERROR = 9001
    LOGIN_PASSWORD_EMPTY = 9002
    LOGIN_PASSWORD_ERROR = 9003
    PHONE_ALREADY_BOUND = 9004
    ACCOUNT_ALREADY_EXISTS = 9005
    USER_BANNED = 9006  # 用户被禁用


class Response:
    """响应工具类"""

    @staticmethod
    def success(data: Any = None, message: str = "success") -> dict:
        """成功响应"""
        return {
            "code": 200,
            "message": message,
            "data": data
        }

    @staticmethod
    def error(message: str = "error", code: int = 500, data: Any = None) -> dict:
        """错误响应"""
        return {
            "code": code,
            "message": message,
            "data": data
        }

    @staticmethod
    def not_found(message: str = "资源不存在") -> dict:
        return Response.error(message=message, code=404)

    @staticmethod
    def unauthorized(message: str = "未授权") -> dict:
        return Response.error(message=message, code=401)

    @staticmethod
    def bad_request(message: str = "请求参数错误") -> dict:
        return Response.error(message=message, code=400)

    @staticmethod
    def response(status: int = Status.OK, data: Any = None, message: str = "成功") -> dict:
        """自定义状态码响应"""
        return {
            "code": status,
            "data": data,
            "message": message
        }
