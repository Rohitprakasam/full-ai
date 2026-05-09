"""
Unified Featherless AI LLM Client — replaces all Ollama calls.
OpenAI-compatible API for chat, embeddings, and tool calling.
"""
from openai import OpenAI
from app.config import settings, MODELS

client = OpenAI(
    base_url=settings.FEATHERLESS_BASE_URL,
    api_key=settings.FEATHERLESS_API_KEY
)


def chat_completion(messages: list, model: str = None, temperature: float = 0.3, max_tokens: int = 2048) -> str:
    """Universal LLM call via Featherless AI."""
    try:
        response = client.chat.completions.create(
            model=model or MODELS["primary"],
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens
        )
        return response.choices[0].message.content or ""
    except Exception as e:
        print(f"[LLM Error] {e}")
        return f"LLM request failed: {str(e)}"


def generate_embeddings(text: str) -> list:
    """Generate embeddings via Featherless API (Qwen3-Embedding-8B)."""
    try:
        response = client.embeddings.create(
            model=MODELS["embedding"],
            input=text[:8000]
        )
        return response.data[0].embedding
    except Exception as e:
        print(f"[Embedding Error] {e}")
        return []


def generate_embeddings_batch(texts: list) -> list:
    """Batch embedding generation."""
    try:
        response = client.embeddings.create(
            model=MODELS["embedding"],
            input=[t[:8000] for t in texts]
        )
        return [item.embedding for item in response.data]
    except Exception as e:
        print(f"[Batch Embedding Error] {e}")
        return []


def chat_completion_with_tools(messages: list, tools: list, model: str = None) -> dict:
    """Tool-calling via Qwen3 native support."""
    try:
        response = client.chat.completions.create(
            model=model or MODELS["primary"],
            messages=messages,
            tools=tools,
            max_tokens=4096
        )
        return response.choices[0].message
    except Exception as e:
        print(f"[Tool Calling Error] {e}")
        return {"content": f"Tool calling failed: {str(e)}"}
