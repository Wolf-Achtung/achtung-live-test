from flask import Flask, request, jsonify
from flask_cors import CORS
from openai import OpenAI
import os
import logging
import re

app = Flask(__name__)
CORS(app)
logging.basicConfig(level=logging.INFO)

# 🧠 GPT API Setup
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

@app.route("/", methods=["GET"])
def home():
    return "achtung.live GPT-API ist aktiv"

@app.route("/analyze", methods=["POST"])
def analyze():
    try:
        data = request.get_json()
        text = data.get("text", "")
        app.logger.info(f"📥 Text erhalten: {text[:100]}...")

        # 🧠 Prompt definieren
        prompt = (
            "Sie sind ein Datenschutz-Coach. Analysieren Sie diesen Text auf sensible Inhalte "
            "(z. B. medizinisch, finanziell, emotional). Geben Sie folgende strukturierte Antwort:\n\n"
            "**Erkannte Datenarten:**\n- ...\n\n**Datenschutz-Risiko:** 🔴 ...\n\n"
            "**achtung.live-Empfehlung:** ...\n**Tipp:** ...\n**Quelle:** ..."
        )

        # ✅ GPT Call
        gpt_response = client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": f"{prompt}\n\nText:\n{text}"}],
            temperature=0.3
        )
        gpt_text = gpt_response.choices[0].message.content
        app.logger.info(f"🤖 GPT-Antwort erhalten:\n{gpt_text[:200]}...")

        # 🔎 Extraktion
        detected = re.findall(r"(?i)Erkannte Datenarten:([\s\S]+?)\n\n", gpt_text)
        risk = re.findall(r"(?i)Datenschutz[- ]?Risiko:?\s*(🟢|🟡|🔴.*?)\n", gpt_text)
        explanation = re.findall(r"(?i)achtung\.live-Empfehlung:?\s*(.+?)\nTipp:", gpt_text, re.DOTALL)
        tip = re.findall(r"(?i)Tipp:?\s*(.+?)\nQuelle:", gpt_text, re.DOTALL)
        source = re.findall(r"(?i)Quelle:?\s*(https?://\S+)", gpt_text)

        # 🔧 Medienhilfe
        media_help_db = ["IBAN", "Medikament", "Diagnose", "Trauma"]
        help_types = [k for k in media_help_db if k.lower() in gpt_text.lower()]

        return jsonify({
            "detected_data": detected[0].strip() if detected else "Keine",
            "risk_level": risk[0].strip() if risk else "🟡 Unbekannt",
            "explanation": explanation[0].strip() if explanation else "Keine Empfehlung erkannt.",
            "tip": tip[0].strip() if tip else "Kein Tipp erkannt.",
            "source": source[0].strip() if source else "",
            "explanation_media": {"types": help_types}
        })

    except Exception as e:
        app.logger.error(f"❌ GPT-Fehler: {e}")
        # 🧪 Dummy-Fallback
        return jsonify({
            "detected_data": "IBAN, Medikament",
            "risk_level": "🔴 Sehr hohes Risiko",
            "explanation": "Diese Informationen könnten missbraucht werden.",
            "tip": "Teile IBAN & medizinische Infos nur verschlüsselt.",
            "source": "https://proton.me/de/mail",
            "explanation_media": { "types": ["IBAN", "Medikament"] }
        }), 200
