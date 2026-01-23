def summarize_compose_memory(memories):
    prefs = {
        "tone": None,
        "brevity": None,
    }

    successful = [
        m for m in memories
        if m.get("intent") == "COMPOSE"
        and m.get("outcome") in ("SENT", "APPROVED")
    ]

    if not successful:
        return prefs

    tones = []
    for m in successful:
        meta = m.get("metadata") or {}
        if meta.get("tone"):
            tones.append(meta["tone"])

    if tones:
        prefs["tone"] = max(set(tones), key=tones.count)

    prefs["brevity"] = "concise"
    return prefs
