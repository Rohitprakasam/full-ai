"""Legal Report Agent — Court-ready investigation reports."""
from app.ai.openclaw.agent_runner import run_agent

PROMPT = """You are a forensic legal report generation AI agent.
Generate a structured investigation report with sections:
1. Case Summary  2. Evidence Overview  3. Suspect Analysis
4. Timeline of Events  5. Key Findings  6. Recommended Next Steps
7. Confidence Assessment (Low / Medium / High)
Use formal, precise language. Do not speculate. Cite evidence."""


def generate_legal_report(case_data: dict) -> str:
    context = (f"Case ID: {case_data.get('case_id', 'N/A')}\n"
               f"Crime Type: {case_data.get('crime_type', 'N/A')}\n"
               f"Suspects: {', '.join(case_data.get('suspects', []))}\n"
               f"Evidence Count: {len(case_data.get('evidence', []))}\n"
               f"Risk Score: {case_data.get('risk_score', 'N/A')}\n")
    return run_agent("legal_agent", PROMPT, context)
