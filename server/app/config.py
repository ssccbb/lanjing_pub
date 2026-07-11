"""应用配置管理

所有配置项从环境变量或 .env 文件读取，无默认值。
配置文件加载顺序：../.env.shared → .env（后者覆盖前者）
"""
import os
from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """应用配置类 - 所有配置项必须从环境变量提供"""

    # 项目根目录
    PROJECT_ROOT: str = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

    # 应用信息
    app_name: str
    app_version: str
    debug: bool

    # 服务器
    host: str
    port: int

    # MySQL数据库
    mysql_host: str
    mysql_port: int
    mysql_user: str
    mysql_password: str
    mysql_db: str
    mysql_charset: str

    @property
    def mysql_url(self) -> str:
        """生成MySQL连接URL"""
        return (
            f"mysql+aiomysql://{self.mysql_user}:{self.mysql_password}"
            f"@{self.mysql_host}:{self.mysql_port}/{self.mysql_db}"
            f"?charset={self.mysql_charset}"
        )

    # Redis
    redis_host: str
    redis_port: int
    redis_password: str
    redis_db: int

    @property
    def redis_url(self) -> str:
        """生成Redis连接URL"""
        if self.redis_password:
            return f"redis://:{self.redis_password}@{self.redis_host}:{self.redis_port}/{self.redis_db}"
        return f"redis://{self.redis_host}:{self.redis_port}/{self.redis_db}"

    # CORS
    allow_origins: str

    @property
    def cors_origins(self) -> list:
        """解析允许的域名列表"""
        return [origin.strip() for origin in self.allow_origins.split(",")]

    # 日志
    log_level: str
    log_file: str

    # 请求签名密钥（与前端共用）
    NUXT_PUBLIC_AUTHOR_KEY: str
    # API 基础地址（共享配置）
    NUXT_PUBLIC_API_BASE: str
    # 短信测试验证码
    SMS_TEST_CODE: str

    # 联系邮箱
    NUXT_PUBLIC_CONTACT_EMAIL: str

    # 备案号
    NUXT_PUBLIC_ICP_NUMBER: str

    class Config:
        # 先加载共享配置，再加载私有配置（私有配置优先级更高）
        env_file = ("../.env.shared", ".env")
        env_file_encoding = "utf-8"
        # 允许额外的环境变量（如前端专用的 NUXT_PUBLIC_DEBUG_API_BASE）
        extra = "ignore"


@lru_cache()
def get_settings() -> Settings:
    """获取配置单例"""
    return Settings()


def reload_settings() -> Settings:
    """重新加载配置"""
    get_settings.cache_clear()
    return get_settings()


settings = get_settings()
