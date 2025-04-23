from flask import Flask, request, jsonify
from flask_cors import CORS
from openai import OpenAI
import os
import json
import logging

app = Flask(__name__)
CORS(app)

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Trusted Links laden
try:
    with open("trusted_links.json", "r", encoding="utf-8") as f:
        trusted_links = json.load(f)
        print(f"✅ {len(trusted_links)} vertrauenswürdige Links geladen.")
except Exception as e:
    trusted_links = []
    print("⚠️ trusted_links.json konnte nicht geladen werden:", e)

# Logging aktivieren
logging.basicConfig(level=logging.DEBUG)

@app.route("/analyze", methods=["POST"])
def analyze_text():
    data = request.json
    input_text = data.get("text", "")
    language = data.get("language", "de")

    if not input_text:
        return jsonify({"error": "Textfeld ist leer."}), 400

    prompt = f"""
Analysieren Sie folgenden Text auf Datenschutzrisiken, Emoji-Symbolik und rechtliche Fallstricke:
"{input_text}"

Antwortstruktur:
1. Erkannte Datenarten
2. Datenschutz-Risiko (Ampel: 🟢, 🟡, 🔴)
3. Bedeutung der gefundenen Elemente
4. achtung.live-Empfehlung
5. Tipp: Rewrite-Vorschlag oder sichere Handlungsalternative
6. Quelle (nur wenn relevant)

Nutzen Sie klare, verständliche Sprache.
"""

    try:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7
        )

        # 🛠 JSON-Safe-Access: response.choices[0].message.content
        content = None
        if hasattr(response, "choices") and isinstance(response.choices, list):
            choice = response.choices[0]
            if hasattr(choice, "message") and hasattr(choice.message, "content"):
                content = choice.message.content

        if not content:
            raise ValueError("GPT-Antwort nicht lesbar oder leer.")

        return jsonify({"result": content})

    except Exception as e:
        logging.error(f"❌ GPT-Fehler: {e}")
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)
