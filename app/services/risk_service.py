"""Risk Scoring Engine — Pure Python rule-based assessment."""


def calculate_risk_score(case_data: dict) -> dict:
    score = 0
    flags = []
    evidence_list = case_data.get("evidence", [])
    timeline_events = case_data.get("timeline_events", [])
    graph_data = case_data.get("graph", {})

    if len(evidence_list) > 20:
        score += 15; flags.append("High evidence volume — complex case")
    suspects = [n for n in graph_data.get("nodes", []) if n.get("type") == "Person"]
    if len(suspects) > 3:
        score += 20; flags.append(f"{len(suspects)} connected individuals detected")

    financial_kw = ["transfer", "payment", "cash", "bank", "transaction", "money"]
    violence_kw = ["weapon", "knife", "gun", "threat", "attack", "assault", "murder"]

    for ev in evidence_list:
        summary = (ev.get("ai_summary") or "").lower()
        if any(kw in summary for kw in financial_kw):
            score += 10; flags.append("Financial evidence detected"); break
    for ev in evidence_list:
        summary = (ev.get("ai_summary") or "").lower()
        if any(kw in summary for kw in violence_kw):
            score += 25; flags.append("Weapon or violence evidence present"); break

    risk_level = "LOW" if score < 30 else "MEDIUM" if score < 60 else "HIGH" if score < 80 else "CRITICAL"
    recs = {
        "LOW": "Standard investigation protocols apply.",
        "MEDIUM": "Prioritize evidence review. Additional officers recommended.",
        "HIGH": "Immediate senior review required. Consider arrest warrants.",
        "CRITICAL": "URGENT — Escalate immediately. Full task force deployment recommended."
    }
    return {"score": min(score, 100), "risk_level": risk_level, "flags": list(set(flags)),
            "recommendation": recs.get(risk_level, "")}
