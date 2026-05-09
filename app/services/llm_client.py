"""
Unified Featherless AI LLM Client — replaces all Ollama calls.
OpenAI-compatible API for chat, embeddings, tool calling, and streaming.
"""
from openai import OpenAI, AsyncOpenAI
from app.config import settings, MODELS

# Sync client (for Celery workers and regular calls)
client = OpenAI(
    base_url=settings.FEATHERLESS_BASE_URL,
    api_key=settings.FEATHERLESS_API_KEY
)

# Async client (for streaming copilot)
async_client = AsyncOpenAI(
    base_url=settings.FEATHERLESS_BASE_URL,
    api_key=settings.FEATHERLESS_API_KEY
)


def chat_completion(messages: list, model: str = None, temperature: float = 0.3, max_tokens: int = 2048) -> str:
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


async def stream_chat_completion(messages: list, model: str = None):
    """Async generator that yields text chunks as they arrive. Use with StreamingResponse."""
    try:
        stream = await async_client.chat.completions.create(
            model=model or MODELS["primary"],
            messages=messages,
            max_tokens=2048,
            temperature=0.3,
            stream=True,
        )
        async for chunk in stream:
            delta = chunk.choices[0].delta.content
            if delta:
                yield delta
    except Exception as e:
        yield f"[Stream Error] {str(e)}"


def generate_embeddings(text: str) -> list:
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
