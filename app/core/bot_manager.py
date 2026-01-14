import asyncio
import logging
from typing import Dict, Optional, List
import redis.asyncio as redis
from app.core.bot_client import FastGG
from app.core.config import settings

logger = logging.getLogger(__name__)

class BotManager:
    def __init__(self):
        self.active_bots: Dict[int, FastGG] = {}
        self.redis_client: Optional[redis.Redis] = None

    async def initialize_redis(self):
        try:
            self.redis_client = redis.Redis(
                host=settings.REDIS_HOST, 
                port=settings.REDIS_PORT, 
                db=settings.REDIS_DB
            )
            await self.redis_client.ping()
            logger.info("BotManager connected to Redis")
        except Exception as e:
            logger.error(f"BotManager failed to connect to Redis: {e}")
            raise e

    async def close_redis(self):
        if self.redis_client:
            await self.redis_client.close()

    async def start_bot(self, uin: int, password: str, events: List[str], settings_dict: Optional[dict] = None) -> FastGG:
        if uin in self.active_bots:
            raise ValueError("Bot already connected")
        
        if not self.redis_client:
            raise RuntimeError("Redis not initialized")

        bot = FastGG(uin, password, events, self.redis_client)
        
        if settings_dict:
            if 'gender' in settings_dict:
                bot.roulette_settings.gender = int(settings_dict['gender'])
            if 'min_age' in settings_dict:
                bot.roulette_settings.min_age = int(settings_dict['min_age'])
            if 'max_age' in settings_dict:
                bot.roulette_settings.max_age = int(settings_dict['max_age'])
        else:
            # Apply default settings if not provided
            bot.roulette_settings.gender = settings.DEFAULT_GENDER
            bot.roulette_settings.min_age = settings.MIN_AGE
            bot.roulette_settings.max_age = settings.MAX_AGE

        self.active_bots[uin] = bot
        asyncio.create_task(bot.connect(reconnect=True))
        return bot

    async def stop_bot(self, uin: int):
        bot = self.active_bots.get(uin)
        if bot:
            await bot.disconnect()
            del self.active_bots[uin]
            return True
        return False

    async def shutdown_all(self):
        tasks = [bot.disconnect() for bot in self.active_bots.values()]
        if tasks:
            await asyncio.gather(*tasks)
        await self.close_redis()

    def get_bot(self, uin: int) -> Optional[FastGG]:
        return self.active_bots.get(uin)

# Global instance
manager = BotManager()
