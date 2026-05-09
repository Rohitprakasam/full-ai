"""MFA Service — TOTP (Google Authenticator compatible)."""
import pyotp
import qrcode
import io
import base64


def generate_mfa_secret() -> str:
    return pyotp.random_base32()


def generate_qr_code(email: str, secret: str, issuer: str = "RAW Investigation OS") -> str:
    totp_uri = pyotp.totp.TOTP(secret).provisioning_uri(name=email, issuer_name=issuer)
    qr = qrcode.make(totp_uri)
    buffer = io.BytesIO()
    qr.save(buffer, format="PNG")
    buffer.seek(0)
    return base64.b64encode(buffer.read()).decode()


def verify_totp(secret: str, code: str) -> bool:
    totp = pyotp.TOTP(secret)
    return totp.verify(code, valid_window=1)
