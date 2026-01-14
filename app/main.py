from fastapi import FastAPI
from app.routers import bots, system
from app.core.bot_manager import manager
from app.core.config import settings
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_app() -> FastAPI:
    app = FastAPI(title="GG Gateway", version="2.0.0")

    app.include_router(bots.router)
    app.include_router(system.router)

    @app.on_event("startup")
    async def startup_event():
        logger.info("Gateway starting up...")
        await manager.initialize_redis()

        # Login default bot from .env if present
        if settings.DEFAULT_UIN and settings.DEFAULT_PASSWORD:
            logger.info(f"Found default bot in config (UIN: {settings.DEFAULT_UIN}), connecting...")
            try:
                default_events = ["message", "roulette", "system"]
                await manager.start_bot(
                    settings.DEFAULT_UIN, 
                    settings.DEFAULT_PASSWORD, 
                    default_events
                )
            except Exception as e:
                logger.error(f"Failed to connect default bot: {e}")

    @app.on_event("shutdown")
    async def shutdown_event():
        logger.info("Gateway shutting down...")
        await manager.shutdown_all()

    return app

app = create_app()
