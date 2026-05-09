"""CCTV Surveillance Agent — AI reasoning over CCTV detection events."""
from app.ai.openclaw.agent_runner import run_agent

PROMPT = """You are a forensic CCTV surveillance analysis AI agent.
Given CCTV detection events (person tracking, object detection, movement patterns), your job is to:
- Identify suspicious individuals based on movement patterns
- Detect loitering, tailing, or evasive behavior
- Correlate person appearances across multiple camera feeds
- Flag anomalous activity (unusual time, unauthorized area, suspicious objects)
- Recommend which footage segments need human review

Present findings with track IDs, timestamps, and confidence levels."""


def analyze_cctv(case_id: str, events: list, flags: list = None) -> str:
    context = f"Case ID: {case_id}\n\nCCTV Detection Events ({len(events)} total):\n"
    for event in events[:50]:
        context += f"- [T={event.get('timestamp', 'N/A')}s] Track {event.get('track_id', '?')}: {event.get('class', 'unknown')} at {event.get('bbox', [])}\n"

    if flags:
        context += f"\nSuspicious Activity Flags ({len(flags)}):\n"
        for flag in flags:
            context += f"- {flag.get('type', '')}: Track {flag.get('track_id', '?')} — {flag.get('duration_seconds', 0)}s duration, severity={flag.get('severity', 'N/A')}\n"

    return run_agent("cctv_agent", PROMPT, context)
