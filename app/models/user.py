from typing import Optional
from beanie import Document
from pydantic import EmailStr

class User(Document):
    name: str
    role: str = "officer"
    email: EmailStr
    password_hash: str
    # MFA fields
    mfa_enabled: bool = False
    mfa_secret: Optional[str] = None

    class Settings:
        name = "users"
