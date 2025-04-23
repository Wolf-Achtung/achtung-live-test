from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import logging

app = Flask(__name__)
CORS(app)

# 📘 Debug-Log aktivieren
logging.basicConfig(level=logging.INFO)

@app.route("/", methods=["GET"])
def home():
    return "achtung.live Debug-API ist aktiv"

@app.route("/analyze", methods=["POST"])
def analyze():
    try:
        data = request.get_json()
        text = data.get("text", "")
        app.logger.info(f"📥 Anfrage erhalten: {text[:100]}...")

        # Dummy-Antwort ohne GPT
        dummy_response = {
            "detected_data": "IBAN, Medikament",
            "risk_level": "🔴 Sehr hohes Risiko",
            "explanation": "Diese Informationen könnten missbraucht werden.",
            "tip": "Teile IBAN & medizinische Infos nur verschlüsselt.",
            "source": "https://proton.me/de/mail",
            "explanation_media": {
                "types": ["IBAN", "Medikament"]
            }
        }

        return jsonify(dummy_response)

    except Exception as e:
        app.logger.error(f"❌ Fehler in /analyze: {e}")
        return jsonify({"error": str(e)}), 500
