from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "RAW — AI-Powered Unified Investigation OS"
    API_V1_STR: str = "/api/v1"

    # MongoDB (Person 1)
    MONGO_URL: str = "mongodb://127.0.0.1:27017"
    MONGO_DB: str = "investigation_os"

    # MinIO File Storage (Person 1)
    MINIO_URL: str = "127.0.0.1:9000"
    MINIO_ACCESS_KEY: str = "minioadmin"
    MINIO_SECRET_KEY: str = "minioadmin"
    MINIO_SECURE: bool = False

    # Redis (Shared)
    REDIS_URL: str = "redis://127.0.0.1:6379/0"

    # JWT Auth (Person 1)
    SECRET_KEY: str = "super_secret_key_for_jwt_auth_change_in_production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days

    # Featherless AI (Person 2)
    FEATHERLESS_API_KEY: str = "rc_b6cb34a0e41abcd2266da87e740d1ec579d172e3412d675051b0bd1b73bac7c1"
    FEATHERLESS_BASE_URL: str = "https://api.featherless.ai/v1"
    LLM_MODEL_PRIMARY: str = "Qwen/Qwen3-32B"
    LLM_MODEL_FAST: str = "Qwen/Qwen2.5-7B-Instruct"
    LLM_MODEL_EMBEDDING: str = "Qwen/Qwen3-Embedding-8B"
    LLM_MODEL_AGENT: str = "NousResearch/Hermes-3-Llama-3.1-8B"

    # Neo4j (Person 2)
    NEO4J_URI: str = "bolt://127.0.0.1:7687"
    NEO4J_USER: str = "neo4j"
    NEO4J_PASSWORD: str = "investigation123"

    # Milvus (Person 2)
    MILVUS_HOST: str = "127.0.0.1"
    MILVUS_PORT: int = 19530

    # Upload directory
    UPLOAD_DIR: str = "./uploads"

    class Config:
        env_file = ".env"

settings = Settings()

# Model shortcuts for AI services
MODELS = {
    "primary": settings.LLM_MODEL_PRIMARY,
    "fast": settings.LLM_MODEL_FAST,
    "embedding": settings.LLM_MODEL_EMBEDDING,
    "agent": settings.LLM_MODEL_AGENT,
}
