import os
import json
from redis.asyncio import Redis

# Ініціалізуємо Redis клієнта глобально
redis_client: Redis = None

async def init_redis() -> Redis:
    """
    Ініціалізує та повертає клієнт Redis.
    Якщо змінна REDIS_URL не задана, використовується значення за замовчуванням.
    """
    global redis_client
    if redis_client is None:
        redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")
        redis_client = Redis.from_url(redis_url)
    return redis_client

async def get_cached_user(email: str) -> dict | None:
    """
    Отримує дані користувача з кешу за ключем, сформованим на основі email.
    """
    client = await init_redis()
    data = await client.get(f"user:{email}")
    if data:
        return json.loads(data)
    return None

async def set_cached_user(email: str, user_data: dict, expire: int = 300) -> None:
    """
    Зберігає дані користувача у кеші з часом життя expire (за замовчуванням 5 хвилин).
    """
    client = await init_redis()
    await client.setex(f"user:{email}", expire, json.dumps(user_data))
