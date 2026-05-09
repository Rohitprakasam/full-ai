"""NLP Service — Featherless AI summarization + spaCy NER."""
import spacy
from app.services.llm_client import chat_completion, generate_embeddings

nlp = spacy.load("en_core_web_sm")


def summarize_text(text: str, context: str = "forensic evidence") -> str:
    messages = [
        {"role": "system", "content": f"You are a forensic AI analyst. Analyze the following {context} document. "
         "Extract: key facts, persons mentioned, locations, dates, and suspicious elements. "
         "Provide a structured summary in 5-8 bullet points. Be precise and factual."},
        {"role": "user", "content": text[:4000]}
    ]
    return chat_completion(messages)


def extract_entities(text: str) -> dict:
    doc = nlp(text[:100000])
    return {
        "persons": list({ent.text for ent in doc.ents if ent.label_ == "PERSON"}),
        "locations": list({ent.text for ent in doc.ents if ent.label_ in ["GPE", "LOC"]}),
        "dates": list({ent.text for ent in doc.ents if ent.label_ == "DATE"}),
        "organizations": list({ent.text for ent in doc.ents if ent.label_ == "ORG"}),
        "money": list({ent.text for ent in doc.ents if ent.label_ == "MONEY"}),
    }


def analyze_text_full(text: str, context: str = "forensic evidence") -> dict:
    summary = summarize_text(text, context)
    entities = extract_entities(text)
    embedding = generate_embeddings(text[:8000])
    return {"summary": summary, "entities": entities, "embedding": embedding}
