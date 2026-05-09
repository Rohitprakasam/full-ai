from datetime import timedelta
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel
from app.models.user import User
from app.models.audit import AuditLog
from app.schemas.user import UserCreate, UserOut, Token
from app.utils.security import get_password_hash, verify_password, create_access_token, get_current_user
from app.config import settings

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", response_model=UserOut)
async def register(user_in: UserCreate):
    user = await User.find_one(User.email == user_in.email)
    if user:
        raise HTTPException(status_code=400, detail="Email already exists in the system.")
    user = User(
        name=user_in.name, email=user_in.email,
        password_hash=get_password_hash(user_in.password), role=user_in.role
    )
    await user.insert()
    return user


@router.post("/login", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = await User.find_one(User.email == form_data.username)
    if not user or not verify_password(form_data.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Incorrect email or password")

    # MFA check
    if user.mfa_enabled:
        from app.services.mfa_service import verify_totp
        mfa_code = form_data.scopes[0] if form_data.scopes else None
        if not mfa_code:
            raise HTTPException(status_code=202, detail="MFA_REQUIRED")
        if not verify_totp(user.mfa_secret, mfa_code):
            raise HTTPException(status_code=401, detail="Invalid MFA code.")

    token = create_access_token(subject=user.email)
    return {"access_token": token, "token_type": "bearer"}


@router.post("/logout")
async def logout(current_user: User = Depends(get_current_user)):
    return {"message": "Logged out successfully", "note": "Please discard your JWT token on the client side."}


# --- MFA Endpoints ---

class MFASetupResponse(BaseModel):
    secret: str
    qr_code: str

class MFAVerifyRequest(BaseModel):
    code: str


@router.post("/mfa/setup", response_model=MFASetupResponse)
async def setup_mfa(current_user: User = Depends(get_current_user)):
    from app.services.mfa_service import generate_mfa_secret, generate_qr_code
    secret = generate_mfa_secret()
    qr = generate_qr_code(current_user.email, secret)
    current_user.mfa_secret = secret
    await current_user.save()
    return MFASetupResponse(secret=secret, qr_code=qr)


@router.post("/mfa/verify")
async def verify_mfa_setup(req: MFAVerifyRequest, current_user: User = Depends(get_current_user)):
    from app.services.mfa_service import verify_totp
    if not current_user.mfa_secret:
        raise HTTPException(400, "MFA setup not started. Call /mfa/setup first.")
    if not verify_totp(current_user.mfa_secret, req.code):
        raise HTTPException(400, "Invalid code.")
    current_user.mfa_enabled = True
    await current_user.save()
    return {"message": "MFA enabled successfully."}


@router.post("/mfa/disable")
async def disable_mfa(req: MFAVerifyRequest, current_user: User = Depends(get_current_user)):
    from app.services.mfa_service import verify_totp
    if not current_user.mfa_enabled:
        raise HTTPException(400, "MFA is not enabled.")
    if not verify_totp(current_user.mfa_secret, req.code):
        raise HTTPException(400, "Invalid code.")
    current_user.mfa_enabled = False
    current_user.mfa_secret = None
    await current_user.save()
    return {"message": "MFA disabled."}


# --- Audit Logs ---

@router.get("/audit-logs")
async def get_audit_logs(limit: int = 50, current_user: User = Depends(get_current_user)):
    logs = await AuditLog.find_all().sort("-timestamp").limit(limit).to_list()
    return logs
