import json
from functools import wraps

from fastapi.encoders import jsonable_encoder
from sqlalchemy.ext.asyncio import AsyncSession

from app.authentication.models import User
from app.config import get_cache, set_cache


def cache_response(key_func, ttl=300):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            key = key_func(*args, **kwargs)
            cached = await get_cache(key)
            if cached:
                return json.loads(cached)
            result = await func(*args, **kwargs)
            encode_result = jsonable_encoder(result)
            await set_cache(key, json.dumps(encode_result), ttl)
            return result

        return wrapper

    return decorator


def user_cache_key(current_user: User, db: AsyncSession):
    return f"user_profile:{current_user.id}"
