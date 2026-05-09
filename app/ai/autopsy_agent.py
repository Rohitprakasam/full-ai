"""Autopsy Intelligence Agent — AI reasoning over medical/forensic autopsy reports."""
from app.ai.openclaw.agent_runner import run_agent

PROMPT = """You are a forensic autopsy intelligence AI agent.
Given autopsy report data, your job is to:
- Extract injury descriptions and classify them (blunt force, sharp force, gunshot, chemical, etc.)
- Identify toxicology findings and their significance
- Determine probable cause of death and mechanism
- Analyze organ damage patterns
- Flag inconsistencies between claimed cause of death and evidence
- Provide a medical-forensic opinion with confidence level

Use precise medical terminology. Reference evidence directly. Do not speculate beyond the data."""


def analyze_autopsy(case_id: str, report_text: str) -> str:
    context = f"Case ID: {case_id}\n\nAutopsy / Medical Forensic Report:\n{report_text[:6000]}"
    return run_agent("autopsy_agent", PROMPT, context)
