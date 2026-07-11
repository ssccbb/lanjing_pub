"""日志配置"""
import sys
from pathlib import Path
from loguru import logger

from app.config import settings

# 使用 PROJECT_ROOT 构建日志路径，确保日志写入外层 logs 目录
log_dir = Path(settings.PROJECT_ROOT) / "logs"
log_dir.mkdir(parents=True, exist_ok=True)

# 日志文件路径
log_path = log_dir / "app.log"
access_log_path = log_dir / "access.log"

# 移除默认处理器
logger.remove()

# 添加控制台输出
logger.add(
    sys.stdout,
    level=settings.log_level,
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
           "<level>{level: <8}</level> | "
           "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - "
           "<level>{message}</level>",
)

# 添加文件输出
logger.add(
    str(log_path),
    level=settings.log_level,
    rotation="10 MB",
    retention="30 days",
    encoding="utf-8",
)

# 添加访问日志文件输出（单独文件）
logger.add(
    str(access_log_path),
    level="INFO",
    rotation="50 MB",
    retention="30 days",
    encoding="utf-8",
    filter=lambda record: record["extra"].get("type") == "access",
    format="{time:YYYY-MM-DD HH:mm:ss} | {message}",
)


def get_logger(name: str):
    """获取带名称的logger"""
    return logger.bind(name=name)


def get_access_logger():
    """获取访问日志logger"""
    return logger.bind(type="access")
