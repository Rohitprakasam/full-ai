import io
from minio import Minio
from app.config import settings

minio_client = Minio(
    settings.MINIO_URL,
    access_key=settings.MINIO_ACCESS_KEY,
    secret_key=settings.MINIO_SECRET_KEY,
    secure=settings.MINIO_SECURE
)

def get_minio_client():
    return minio_client

def ensure_bucket(bucket_name: str):
    if not minio_client.bucket_exists(bucket_name):
        minio_client.make_bucket(bucket_name)

def upload_file(bucket_name: str, object_name: str, data: bytes, content_type: str = "application/octet-stream"):
    ensure_bucket(bucket_name)
    minio_client.put_object(
        bucket_name,
        object_name,
        data=io.BytesIO(data),
        length=len(data),
        content_type=content_type
    )
