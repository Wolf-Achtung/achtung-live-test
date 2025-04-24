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

EMOTIONAL_TRIGGERS = {
    "hoch": [
        "ich will nicht mehr", "ich kann nicht mehr", "suizid", "selbstmord", "hilfe", "verzweifelt", "am ende"
    ],
    "mittel": [
        "depression", "depressiv", "trauma", "panik", "überfordert", "stress", "therapie", "angst", "leiden"
    ],
    "niedrig": [
        "traurig", "einsam", "verletzt", "idiot", "chef", "müde", "allein", "ungerecht", "scheiße", "fuck"
    ]
}

def detect_empathy_level(text):
    tl = text.lower()
    for level in ["hoch", "mittel", "niedrig"]:
        if any(trigger in tl for trigger in EMOTIONAL_TRIGGERS[level]):
            return level
    return None

@app.route("/analyze", methods=["POST"])
def analyze():
    data = request.get_json()
    text = data.get("text", "")

    prompt = (
        "Du bist ein einfühlsamer Datenschutz-Coach. Analysiere den folgenden Text in Bezug auf Datenschutz und emotionale Sensibilität. "
        "Identifiziere präzise:\n\n"
        "1. **Erkannte Datenarten** (z. B. Gesundheitsdaten, IBAN, psychische Belastung etc.)\n"
        "2. **Datenschutz-Risiko-Ampel**: Nur 🟢 (kein Risiko), 🟡 (sensibel), 🔴 (kritisch). "
        "Setze 🔴, wenn mehrere sensible Inhalte kombiniert werden.\n"
        "3. **achtung.live-Empfehlung:** Was sollte der Nutzer tun?\n"
        "4. **Tipp:** Formuliere eine konkrete Hilfe.\n"
        "5. **Quelle:** (wenn vorhanden)\n\n"
        "Format:\n"
        "**Erkannte Datenarten:** ...\n"
        "**Datenschutz-Risiko:** ...\n"
        "**achtung.live-Empfehlung:** ...\n"
        "**Tipp:** ...\n"
        "**Quelle:** ...\n\n"
        f"Text:\n{text}"
    )

    gpt_response = client.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3
    )
    gpt_text = gpt_response.choices[0].message.content

    detected = re.findall(r"(?i)Erkannte Datenarten:([\s\S]+?)\n", gpt_text)
    risk = re.findall(r"(?i)Datenschutz[- ]?Risiko:?\s*(🟢|🟡|🔴.*?)\n", gpt_text)
    explanation = re.findall(r"(?i)achtung\.live-Empfehlung:?\s*(.+?)\nTipp:", gpt_text, re.DOTALL)
    tip = re.findall(r"(?i)Tipp:?\s*(.+?)\nQuelle:", gpt_text, re.DOTALL)
    source = re.findall(r"(?i)Quelle:?\s*(https?://\S+)", gpt_text)

    risk_level = risk[0].strip() if risk else "🟡 Unbekannt"

    # 🛡️ Fallback-Ampel: automatisch bewerten, falls GPT keine liefert
    if risk_level == "🟡 Unbekannt":
        critical_terms = ["gesundheit", "diagnose", "medikament", "iban", "konto", "adresse", "bank", "depression", "chef"]
        if sum(1 for word in critical_terms if word in text.lower()) >= 2:
            risk_level = "🔴 Kritisch"
        elif any(word in text.lower() for word in critical_terms):
            risk_level = "🟡 Sensibel"
        else:
            risk_level = "🟢 Kein Risiko"

    explanation_final = explanation[0].strip() if explanation else "Diese Info solltest du nur vertraulich teilen."
    tip_final = tip[0].strip() if tip else "Verwende sichere Methoden wie verschlüsselte E-Mail."

    empathy_level = detect_empathy_level(text)
    shadow_msg = None
    rewrite_suggestion = False

    if empathy_level == "hoch":
        shadow_msg = "Du sprichst über Gesundheit, Frust und Finanzen – möchtest du deinen Text diskret umformulieren?"
        rewrite_suggestion = True
    elif empathy_level == "mittel":
        shadow_msg = "Das klingt persönlich. Wir helfen dir beim sicheren Umschreiben."
        rewrite_suggestion = True
    elif empathy_level == "niedrig":
        shadow_msg = "Möchtest du deinen Text in eine geschützte Form bringen?"
        rewrite_suggestion = True

    return jsonify({
        "detected_data": detected[0].strip() if detected else "Keine",
        "risk_level": risk_level,
        "explanation": explanation_final,
        "tip": tip_final,
        "source": source[0].strip() if source else "",
        "empathy_message": shadow_msg,
        "rewrite_offer": rewrite_suggestion,
        "empathy_level": empathy_level or ""
    })

@app.route("/rewrite", methods=["POST"])
def rewrite():
    data = request.get_json()
    original = data.get("text", "")
    prompt = (
        "Formuliere diesen Text datenschutzkonform, empathisch und in einfacher Sprache um. "
        "Erhalte dabei die emotionale Aussage, aber schütze persönliche Inhalte durch Neutralität. "
        "Kling nicht therapeutisch oder übertrieben formal.\n\n"
        f"{original}"
    )
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3
    )
    return jsonify({ "rewritten": response.choices[0].message.content.strip() })

@app.route("/howto", methods=["GET"])
def howto():
    prompt = (
        "Erstelle eine einfache Schritt-für-Schritt-Anleitung auf Deutsch für Laien, "
        "wie man eine verschlüsselte E-Mail versendet. Nutze Dienste wie ProtonMail oder Tutanota."
    )
    try:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2
        )
        steps = response.choices[0].message.content.strip()
    except Exception as e:
        print("GPT fallback active:", e)
        steps = (
            "So sendest du eine verschlüsselte E-Mail:\n"
            "1. Erstelle ein kostenloses Konto bei proton.me oder tutanota.com\n"
            "2. Verfasse deine Nachricht, klicke auf das Schloss-Symbol\n"
            "3. Wähle ein Passwort – teile es getrennt mit der empfangenden Person\n"
            "4. Der Empfänger bekommt einen sicheren Link\n"
            "5. Optional: Lade Anhänge nur verschlüsselt hoch"
        )

    return jsonify({ "howto": steps })
