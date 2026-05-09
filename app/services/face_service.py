"""Face Recognition Service — DeepFace for suspect identification in CCTV."""
import cv2
import numpy as np
from pathlib import Path
import os

SUSPECT_FACE_DB = "./uploads/suspect_faces"


def ensure_face_db():
    Path(SUSPECT_FACE_DB).mkdir(parents=True, exist_ok=True)


def register_suspect_face(suspect_name: str, image_path: str) -> str:
    ensure_face_db()
    dest = os.path.join(SUSPECT_FACE_DB, f"{suspect_name}.jpg")
    img = cv2.imread(image_path)
    cv2.imwrite(dest, img)
    return dest


def identify_face_in_frame(frame: np.ndarray) -> list:
    ensure_face_db()
    if not os.listdir(SUSPECT_FACE_DB):
        return []
    try:
        from deepface import DeepFace
        results = DeepFace.find(
            img_path=frame, db_path=SUSPECT_FACE_DB,
            model_name="Facenet512", detector_backend="retinaface",
            enforce_detection=False, silent=True
        )
        matches = []
        for df in results:
            if not df.empty:
                top = df.iloc[0]
                confidence = max(0, round((1 - top["distance"]) * 100, 1))
                if confidence > 60:
                    matches.append({
                        "suspect": Path(top["identity"]).stem,
                        "confidence": confidence,
                        "source_x": int(top.get("source_x", 0)),
                        "source_y": int(top.get("source_y", 0)),
                    })
        return matches
    except Exception:
        return []
