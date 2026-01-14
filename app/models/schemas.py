from pydantic import BaseModel
from typing import List, Optional, Dict, Any

class BotLoginRequest(BaseModel):
    password: str
    events: List[str] = ["message", "roulette", "system", "status", "typing"] 
    settings: Optional[Dict[str, Any]] = None 

class MessageRequest(BaseModel):
    recipient: int
    content: str

class BotStatus(BaseModel):
    uin: int
    connected: bool
    events: List[str]

class SystemStatus(BaseModel):
    active_bots_count: int
    bots: List[BotStatus]
