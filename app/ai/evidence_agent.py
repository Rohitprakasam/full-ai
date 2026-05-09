"""Evidence Analysis Agent"""
from app.ai.openclaw.agent_runner import run_agent

PROMPT = """You are a forensic evidence analysis AI agent. Analyze collected evidence and identify:
- Key facts established by the evidence
- Inconsistencies or contradictions
- Missing evidence that should be collected
- Connections between pieces of evidence
- Priority evidence for prosecution
Structure your output clearly. Never speculate beyond what evidence supports."""


def analyze_evidence(case_id: str, evidence_summaries: list) -> str:
    context = f"Case ID: {case_id}\n\nEvidence Summaries:\n"
    for i, ev in enumerate(evidence_summaries, 1):
        context += f"\n[{i}] Type: {ev.get('type', 'unknown')}\nSummary: {ev.get('summary', 'N/A')}\n"
    return run_agent("evidence_agent", PROMPT, context)
