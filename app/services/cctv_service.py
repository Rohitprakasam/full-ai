"""CCTV Analytics Service — YOLOv8 + DeepSORT video analysis. Runs locally."""
import cv2
from ultralytics import YOLO
from deep_sort_realtime.deepsort_tracker import DeepSort
from collections import defaultdict

model = YOLO("yolov8n.pt")
tracker = DeepSort(max_age=30)


def analyze_video(video_path: str, case_id: str) -> list:
    """Run YOLO detection + DeepSORT tracking on a video file."""
    cap = cv2.VideoCapture(video_path)
    fps = cap.get(cv2.CAP_PROP_FPS) or 30.0
    events = []
    frame_count = 0

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
        if frame_count % 10 == 0:
            results = model(frame, verbose=False)
            detections = []
            for r in results:
                for box in r.boxes:
                    x1, y1, x2, y2 = map(int, box.xyxy[0])
                    conf = float(box.conf[0])
                    cls = int(box.cls[0])
                    label = model.names[cls]
                    if conf > 0.4:
                        detections.append(([x1, y1, x2 - x1, y2 - y1], conf, label))

            tracks = tracker.update_tracks(detections, frame=frame)
            timestamp_sec = frame_count / fps
            for track in tracks:
                if track.is_confirmed():
                    events.append({
                        "timestamp": round(timestamp_sec, 2),
                        "track_id": track.track_id,
                        "class": track.det_class,
                        "bbox": track.to_ltrb().tolist(),
                        "case_id": case_id
                    })
        frame_count += 1

    cap.release()
    return events


def detect_suspicious_activity(events: list) -> list:
    """Detect loitering and other suspicious patterns."""
    flags = []
    person_appearances = defaultdict(list)
    for event in events:
        if event["class"] == "person":
            person_appearances[event["track_id"]].append(event["timestamp"])

    for track_id, timestamps in person_appearances.items():
        if len(timestamps) > 20:
            flags.append({
                "type": "loitering",
                "track_id": track_id,
                "duration_seconds": round(max(timestamps) - min(timestamps), 2),
                "severity": "medium"
            })
    return flags


def get_video_summary(events: list) -> dict:
    unique_persons = set()
    unique_objects = set()
    for event in events:
        if event["class"] == "person":
            unique_persons.add(event["track_id"])
        else:
            unique_objects.add(event["class"])
    return {
        "total_events": len(events),
        "unique_persons": len(unique_persons),
        "unique_object_types": list(unique_objects),
        "duration_seconds": max(e["timestamp"] for e in events) if events else 0
    }
