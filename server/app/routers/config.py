"""配置管理路由"""
from fastapi import APIRouter
from pydantic import BaseModel
from typing import List

from app.config import settings, reload_settings
from app.utils.logger import get_logger

logger = get_logger(__name__)
router = APIRouter()


class ConfigInfo(BaseModel):
    """配置信息（不包含敏感数据）"""
    app_name: str
    app_version: str
    debug: bool
    host: str
    port: int
    mysql_host: str
    mysql_port: int
    mysql_db: str
    mysql_charset: str
    redis_host: str
    redis_port: int
    redis_db: int
    cors_origins: List[str]
    log_level: str


@router.get("/info", response_model=ConfigInfo)
async def get_config_info():
    """获取当前配置信息（不包含敏感数据）"""
    return ConfigInfo(
        app_name=settings.app_name,
        app_version=settings.app_version,
        debug=settings.debug,
        host=settings.host,
        port=settings.port,
        mysql_host=settings.mysql_host,
        mysql_port=settings.mysql_port,
        mysql_db=settings.mysql_db,
        mysql_charset=settings.mysql_charset,
        redis_host=settings.redis_host,
        redis_port=settings.redis_port,
        redis_db=settings.redis_db,
        cors_origins=settings.cors_origins,
        log_level=settings.log_level,
    )


@router.get("/cors")
async def get_cors_config():
    """获取CORS配置"""
    return {
        "allow_origins": settings.cors_origins,
        "allow_credentials": True,
        "allow_methods": ["*"],
        "allow_headers": ["*"],
    }


@router.post("/reload")
async def reload_config():
    """
    重新加载配置（从.env文件）
    注意：部分配置需要重启服务才能生效
    """
    import os
    from dotenv import load_dotenv

    # 重新加载环境变量
    env_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env')
    load_dotenv(env_path, override=True)

    # 清除缓存，强制重新加载
    new_settings = reload_settings()

    return {
        "message": "配置已重新加载",
        "note": "部分配置（如端口、数据库连接）需要重启服务才能生效",
        "cors_origins": new_settings.cors_origins,
    }
