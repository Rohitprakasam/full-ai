"""Metadata Extraction Service — Extract file metadata and forensic attributes."""
import os
import hashlib
from datetime import datetime


def extract_metadata(file_path: str) -> dict:
    """
    Extract metadata from a file for forensic indexing.

    Returns:
        Dict with file size, timestamps, hash, type, etc.
    """
    stat = os.stat(file_path)
    ext = os.path.splitext(file_path)[1].lower()

    # Read file for hashing
    with open(file_path, "rb") as f:
        content = f.read()
        sha256 = hashlib.sha256(content).hexdigest()
        md5 = hashlib.md5(content).hexdigest()

    return {
        "filename": os.path.basename(file_path),
        "extension": ext,
        "size_bytes": stat.st_size,
        "sha256": sha256,
        "md5": md5,
        "created_at": datetime.fromtimestamp(stat.st_ctime).isoformat(),
        "modified_at": datetime.fromtimestamp(stat.st_mtime).isoformat(),
        "mime_type": _get_mime_type(ext),
    }


def extract_image_metadata(file_path: str) -> dict:
    """Extract EXIF metadata from images (GPS, camera, timestamp)."""
    try:
        from PIL import Image
        from PIL.ExifTags import TAGS

        img = Image.open(file_path)
        exif_data = img._getexif()
        if not exif_data:
            return {}

        metadata = {}
        for tag_id, value in exif_data.items():
            tag = TAGS.get(tag_id, tag_id)
            if isinstance(value, bytes):
                continue  # Skip binary data
            metadata[str(tag)] = str(value)
        return metadata
    except Exception:
        return {}


def _get_mime_type(ext: str) -> str:
    mime_map = {
        ".jpg": "image/jpeg", ".jpeg": "image/jpeg", ".png": "image/png",
        ".pdf": "application/pdf", ".doc": "application/msword",
        ".docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        ".mp4": "video/mp4", ".avi": "video/x-msvideo",
        ".wav": "audio/wav", ".mp3": "audio/mpeg",
    }
    return mime_map.get(ext, "application/octet-stream")
