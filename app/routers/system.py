from fastapi import APIRouter, Depends
from app.models.schemas import SystemStatus, BotStatus
from app.core.bot_manager import BotManager
from app.dependencies import get_bot_manager

router = APIRouter(tags=["system"])

@router.get("/status", response_model=SystemStatus)
async def get_system_status(manager: BotManager = Depends(get_bot_manager)):
    bots_status = []
    for uin, bot in manager.active_bots.items():
        bots_status.append(BotStatus(
            uin=uin,
            connected=bool(bot.imtoken),
            events=list(bot.subscribed_events)
        ))

    return SystemStatus(
        active_bots_count=len(manager.active_bots),
        bots=bots_status
    )
