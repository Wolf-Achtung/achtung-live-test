from flask import Flask, request, jsonify
from flask_cors import CORS
from openai import OpenAI
import re
import os

app = Flask(__name__)
CORS(app)

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

PROMPT_CATEGORIES = {
    "medizinisch": ["Diagnose", "Rezept", "Arzt", "Krankheit", "Therapie", "Medikament"],
    "finanziell": ["IBAN", "Kreditkarte", "Gehalt", "Bank", "Investition", "Schulden"],
    "emotional": ["Beziehung", "Depression", "Verlust", "Angst", "Trauma", "intim"]
}

PROMPTS = {
    "medizinisch": """Sie sind Datenschutz-Coach. Analysieren Sie den folgenden Text auf medizinisch sensible Informationen (z. B. Krankheiten, Diagnosen, Medikamente, Arztkontakte). Wenn Sie solche Inhalte finden:

1. Listen Sie die Datenarten konkret auf – **eine pro Zeile mit -** (z. B. `- Medikament`)
2. Bewerten Sie das Risiko vorsorglich mit einer Ampel (🟢 / 🟡 / 🔴).
3. Erläutern Sie in einfacher Sprache, warum diese Infos vertraulich sind.
4. Geben Sie einen konkreten Vorschlag zur sicheren Übermittlung.
5. Fügen Sie eine hilfreiche Quelle (Link) hinzu.""",

    "finanziell": """Sie sind Datenschutz-Coach. Prüfen Sie den Text auf finanzsensible Angaben (z. B. IBAN, Kreditkartennummern, Gehalt, Verträge). Wenn vorhanden:

1. Listen Sie jede Datenart mit `-` auf (z. B. `- IBAN`)
2. Setzen Sie das Risiko mindestens auf 🟡, bei Kontodaten auf 🔴.
3. Erklären Sie ruhig, warum diese Angaben riskant sind.
4. Geben Sie einen praktischen Tipp inkl. Link zur sicheren Methode.
5. Kein Tech-Jargon, bitte einfach erklären.""",

    "emotional": """Sie sind ein einfühlsamer Datenschutz-Coach. Analysieren Sie den Text auf emotional sensible Inhalte (z. B. Beziehungskrisen, psychische Belastung). Wenn Sie solche Inhalte finden:

1. Nennen Sie diese Inhalte einzeln mit `-`
2. Bewerten Sie das Risiko (🟡 / 🔴)
3. Erklären Sie in ruhiger Sprache, warum Diskretion wichtig ist.
4. Geben Sie einen konkreten Tipp zur sicheren Kommunikation.
5. Quelle oder Anleitung gern als Link beilegen.""",

    "standard": """Sie sind ein empathischer Datenschutz-Coach. Analysieren Sie den Text auf sensible Inhalte (z. B. finanziell, medizinisch, emotional, persönlich):

1. Schreiben Sie jede erkannte Datenart als `-`-Liste
2. Bewerten Sie das Datenschutz-Risiko vorsorglich mit 🟢, 🟡 oder 🔴
3. Geben Sie eine kurze, verständliche Erklärung
4. Bieten Sie eine praktische Lösung an (z. B. "Datei verschlüsseln")
5. Hängen Sie, falls möglich, eine Quelle (Link) an

Strukturieren Sie Ihre Antwort wie folgt:
---
**Erkannte Datenarten:**
- ...

**Datenschutz-Risiko:** 🟡 ...

**achtung.live-Empfehlung:** ...
**Tipp:** ...
**Quelle:** https://...
"""
}

def choose_prompt(text):
    for category, keywords in PROMPT_CATEGORIES.items():
        if any(kw.lower() in text.lower() for kw in keywords):
            return PROMPTS[category]
    return PROMPTS["standard"]

def call_gpt(prompt, user_text):
    full_prompt = f"{prompt}\n\nText:\n{user_text}"
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": full_prompt}],
        temperature=0.3
    )
    return response.choices[0].message.content

def extract_structured_json(raw_text):
    # Datenarten (mit - Aufzählung)
    detected_block = re.search(r"(?i)Erkannte Datenarten:([\s\S]+?)\n\n", raw_text)
    if detected_block:
        raw_detected = detected_block.group(1).strip()
        detected_items = re.findall(r"-\s*(.+)", raw_detected)
        detected_data = ", ".join(detected_items) if detected_items else raw_detected
    else:
        detected_data = "Keine"

    # Risiko
    risk = re.findall(r"(?i)Datenschutz[- ]?Risiko:?\s*(🟢|🟡|🔴.*?)\n", raw_text)

    # Erklärung, Tipp, Quelle
    explanation = re.findall(r"(?i)achtung\.live-Empfehlung:?\s*(.+?)(?:\nTipp:|\nQuelle:|\Z)", raw_text, re.DOTALL)
    tip = re.findall(r"(?i)Tipp:?\s*(.+?)(?:\nQuelle:|\Z)", raw_text, re.DOTALL)
    source = re.findall(r"(?i)Quelle:?\s*(https?://\S+)", raw_text)

    # Risiko nachschärfen bei Schlüsselbegriffen
    raw_lower = raw_text.lower()
    if any(word in raw_lower for word in ["iban", "kreditkarte", "bankkonto"]):
        risk_level = "🔴 Finanzdaten erkannt – sehr hohes Risiko"
    elif any(word in raw_lower for word in ["medikament", "diagnose", "krankheit"]):
        risk_level = "🟡 Vorsicht – medizinische Angabe erkannt"
    else:
        risk_level = risk[0].strip() if risk else "🟢 Kein Risiko"

    return {
        "detected_data": detected_data,
        "risk_level": risk_level,
        "explanation": explanation[0].strip() if explanation else "Diese Information könnte missbraucht werden, wenn sie öffentlich wird – bitte behandeln Sie sie mit Vorsicht.",
        "tip": tip[0].strip() if tip else "Nutzen Sie eine sichere Methode wie verschlüsselte E-Mail oder passwortgeschützte Dateiübertragung. Anleitung: https://protonmail.com/support/knowledge-base/how-to-send-encrypted-emails/",
        "source": source[0].strip() if source else ""
    }

@app.route("/analyze", methods=["POST"])
def analyze():
    data = request.get_json()
    user_text = data.get("text", "")
    prompt = choose_prompt(user_text)
    gpt_response = call_gpt(prompt, user_text)
    structured = extract_structured_json(gpt_response)
    return jsonify(structured)

@app.route("/", methods=["GET"])
def home():
    return "achtung.live API ist aktiv"
