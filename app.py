from flask import Flask, request, jsonify
from flask_cors import CORS
from openai import OpenAI
import os
import json
import logging

# Initialisierung
app = Flask(__name__)
CORS(app)
logging.basicConfig(level=logging.INFO)

# OpenAI Client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Trusted Links laden
try:
    with open("trusted_links.json", "r", encoding="utf-8") as f:
        trusted_links = json.load(f)
    logging.info(f"✅ {len(trusted_links)} vertrauenswürdige Links geladen.")
except Exception as e:
    trusted_links = {}
    logging.warning(f"⚠️ trusted_links.json konnte nicht geladen werden: {e}")

# Funktion zur Auswahl eines passenden Links
def get_context_link(keywords):
    for keyword in keywords:
        if keyword in trusted_links:
            return f"[{trusted_links[keyword]['label']}]({trusted_links[keyword]['url']})"
    if "allgemein" in trusted_links:
        return f"[{trusted_links['allgemein']['label']}]({trusted_links['allgemein']['url']})"
    return "❌ Keine verlässliche Quelle verfügbar."

# Flask-Endpunkt
@app.route("/analyze", methods=["POST"])
def analyze():
    try:
        data = request.json
        user_input = data.get("text", "")
        language = data.get("language", "de")

        if not user_input:
            return jsonify({"error": "Kein Text übermittelt."}), 400

        # Prompt mit Platzhalter für Quelle
        prompt = f"""
Du bist ein Datenschutz- und Kommunikations-Experte. Analysiere folgenden Text in Bezug auf Datenschutzrisiken und formuliere Empfehlungen in folgender Struktur:

1. Erkannte Datenarten
2. Datenschutz-Risiko (Ampel: 🟢, 🟡, 🔴)
3. Bedeutung der gefundenen Elemente (nur wenn relevant)
4. achtung.live-Empfehlung:
5. Tipp:
6. Quelle (nur wenn relevant): {get_context_link(['gesundheitsdaten', 'kreditkartendaten', 'emojis', 'persoenliche_daten', 'politische_meinung'])}

Text: {user_input}

Sprache: {language}
"""

        response = client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7
        )

        result = response.choices[0].message.content
        return jsonify({"result": result})

    except Exception as e:
        logging.error(f"❌ Fehler: {e}")
        return jsonify({"error": str(e)}), 500

# Startpunkt für lokale Tests
if __name__ == "__main__":
    app.run(debug=True)
