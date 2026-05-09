"""Timeline Reconstruction Agent"""
from app.ai.openclaw.agent_runner import run_agent

PROMPT = """You are a forensic timeline reconstruction AI agent. Given events, your job is to:
- Reconstruct the chronological sequence of the incident
- Identify gaps in the timeline
- Detect anomalies
- Suggest what likely happened during unknown periods
- Calculate time between critical events
Present the timeline in chronological order with timestamps."""


def reconstruct_timeline(case_id: str, events: list) -> str:
    context = f"Case ID: {case_id}\n\nRaw Events:\n"
    for event in sorted(events, key=lambda x: x.get("timestamp", 0)):
        context += f"- [{event.get('timestamp', 'N/A')}] {event.get('event_type', '')}: {event.get('description', '')}\n"
    return run_agent("timeline_agent", PROMPT, context)
