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

class UserProfile(BaseModel):
    uin: int
    gender: Optional[str]
    label: Optional[str]
    city: Optional[str]
    age: Optional[str]
    description: Optional[str]
    about: Optional[str]
    avatar_url: Optional[str]
    gallery: List[str] = []
    status: Optional[int] = None

class SystemStatus(BaseModel):
    active_bots_count: int
    bots: List[BotStatus]
