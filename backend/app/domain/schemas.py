from pydantic import BaseModel, Field
from typing import Dict, Any, Optional
from uuid import UUID

class UserLogin(BaseModel):
    username: str = Field(..., min_length=1)
    password: str = Field(..., min_length=4)

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    user_id: Optional[str] = None

class ConnectionConfigCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    platform: str = Field("snowflake", max_length=50)
    config: Dict[str, Any] # Dictionary containing credentials (username, password/key, warehouse, database, etc.)

class ConnectionConfigResponse(BaseModel):
    id: UUID
    name: str
    platform: str

    class Config:
        from_attributes = True

class ConnectionTestRequest(BaseModel):
    platform: str = Field("snowflake", max_length=50)
    config: Dict[str, Any]
