from pydantic import BaseModel, EmailStr
from beanie import PydanticObjectId

class UserCreate(BaseModel):
    name: str
    email: EmailStr
    password: str
    role: str = "officer"

class UserOut(BaseModel):
    id: PydanticObjectId
    name: str
    email: EmailStr
    role: str

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: str | None = None
