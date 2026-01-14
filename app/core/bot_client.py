import json
import time
import logging
from typing import List, Set
from pygg import GGClient
import redis.asyncio as redis

logger = logging.getLogger(__name__)

class FastGG(GGClient):
    def __init__(self, uin, password, events: List[str], redis_conn: redis.Redis):
        super().__init__(uin, password)
        self.subscribed_events: Set[str] = set(events)
        self.redis = redis_conn
        self.uin = int(uin)

    async def _emit_event(self, event_type: str, payload: dict):
        """Helper to push event to Redis if subscribed."""
        if event_type in self.subscribed_events and self.redis:
            # Envelope the data with bot_uin context
            event_data = {
                "bot_uin": self.uin,
                "event": event_type,
                "timestamp": time.time(),
                "data": payload
            }
            try:
                await self.redis.rpush("gg:events", json.dumps(event_data))
            except Exception as e:
                logger.error(f"Failed to push event to Redis: {e}")

    async def on_login_ok(self, packet):
        logger.info(f'[{self.uin}] Logged in successfully')
        await self._emit_event("system", {"status": "logged_in"})

    async def on_login_failed(self, packet):
        logger.error(f'[{self.uin}] Login failed')
        await self._emit_event("system", {"status": "login_failed"})
        self.should_disconnect = True

    async def on_message(self, packet):
        logger.info(f"[{self.uin}] Message from {packet.sender}: {packet.raw}")
        await self._emit_event("message", {
            "sender": packet.sender,
            "content": packet.raw,
            "packet_timestamp": packet.timestamp
        })

    async def on_roulette_result(self, packet):
        logger.info(f"[{self.uin}] Roulette result: {packet.content}")
        await self._emit_event("roulette", packet.content)
        
    async def on_status(self, packet):
        if "status" in self.subscribed_events:
            await self._emit_event("status", {
                "user_uin": packet.uin,
                "status": packet.status,
                "description": packet.description
            })
