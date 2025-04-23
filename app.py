from flask import Flask, request, jsonify
from flask_cors import CORS
from openai import OpenAI
import os
import logging
import re

app = Flask(__name__)
CORS(app)
logging.basicConfig(level=logging.INFO)

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

EMOTIONAL_TRIGGERS = ["verletzt", "verloren", "traurig", "deprimiert", "Hilfe", "einsam", "Schmerz", "nicht mehr weiter"]

@app.route("/analyze", methods=["POST"])
def analyze():
    data = request.get_json()
    text = data.get("text", "")
    app.logger.info(f"📥 Text erhalten: {text[:100]}...")

    prompt = (
        "Du bist ein empathischer Datenschutz-Coach. Analysiere den Text und gib folgende strukturierte Antwort:\n"
        "**Erkannte Datenarten:**\n- ...\n\n**Datenschutz-Risiko:** 🔴 ...\n\n"
        "**achtung.live-Empfehlung:** ...\n**Tipp:** ...\n**Quelle:** ..."
    )

    gpt_response = client.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": f"{prompt}\n\nText:\n{text}"}],
        temperature=0.3
    )
    gpt_text = gpt_response.choices[0].message.content

    detected = re.findall(r"(?i)Erkannte Datenarten:([\s\S]+?)\n\n", gpt_text)
    risk = re.findall(r"(?i)Datenschutz[- ]?Risiko:?\s*(🟢|🟡|🔴.*?)\n", gpt_text)
    explanation = re.findall(r"(?i)achtung\.live-Empfehlung:?\s*(.+?)\nTipp:", gpt_text, re.DOTALL)
    tip = re.findall(r"(?i)Tipp:?\s*(.+?)\nQuelle:", gpt_text, re.DOTALL)
    source = re.findall(r"(?i)Quelle:?\s*(https?://\S+)", gpt_text)

    risk_level = risk[0].strip() if risk else "🟡 Unbekannt"
    explanation_final = explanation[0].strip() if explanation else "Diese Info solltest du nur vertraulich teilen."
    tip_final = tip[0].strip() if tip else "Verwende sichere Methoden wie verschlüsselte E-Mail."

    help_types = [k for k in ["IBAN", "Medikament"] if k.lower() in gpt_text.lower()]
    empathy_msg = None
    rewrite_suggestion = None

    if any(trigger in text.lower() for trigger in EMOTIONAL_TRIGGERS):
        empathy_msg = "🫂 Das klingt sehr persönlich. Möchtest du den Text neutraler und geschützter umformulieren lassen?"
        rewrite_suggestion = True

    return jsonify({
        "detected_data": detected[0].strip() if detected else "Keine",
        "risk_level": risk_level,
        "explanation": explanation_final,
        "tip": tip_final,
        "source": source[0].strip() if source else "",
        "explanation_media": {"types": help_types},
        "empathy_message": empathy_msg,
        "rewrite_offer": rewrite_suggestion
    })


@app.route("/rewrite", methods=["POST"])
def rewrite():
    data = request.get_json()
    original = data.get("text", "")

    prompt = (
        "Bitte formuliere diesen Text empathisch, anonymisiert und datenschutzkonform um, "
        "ohne die emotionale Aussage zu verlieren. Vermeide personenbezogene oder zu intime Inhalte, "
        "nutze einen schützenden, sensiblen Ton. Gib nur den neuen Text aus:\n\n"
        f"{original}"
    )

    response = client.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3
    )
    new_text = response.choices[0].message.content.strip()
    return jsonify({ "rewritten": new_text })
