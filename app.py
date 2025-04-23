from flask import Flask, request, jsonify
from flask_cors import CORS
from openai import OpenAI
import os
import json
import logging

# Logging aktivieren
logging.basicConfig(level=logging.DEBUG)

app = Flask(__name__)
CORS(app)

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Emoji-DB laden
with open("emojiDatabase.json", "r", encoding="utf-8") as f:
    try:
        emoji_db = json.load(f)
    except Exception as e:
        logging.error(f"❌ Fehler beim Laden der emojiDatabase: {e}")
        emoji_db = []

# Trusted Links laden
with open("trusted_links.json", "r", encoding="utf-8") as f:
    try:
        trusted_links = json.load(f)
    except Exception as e:
        logging.error(f"❌ trusted_links.json konnte nicht geladen werden: {e}")
        trusted_links = []

def get_emoji_info(text):
    found = []
    for emoji in emoji_db:
        if isinstance(emoji, dict) and emoji.get("symbol") in text:
            bedeutung = emoji.get("bedeutung", "Unbekannt")
            quelle = emoji.get("quelle", "#")
            found.append(f"{emoji['symbol']}: {bedeutung} ([Quelle]({quelle}))")
    return found

def get_link_for_topic(topic):
    for item in trusted_links:
        if isinstance(item, dict) and topic.lower() in item.get("name", "").lower():
            return item.get("url", None)
    return None

@app.route("/analyze", methods=["POST"])
def analyze():
    data = request.json
    user_input = data.get("text", "")

    logging.info(f"🔍 Analyse gestartet für Text: {user_input}")

    try:
        emoji_info = get_emoji_info(user_input)
        themen_link = get_link_for_topic("Datenschutz")
        prompt = f"""
Analysiere den folgenden Text auf Datenschutzrisiken, politische Aussagen und versteckte Emoji-Codes.
Gib folgende Abschnitte aus:
1. Erkannte Datenarten
2. Datenschutz-Risiko (Ampel: 🟢, 🟡, 🔴)
3. Bedeutung der gefundenen Elemente
4. achtung.live-Empfehlung (empathisch & konkret)
5. Tipp: 1 sinnvoller Rewrite-Vorschlag
6. Quelle (nur wenn relevant)

Text:
\"\"\"{user_input}\"\"\"

Emoji-Analyse:
{', '.join(emoji_info) if emoji_info else "Keine Emojis erkannt."}

Quelle: {themen_link or 'Nicht verfügbar'}
"""

        completion = client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}]
        )

        result = completion.choices[0].message.content
        return jsonify({"result": result})

    except Exception as e:
        logging.error(f"❌ Fehler bei Analyse: {e}")
        return jsonify({"error": str(e)}), 500
