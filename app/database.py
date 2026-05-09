from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie
from app.config import settings

async def init_db():
    client = AsyncIOMotorClient(settings.MONGO_URL)
    database = client[settings.MONGO_DB]

    from app.models.user import User
    from app.models.case import Case
    from app.models.evidence import Evidence
    from app.models.timeline import TimelineEvent
    from app.models.audit import AuditLog

    await init_beanie(
        database=database,
        document_models=[User, Case, Evidence, TimelineEvent, AuditLog]
    )
