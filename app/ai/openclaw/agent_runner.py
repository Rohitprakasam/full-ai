"""OpenClaw Agent Runner — Featherless AI powered agent execution."""
from app.services.llm_client import chat_completion, chat_completion_with_tools
from app.config import MODELS


def run_agent(agent_name: str, system_prompt: str, context: str, model: str = None) -> str:
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": f"CASE CONTEXT:\n{context}\n\nProvide your structured forensic analysis. Be specific, factual, and actionable."}
    ]
    return chat_completion(messages, model=model or MODELS["primary"])


def run_agent_with_tools(agent_name: str, system_prompt: str, context: str, tools: list) -> dict:
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": context}
    ]
    return chat_completion_with_tools(messages, tools, model=MODELS["primary"])
