"""Investigation Copilot — Streaming + non-streaming conversational AI."""
from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from app.services.llm_client import stream_chat_completion, chat_completion
from app.models.case import Case
from app.models.evidence import Evidence
from app.models.timeline import TimelineEvent
from beanie import PydanticObjectId
import json

router = APIRouter(prefix="/copilot", tags=["Investigation Copilot"])


class CopilotQuery(BaseModel):
    case_id: str
    question: str
    conversation_history: list = []


@router.post("/ask")
async def ask_copilot(query: CopilotQuery):
    """Streaming copilot — tokens arrive in real time via SSE."""
    case_context = await _build_case_context(query.case_id)
    messages = _build_messages(case_context, query)

    async def token_stream():
        async for token in stream_chat_completion(messages):
            yield f"data: {json.dumps({'token': token})}\n\n"
        yield "data: [DONE]\n\n"

    return StreamingResponse(
        token_stream(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"}
    )


@router.post("/ask/full")
async def ask_copilot_full(query: CopilotQuery):
    """Non-streaming fallback — returns complete response."""
    case_context = await _build_case_context(query.case_id)
    messages = _build_messages(case_context, query)
    answer = chat_completion(messages)
    return {"answer": answer, "case_id": query.case_id}


def _build_messages(case_context: str, query: CopilotQuery) -> list:
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
    return messages


async def _build_case_context(case_id: str) -> str:
    try:
        case = await Case.get(PydanticObjectId(case_id))
        if not case:
            return f"Case {case_id} not found."
        evidence_list = await Evidence.find(Evidence.case_id == PydanticObjectId(case_id)).to_list()
        timeline_events = await TimelineEvent.find(TimelineEvent.case_id == PydanticObjectId(case_id)).sort("timestamp").to_list()

        ctx = f"Case: {case.title} | Crime: {case.crime_type} | Status: {case.status}\n"
        ctx += f"Risk Level: {case.ai_risk_level or 'Not assessed'} (Score: {case.risk_score})\n"
        ctx += f"Evidence items: {len(evidence_list)} | Timeline events: {len(timeline_events)}\n\n"

        ctx += "EVIDENCE:\n"
        for ev in evidence_list[:8]:
            ctx += f"- [{ev.type}] {(ev.ai_summary or 'Not analyzed')[:200]}\n"
            if ev.ai_entities:
                ctx += f"  Entities: {ev.ai_entities}\n"

        if timeline_events:
            ctx += "\nTIMELINE:\n"
            for te in timeline_events[:10]:
                ctx += f"- [{te.timestamp}] {te.event_type}: {te.description or ''}\n"

        if case.ai_risk_flags:
            ctx += f"\nRISK FLAGS: {', '.join(case.ai_risk_flags)}\n"

        return ctx
    except Exception as e:
        return f"Error building context: {str(e)}"
