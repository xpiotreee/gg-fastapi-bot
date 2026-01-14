from fastapi import APIRouter, HTTPException, Depends
from app.models.schemas import BotLoginRequest, BotActionRequest, MessageRequest
from app.core.bot_manager import BotManager
from app.dependencies import get_bot_manager

router = APIRouter(prefix="/bot", tags=["bots"])

@router.post("/login")
async def bot_login(req: BotLoginRequest, manager: BotManager = Depends(get_bot_manager)):
    try:
        await manager.start_bot(req.uin, req.password, req.events, req.settings)
        return {"status": "connecting", "uin": req.uin}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=str(e))

@router.post("/logout")
async def bot_logout(req: BotActionRequest, manager: BotManager = Depends(get_bot_manager)):
    success = await manager.stop_bot(req.uin)
    if not success:
        raise HTTPException(status_code=404, detail="Bot not found")
    return {"status": "disconnected", "uin": req.uin}

@router.post("/send")
async def send_message(req: MessageRequest, manager: BotManager = Depends(get_bot_manager)):
    bot = manager.get_bot(req.uin)
    if not bot:
        raise HTTPException(status_code=404, detail="Bot not connected")
    
    if not bot.imtoken:
         raise HTTPException(status_code=503, detail="Bot not authenticated yet")
         
    await bot.send_message(req.recipient, req.content)
    return {"status": "sent", "from": req.uin, "to": req.recipient}

@router.post("/roulette/start")
async def start_roulette(req: BotActionRequest, manager: BotManager = Depends(get_bot_manager)):
    bot = manager.get_bot(req.uin)
    if not bot:
        raise HTTPException(status_code=404, detail="Bot not connected")
        
    try:
        result = await bot.start_roulette()
        return {"status": "started", "api_response": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
