"""Redis缓存管理"""
import json
from typing import Optional, Any, List

import redis.asyncio as redis

from app.config import settings

redis_client: Optional[redis.Redis] = None


async def init_redis():
    """初始化Redis连接"""
    global redis_client
    redis_client = redis.from_url(
        settings.redis_url,
        encoding="utf-8",
        decode_responses=True,
        socket_connect_timeout=5,
        socket_timeout=5,
        max_connections=50,
    )


async def close_redis():
    """关闭Redis连接"""
    global redis_client
    if redis_client:
        await redis_client.close()


def get_redis() -> redis.Redis:
    """获取Redis客户端"""
    if not redis_client:
        raise RuntimeError("Redis not initialized")
    return redis_client


async def cache_get(key: str) -> Optional[Any]:
    """获取缓存"""
    try:
        r = get_redis()
        data = await r.get(key)
        if data:
            try:
                return json.loads(data)
            except json.JSONDecodeError:
                return data
    except Exception:
        pass
    return None


async def cache_set(key: str, value: Any, expire: int = 300) -> bool:
    """设置缓存"""
    try:
        r = get_redis()
        if isinstance(value, (dict, list)):
            value = json.dumps(value, ensure_ascii=False)
        await r.setex(key, expire, value)
        return True
    except Exception:
        return False


async def cache_delete(key: str) -> bool:
    """删除缓存"""
    try:
        r = get_redis()
        return await r.delete(key) > 0
    except Exception:
        return False


async def cache_delete_pattern(pattern: str) -> int:
    """根据模式删除缓存"""
    try:
        r = get_redis()
        keys = await r.keys(pattern)
        if keys:
            return await r.delete(*keys)
        return 0
    except Exception:
        return 0


async def cache_get_multi(keys: List[str]) -> dict:
    """批量获取缓存"""
    if not keys:
        return {}

    try:
        r = get_redis()
        values = await r.mget(keys)
        result = {}
        for key, value in zip(keys, values):
            if value:
                try:
                    result[key] = json.loads(value)
                except json.JSONDecodeError:
                    result[key] = value
        return result
    except Exception:
        return {}


async def cache_set_multi(mapping: dict, expire: int = 300) -> bool:
    """批量设置缓存"""
    if not mapping:
        return True

    try:
        r = get_redis()
        pipe = r.pipeline()
        for key, value in mapping.items():
            if isinstance(value, (dict, list)):
                value = json.dumps(value, ensure_ascii=False)
            pipe.setex(key, expire, value)
        await pipe.execute()
        return True
    except Exception:
        return False


def cache_key(prefix: str, *args, **kwargs) -> str:
    """生成缓存key"""
    parts = [prefix]
    if args:
        parts.extend(str(a) for a in args)
    if kwargs:
        parts.extend(f"{k}={v}" for k, v in sorted(kwargs.items()))
    return ":".join(parts)
