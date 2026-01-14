from fastapi import APIRouter, HTTPException, Depends
from app.models.schemas import BotLoginRequest, MessageRequest, BotStatus
from app.core.bot_manager import BotManager
from app.dependencies import get_bot_manager

router = APIRouter(prefix="/bot", tags=["bots"])

@router.post("/{uin}/login")
async def bot_login(uin: int, req: BotLoginRequest, manager: BotManager = Depends(get_bot_manager)):
    try:
        await manager.start_bot(uin, req.password, req.events, req.settings)
        return {"status": "connecting", "uin": uin}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=str(e))

@router.post("/{uin}/logout")
async def bot_logout(uin: int, manager: BotManager = Depends(get_bot_manager)):
    success = await manager.stop_bot(uin)
    if not success:
        raise HTTPException(status_code=404, detail="Bot not found")
    return {"status": "disconnected", "uin": uin}

@router.post("/{uin}/message")
async def send_message(uin: int, req: MessageRequest, manager: BotManager = Depends(get_bot_manager)):
    bot = manager.get_bot(uin)
    if not bot:
        raise HTTPException(status_code=404, detail="Bot not connected")
    
    if not bot.imtoken:
         raise HTTPException(status_code=503, detail="Bot not authenticated yet")
         
    await bot.send_message(req.recipient, req.content)
    return {"status": "sent", "from": uin, "to": req.recipient}

@router.post("/{uin}/roulette")
async def start_roulette(uin: int, manager: BotManager = Depends(get_bot_manager)):
    bot = manager.get_bot(uin)
    if not bot:
        raise HTTPException(status_code=404, detail="Bot not connected")
        
    try:
        result = await bot.start_roulette()
        return {"status": "started", "api_response": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{uin}", response_model=BotStatus)
async def get_bot_status(uin: int, manager: BotManager = Depends(get_bot_manager)):
    bot = manager.get_bot(uin)
    if not bot:
        raise HTTPException(status_code=404, detail="Bot not connected")
    
    return BotStatus(
        uin=uin,
        connected=bool(bot.imtoken),
        events=list(bot.subscribed_events)
    )
