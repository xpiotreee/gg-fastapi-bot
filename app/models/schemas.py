from pydantic import BaseModel
from typing import List, Optional, Dict, Any

class BotLoginRequest(BaseModel):
    uin: int
    password: str
    events: List[str] = ["message", "roulette", "system"] 
    settings: Optional[Dict[str, Any]] = None 

class BotActionRequest(BaseModel):
    uin: int

class MessageRequest(BaseModel):
    uin: int
    recipient: int
    content: str

class BotStatus(BaseModel):
    uin: int
    connected: bool
    events: List[str]

class SystemStatus(BaseModel):
    active_bots_count: int
    bots: List[BotStatus]
