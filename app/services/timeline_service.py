"""Timeline Reconstruction Service — Aggregates events from all sources into a unified timeline."""
from datetime import datetime


def merge_timelines(cctv_events: list, db_events: list, nlp_dates: list = None) -> list:
    """
    Merge events from different sources into one unified timeline.

    Args:
        cctv_events: Events from CCTV analysis
        db_events: Timeline events from MongoDB
        nlp_dates: Dates extracted from evidence text by NLP

    Returns:
        Sorted list of unified timeline events
    """
    unified = []

    for event in db_events:
        unified.append({
            "source": "database",
            "timestamp": event.get("timestamp"),
            "event_type": event.get("event_type", ""),
            "description": event.get("description", ""),
            "confidence": event.get("confidence_score", 1.0),
        })

    for event in cctv_events:
        unified.append({
            "source": "cctv",
            "timestamp": event.get("timestamp"),
            "event_type": f"CCTV: {event.get('class', 'detection')}",
            "description": f"Track {event.get('track_id', '?')} detected",
            "confidence": 0.8,
        })

    if nlp_dates:
        for date_str in nlp_dates:
            unified.append({
                "source": "nlp_extraction",
                "timestamp": date_str,
                "event_type": "document_date",
                "description": f"Date mentioned in evidence: {date_str}",
                "confidence": 0.6,
            })

    # Sort by timestamp (handle mixed types)
    def _sort_key(event):
        ts = event.get("timestamp")
        if isinstance(ts, (int, float)):
            return ts
        if isinstance(ts, datetime):
            return ts.timestamp()
        return 0

    unified.sort(key=_sort_key)
    return unified


def detect_timeline_gaps(events: list, gap_threshold_seconds: float = 3600) -> list:
    """Detect gaps in the timeline where information is missing."""
    gaps = []
    for i in range(len(events) - 1):
        ts1 = events[i].get("timestamp", 0)
        ts2 = events[i + 1].get("timestamp", 0)

        if isinstance(ts1, datetime):
            ts1 = ts1.timestamp()
        if isinstance(ts2, datetime):
            ts2 = ts2.timestamp()

        diff = ts2 - ts1
        if diff > gap_threshold_seconds:
            gaps.append({
                "from_event": events[i],
                "to_event": events[i + 1],
                "gap_seconds": round(diff, 2),
                "gap_hours": round(diff / 3600, 2)
            })
    return gaps
