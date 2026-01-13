# backend/ai_sum.py
import json, textwrap

def summarise(raw: dict) -> str:
    summary = []
    if raw.get("nmap"):
        ports = len(raw["nmap"].get("open", []))
        summary.append(f"{ports} açık port bulundu.")
    if raw.get("zap"):
        highs = sum(1 for x in raw["zap"] if x.get("risk") == "High")
        summary.append(f"ZAP {highs} yüksek riskli bulgu raporladı.")
    risk = "YÜKSEK" if "High" in str(raw) else "ORTA" if "Medium" in str(raw) else "DÜŞÜK"
    return textwrap.shorten(" | ".join(summary), 200, placeholder="…") + f" → Risk: {risk}"
