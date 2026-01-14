from fastapi import FastAPI, HTTPException, BackgroundTasks
from pydantic import BaseModel
import asyncio
import redis.asyncio as redis
from pygg import GGClient
from config import uin, password, redis_host, redis_port, redis_db
import uvicorn
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()
redis_client = None
bot_client = None

class FastGG(GGClient):
    async def on_login_ok(self, packet):
        logger.info('Logged in successfully')

    async def on_message(self, packet):
        logger.info(f"Received message from {packet.sender}: {packet.raw}")
        # Example of using redis to count messages
        if redis_client:
            await redis_client.incr("message_count")

    async def on_login_failed(self, packet):
        logger.error('Login failed')
        self.should_disconnect = True

class MessageRequest(BaseModel):
    uin: int
    content: str

@app.on_event("startup")
async def startup_event():
    global redis_client, bot_client
    logger.info("Starting up...")
    
    # Initialize Redis
    try:
        redis_client = redis.Redis(host=redis_host, port=redis_port, db=redis_db)
        await redis_client.ping()
        logger.info("Connected to Redis")
    except Exception as e:
        logger.error(f"Failed to connect to Redis: {e}")

    # Initialize Bot
    bot_client = FastGG(uin, password)
    
    # Start bot connection in background
    asyncio.create_task(bot_client.connect(reconnect=True))

@app.on_event("shutdown")
async def shutdown_event():
    logger.info("Shutting down...")
    if bot_client:
        await bot_client.disconnect()
    if redis_client:
        await redis_client.close()

@app.post("/send_message")
async def send_message(request: MessageRequest):
    if not bot_client:
        raise HTTPException(status_code=503, detail="Bot not initialized")
    
    # Check if bot is connected/authenticated if possible, 
    # though imtoken check is a proxy for that.
    if not bot_client.imtoken:
         raise HTTPException(status_code=503, detail="Bot not connected or authenticated")
         
    await bot_client.send_message(request.uin, request.content)
    return {"status": "sent", "recipient": request.uin}

@app.get("/status")
async def get_status():
    connected = False
    if bot_client and bot_client.imtoken:
        connected = True
    
    message_count = 0
    if redis_client:
        val = await redis_client.get("message_count")
        if val:
            message_count = int(val)

    return {
        "connected": connected,
        "message_count": message_count
    }

if __name__ == '__main__':
    uvicorn.run(app, host="0.0.0.0", port=8080)