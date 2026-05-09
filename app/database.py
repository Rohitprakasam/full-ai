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

    # FIX 4: Create MongoDB text indexes for keyword search
    await database["evidence"].create_index(
        [("ai_summary", "text"), ("ai_raw_text", "text"), ("type", "text")],
        name="evidence_text_search",
        weights={"ai_summary": 10, "type": 5, "ai_raw_text": 1}
    )
    await database["cases"].create_index(
        [("title", "text"), ("crime_type", "text")],
        name="case_text_search"
    )
