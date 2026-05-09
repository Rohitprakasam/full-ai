"""Audit Log Middleware — Records every mutating action to MongoDB."""
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from app.models.audit import AuditLog
from app.utils.security import get_current_user_from_request
from datetime import datetime, timezone

SKIP_PATHS = {"/health", "/", "/api/v1/auth/login", "/docs", "/openapi.json", "/redoc"}
AUDIT_METHODS = {"POST", "PUT", "DELETE", "PATCH"}


class AuditMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        if (
            request.method in AUDIT_METHODS
            and request.url.path not in SKIP_PATHS
            and response.status_code < 400
        ):
            user_id = await get_current_user_from_request(request)
            if user_id:
                try:
                    log = AuditLog(
                        user_id=user_id,
                        action=f"{request.method} {request.url.path}",
                        resource=request.url.path,
                        timestamp=datetime.now(timezone.utc),
                    )
                    await log.insert()
                except Exception:
                    pass  # Never let audit failure break the request
        return response
