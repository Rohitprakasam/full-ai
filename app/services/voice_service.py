"""Voice Intelligence — faster-whisper transcription (local CPU)."""
from faster_whisper import WhisperModel

model = WhisperModel("base", device="cpu", compute_type="int8")


def transcribe_audio(audio_path: str) -> dict:
    segments, info = model.transcribe(audio_path, beam_size=5)
    full_text = ""
    timestamped = []
    for segment in segments:
        full_text += segment.text + " "
        timestamped.append({"start": round(segment.start, 2), "end": round(segment.end, 2), "text": segment.text.strip()})
    return {"full_transcript": full_text.strip(), "language": info.language, "duration": info.duration, "segments": timestamped}
