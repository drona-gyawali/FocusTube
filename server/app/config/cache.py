from app.config import conf
from redis.asyncio import Redis

redis: Redis | None = None


async def init_redis():
    """Initialize Redis connection at app startup"""
    global redis
    redis = Redis(
        host=conf.redis_host,
        port=conf.redis_port,
        db=conf.redis_db,
        password=conf.redis_password,
        decode_responses=True,
    )


async def close_redis():
    """Close Redis connection at app shutdown"""
    global redis
    if redis:
        await redis.close()


async def get_cache(key: str):
    if not redis:
        raise RuntimeError("Redis not initialized. Call init_redis() first.")
    return await redis.get(key)


async def set_cache(key: str, value: str, ttl: int = 300):
    if not redis:
        raise RuntimeError("Redis not initialized. Call init_redis() first.")
    await redis.set(key, value, ex=ttl)


async def delete_cache(key: str):
    if not redis:
        raise RuntimeError("Redis not initialized. Call init_redis() first.")
    await redis.delete(key)
