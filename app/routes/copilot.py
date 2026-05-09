"""Investigation Copilot — Conversational AI for investigators.
Fetches real case data from MongoDB (Person 1) and reasons over it with Featherless AI (Person 2)."""
from fastapi import APIRouter
from pydantic import BaseModel
from app.services.llm_client import chat_completion
from app.config import MODELS
from app.models.case import Case
from app.models.evidence import Evidence
from app.models.timeline import TimelineEvent
from beanie import PydanticObjectId

router = APIRouter(prefix="/copilot", tags=["Investigation Copilot"])


class CopilotQuery(BaseModel):
    case_id: str
    question: str
    conversation_history: list = []


@router.post("/ask")
async def ask_copilot(query: CopilotQuery):
    case_context = await _build_case_context(query.case_id)

    messages = [
        {"role": "system", "content": f"""You are RAW — an AI-powered forensic investigation copilot.
You have full access to the case intelligence below. Answer the investigator's question
concisely and accurately. If you do not have enough data, say so honestly. Never fabricate facts.

CASE INTELLIGENCE:
{case_context}"""}
    ]

    for msg in query.conversation_history[-6:]:
        messages.append({"role": "user", "content": msg.get("question", "")})
        messages.append({"role": "assistant", "content": msg.get("answer", "")})

    messages.append({"role": "user", "content": query.question})

    answer = chat_completion(messages, model=MODELS["fast"])
    return {"answer": answer, "case_id": query.case_id}


async def _build_case_context(case_id: str) -> str:
    """Build context directly from MongoDB — no inter-service HTTP calls needed."""
    try:
        case = await Case.get(PydanticObjectId(case_id))
        if not case:
            return f"Case {case_id} not found in database."

        evidence_list = await Evidence.find(Evidence.case_id == PydanticObjectId(case_id)).to_list()
        timeline_events = await TimelineEvent.find(TimelineEvent.case_id == PydanticObjectId(case_id)).sort("timestamp").to_list()

        context = f"Case: {case.title} | Crime: {case.crime_type} | Status: {case.status}\n"
        context += f"Risk Score: {case.risk_score} | Risk Level: {case.ai_risk_level or 'N/A'}\n"
        context += f"Evidence items: {len(evidence_list)}\nTimeline events: {len(timeline_events)}\n\n"

        context += "EVIDENCE:\n"
        for ev in evidence_list[:10]:
            context += f"- [{ev.type}] Summary: {ev.ai_summary or 'Not yet analyzed'}\n"
            if ev.ai_entities:
                context += f"  Entities: {ev.ai_entities}\n"

        context += "\nTIMELINE:\n"
        for te in timeline_events[:15]:
            context += f"- [{te.timestamp}] {te.event_type}: {te.description or ''}\n"

        return context
    except Exception as e:
        return f"Error building context: {str(e)}"
