from flask import Flask, request, jsonify
from flask_cors import CORS
import openai
import re

app = Flask(__name__)
CORS(app)

# 🔐 Setze deinen echten OpenAI API-Key hier
openai.api_key = "DEIN_OPENAI_KEY"

# 🔍 Kategorisierte Schlüsselwörter für dynamisches Prompt-Routing
PROMPT_CATEGORIES = {
    "medizinisch": ["Diagnose", "Rezept", "Arzt", "Krankheit", "Therapie", "Medikament"],
    "finanziell": ["IBAN", "Kreditkarte", "Gehalt", "Bank", "Investition", "Schulden"],
    "emotional": ["Beziehung", "Depression", "Verlust", "Angst", "Trauma", "intim"]
}

# 📋 Prompt-Vorlagen
PROMPTS = {
    "medizinisch": """Analysieren Sie den folgenden Text auf medizinisch sensible Informationen wie Krankheiten, Medikamente, Diagnosen oder Arztkontakte. Wenn Sie solche Inhalte finden, bieten Sie eine strukturierte Analyse:
1. Erkannte Datenarten
2. Datenschutz-Risiko (Ampel)
3. Empathische Erklärung + Empfehlung
4. Praktischer Tipp (ggf. Link)
5. Quelle""",
    "finanziell": """Prüfen Sie den folgenden Text auf finanzsensible Angaben wie Kontodaten, Kreditkartennummern, Gehälter oder Schulden. Wenn vorhanden, ersetzen Sie diese durch anonyme, aber inhaltlich passende Umschreibungen. Strukturieren Sie Ihre Antwort:
1. Datenarten
2. Risiko (Ampel)
3. Erklärung
4. Konkreter Tipp mit Link
5. Quelle""",
    "emotional": """Bitte überprüfen Sie folgenden Text auf emotional sensible Aussagen (z. B. über Beziehungskrisen, psychische Belastung, intime Erlebnisse). Wenn vorhanden, analysieren Sie:
1. Welche sensiblen Aussagen enthalten sind
2. Ampel-Risiko
3. Warum diese problematisch sein könnten
4. Konkrete Handlungsempfehlung
5. Quelle (falls vorhanden)""",
    "standard": """Sie sind ein empathischer Datenschutz-Coach. Bitte analysieren Sie den folgenden Text. Wenn sensible Informationen erkannt werden:
1. Nennen Sie die erkannten Datenarten.
2. Bewerten Sie das Datenschutzrisiko mit einer Ampel (🟢, 🟡, 🔴).
3. Erklären Sie, warum diese Daten kritisch sind.
4. Geben Sie eine konkrete Handlungsempfehlung – mit Link zu einer sicheren Methode.
5. Quelle."""
}

# 🔁 Auswahl der passenden Prompt-Vorlage
def choose_prompt(text):
    for category, keywords in PROMPT_CATEGORIES.items():
        if any(kw.lower() in text.lower() for kw in keywords):
            return PROMPTS[category]
    return PROMPTS["standard"]

# 🤖 GPT-Call
def call_gpt(prompt, user_text):
    full_prompt = f"{prompt}\n\nText:\n{user_text}"
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role": "user", "content": full_prompt}],
        temperature=0.3
    )
    return response.choices[0].message["content"]

# 🧠 Textanalyse-Ausgabe extrahieren & strukturieren
def extract_structured_json(raw_text):
    detected = re.findall(r"(?i)Erkannte Datenarten:?\s*(.+?)\n", raw_text)
    risk = re.findall(r"(?i)Datenschutz[- ]?Risiko:?\s*(🟢|🟡|🔴.*?)\n", raw_text)
    explanation = re.findall(r"(?i)achtung\.live-Empfehlung:?\s*(.+?)(?:\n|Tipp:)", raw_text, re.DOTALL)
    tip = re.findall(r"(?i)Tipp:?\s*(.+?)(?:\n|Quelle:)", raw_text, re.DOTALL)
    source = re.findall(r"(?i)Quelle:?\s*(https?://\S+)", raw_text)

    return {
        "detected_data": detected[0].strip() if detected else "Keine",
        "risk_level": risk[0].strip() if risk else "🟢 Kein Risiko",
        "explanation": explanation[0].strip() if explanation else "Keine Empfehlung verfügbar.",
        "tip": tip[0].strip() if tip else "Kein Tipp verfügbar.",
        "source": source[0].strip() if source else ""
    }

# 🔐 Haupt-Endpunkt für Analyse
@app.route("/analyze", methods=["POST"])
def analyze():
    data = request.get_json()
    user_text = data.get("text", "")
    prompt = choose_prompt(user_text)
    gpt_response = call_gpt(prompt, user_text)
    structured = extract_structured_json(gpt_response)
    return jsonify(structured)

# ✅ Startseite zum Test
@app.route("/", methods=["GET"])
def home():
    return "achtung.live API ist aktiv"
