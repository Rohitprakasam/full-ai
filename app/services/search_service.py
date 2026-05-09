"""Semantic Search — Milvus + Featherless AI embeddings."""
from pymilvus import connections, Collection, CollectionSchema, FieldSchema, DataType, utility
from app.services.llm_client import generate_embeddings
from app.config import settings

COLLECTION_NAME = "evidence_embeddings"
EMBEDDING_DIM = 4096  # Qwen3-Embedding-8B dimension
_connected = False


def _ensure_connection():
    global _connected
    if not _connected:
        connections.connect("default", host=settings.MILVUS_HOST, port=str(settings.MILVUS_PORT))
        _connected = True


def init_milvus():
    _ensure_connection()
    if not utility.has_collection(COLLECTION_NAME):
        fields = [
            FieldSchema(name="id", dtype=DataType.INT64, is_primary=True, auto_id=True),
            FieldSchema(name="evidence_id", dtype=DataType.VARCHAR, max_length=100),
            FieldSchema(name="case_id", dtype=DataType.VARCHAR, max_length=100),
            FieldSchema(name="summary", dtype=DataType.VARCHAR, max_length=2000),
            FieldSchema(name="embedding", dtype=DataType.FLOAT_VECTOR, dim=EMBEDDING_DIM),
        ]
        schema = CollectionSchema(fields, description="Evidence embeddings for semantic search")
        collection = Collection(COLLECTION_NAME, schema)
        collection.create_index("embedding", {
            "index_type": "IVF_FLAT", "metric_type": "COSINE", "params": {"nlist": 128}
        })
    return Collection(COLLECTION_NAME)


def store_embedding(evidence_id: str, embedding: list, metadata: dict):
    collection = init_milvus()
    collection.insert([
        [evidence_id], [metadata.get("case_id", "")],
        [metadata.get("summary", "")[:2000]], [embedding]
    ])
    collection.flush()


def semantic_search(query: str, case_id: str = None, top_k: int = 5) -> list:
    query_embedding = generate_embeddings(query)
    if not query_embedding:
        return []
    collection = init_milvus()
    collection.load()
    search_params = {"metric_type": "COSINE", "params": {"nprobe": 10}}
    expr = f'case_id == "{case_id}"' if case_id else None
    results = collection.search(
        data=[query_embedding], anns_field="embedding", param=search_params,
        limit=top_k, expr=expr, output_fields=["evidence_id", "summary"]
    )
    return [
        {"evidence_id": r.entity.get("evidence_id"), "summary": r.entity.get("summary"),
         "relevance_score": round(r.score, 4)}
        for r in results[0]
    ]
