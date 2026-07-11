"""数据库连接管理"""
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base

from app.config import settings

# 创建异步引擎 - 优化连接池配置
engine = create_async_engine(
    settings.mysql_url,
    echo=settings.debug,
    # 连接池配置
    pool_size=20,              # 基础连接数（增加）
    max_overflow=30,           # 最大溢出连接（增加）
    pool_pre_ping=True,        # 连接前ping检测
    pool_recycle=3600,         # 连接回收时间（1小时）
    pool_timeout=30,           # 获取连接超时时间
    # 执行超时
    connect_args={
        "connect_timeout": 10,  # 连接超时10秒
    }
)

# 会话工厂 - 优化配置
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)

# 模型基类
Base = declarative_base()


async def get_db():
    """获取数据库会话（依赖注入用）"""
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def init_db():
    """初始化数据库"""
    async with engine.begin() as conn:
        pass


async def close_db():
    """关闭数据库连接"""
    await engine.dispose()
