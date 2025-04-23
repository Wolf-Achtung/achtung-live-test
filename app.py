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
    "standard": """Sie sind ein empathischer Datenschutz-Coach. Analysieren Sie den Text auf sensible Inhalte:

1. Datenarten: Auflisten mit `-` je Zeile
2. Datenschutz-Risiko: Ampel
3. Erklärung
4. Tipp
5. Quelle (Link, falls möglich)

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
            return PROMPTS["standard"]
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
    detected_block = re.search(r"(?i)Erkannte Datenarten:([\s\S]+?)\n\n", raw_text)
    if detected_block:
        raw_detected = detected_block.group(1).strip()
        detected_items = re.findall(r"-\s*(.+)", raw_detected)
        detected_data = ", ".join(detected_items) if detected_items else raw_detected
    else:
        detected_data = "Keine"

    risk = re.findall(r"(?i)Datenschutz[- ]?Risiko:?\s*(🟢|🟡|🔴.*?)\n", raw_text)
    explanation = re.findall(r"(?i)achtung\.live-Empfehlung:?\s*(.+?)(?:\nTipp:|\nQuelle:|\Z)", raw_text, re.DOTALL)
    tip = re.findall(r"(?i)Tipp:?\s*(.+?)(?:\nQuelle:|\Z)", raw_text, re.DOTALL)
    source = re.findall(r"(?i)Quelle:?\s*(https?://\S+)", raw_text)

    media_help_db = {
        "IBAN": "IBAN",
        "Medikament": "Medikament",
        "Diagnose": "Diagnose",
        "Trauma": "Trauma"
    }
    matched_keys = [key for key in media_help_db if key.lower() in detected_data.lower()]
    media_help = {"types": matched_keys} if matched_keys else {}

    return {
        "detected_data": detected_data,
        "risk_level": risk[0].strip() if risk else "🟡 Vorsicht – unklare Einschätzung",
        "explanation": explanation[0].strip() if explanation else "Diese Information könnte missbraucht werden.",
        "tip": tip[0].strip() if tip else "Nutzen Sie eine sichere Methode wie verschlüsselte E-Mail.",
        "source": source[0].strip() if source else "",
        "explanation_media": media_help
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
