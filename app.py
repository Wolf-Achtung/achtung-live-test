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
    "medizinisch": """Sie sind Datenschutz-Coach. Analysieren Sie den folgenden Text auf medizinisch sensible Informationen (Krankheiten, Diagnosen, Medikamente, Arztkontakte). Wenn solche enthalten sind:

1. Listen Sie die Datenarten konkret auf.
2. Bewerten Sie das Risiko vorsorglich mit einer Ampel (🟢 / 🟡 / 🔴).
3. Erläutern Sie, warum diese Infos vertraulich sind – einfach, empathisch.
4. Geben Sie einen konkreten Vorschlag, wie der Nutzer diese Information sicherer übermitteln oder anonymisieren kann – für Laien verständlich.
5. Fügen Sie eine Quelle oder Anleitung als Link hinzu.""",

    "finanziell": """Sie sind Datenschutz-Coach. Prüfen Sie den Text auf finanzsensible Angaben (IBAN, Kreditkartennummer, Gehalt, Bankverbindung, Schulden, Verträge). Wenn vorhanden:

1. Nennen Sie die sensiblen Datenarten.
2. Setzen Sie das Risiko mindestens auf 🟡, bei Konto- oder Kartennummern auf 🔴.
3. Erklären Sie ruhig, warum diese Angaben riskant sind.
4. Geben Sie einen praktischen, einfach umsetzbaren Tipp – inkl. Link zur sicheren Methode.
5. Strukturieren Sie die Antwort klar, verwenden Sie keinen Tech-Jargon.""",

    "emotional": """Sie sind ein einfühlsamer Datenschutz-Coach. Analysieren Sie den Text auf emotional sensible Inhalte (Beziehungskrisen, psychische Belastung, intime Themen, Trauer). Wenn Sie solche Inhalte finden:

1. Nennen Sie die erkannten Aussagen.
2. Bewerten Sie das Risiko – schon bei potenzieller Stigmatisierung mit 🟡 oder 🔴.
3. Erläutern Sie ruhig und respektvoll, warum Diskretion wichtig ist.
4. Geben Sie einen konkreten, leicht umsetzbaren Tipp zur sicheren Kommunikation.
5. Geben Sie, wenn möglich, einen Link mit Anleitung an.""",

    "standard": """Sie sind ein empathischer Datenschutz-Coach. Bitte analysieren Sie den folgenden Text. Wenn sensible Inhalte enthalten sind (persönlich, medizinisch, finanziell, emotional):

1. Nennen Sie die Datenarten.
2. Bewerten Sie das Risiko vorsorglich mit Ampel (🟢, 🟡, 🔴) – lieber zu streng als zu tolerant.
3. Erklären Sie einfach, warum das problematisch sein kann.
4. Geben Sie einen klaren Vorschlag zur sicheren Übermittlung oder Umschreibung – mit Link für technisch Unerfahrene.
5. Strukturieren Sie die Antwort wie folgt:

---
**Erkannte Datenarten:**  
...

**Datenschutz-Risiko:** 🟡 Mögliches Risiko

**achtung.live-Empfehlung:**  
...

**Tipp:**  
...

**Quelle:**  
..."""
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
    # Datenarten (unterstützt auch Aufzählungspunkte)
    detected_block = re.search(r"(?i)Erkannte Datenarten:([\s\S]+?)\n\n", raw_text)
    if detected_block:
        raw_detected = detected_block.group(1).strip()
        detected_items = re.findall(r"-\s*(.+)", raw_detected)
        detected_data = ", ".join(detected_items) if detected_items else raw_detected
    else:
        detected_data = "Keine"

    # Risiko (einzeilig)
    risk = re.findall(r"(?i)Datenschutz[- ]?Risiko:?\s*(🟢|🟡|🔴.*?)\n", raw_text)

    # Empfehlung, Tipp, Quelle
    explanation = re.findall(r"(?i)achtung\.live-Empfehlung:?\s*(.+?)(?:\nTipp:|\nQuelle:|\Z)", raw_text, re.DOTALL)
    tip = re.findall(r"(?i)Tipp:?\s*(.+?)(?:\nQuelle:|\Z)", raw_text, re.DOTALL)
    source = re.findall(r"(?i)Quelle:?\s*(https?://\S+)", raw_text)

    # Risikoanpassung bei Schlüsselwörtern (Fallback bei zu laschem GPT)
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
        "explanation": explanation[0].strip() if explanation else "Bitte prüfen Sie, ob diese Angabe vertraulich ist.",
        "tip": tip[0].strip() if tip else "Wir empfehlen, diese Information nur verschlüsselt oder anonymisiert zu übermitteln.",
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
