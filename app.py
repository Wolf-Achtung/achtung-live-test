from flask import Flask, request, jsonify
from flask_cors import CORS
from openai import OpenAI
import os
import json
import logging
import re
import requests

app = Flask(__name__)
CORS(app)

# Setup logging
logging.basicConfig(level=logging.DEBUG)

# OpenAI initialisieren
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Lade Emoji-Datenbank
with open("emojiDatabase.json", "r", encoding="utf-8") as f:
    emoji_db = json.load(f)

# Lade trusted_links.json
try:
    with open("trusted_links.json", "r", encoding="utf-8") as f:
        trusted_links = json.load(f)
    logging.info(f"✅ {len(trusted_links)} vertrauenswürdige Links geladen.")
except Exception as e:
    trusted_links = []
    logging.warning(f"⚠️ trusted_links.json konnte nicht geladen werden: {e}")

# Linkprüfung
def check_links_in_text(text):
    found_links = re.findall(r'(https?://[^\s]+)', text)
    checked_links = []
    for link in found_links:
        try:
            resp = requests.head(link, allow_redirects=True, timeout=3)
            if resp.status_code == 200:
                checked_links.append(f"✅ Link erreichbar: <a href='{link}' target='_blank'>{link}</a>")
            else:
                checked_links.append(f"❌ Link nicht erreichbar: {link}")
        except Exception:
            checked_links.append(f"❌ Link nicht erreichbar: {link}")
    return checked_links

def get_emoji_info(text):
    found = []
    for emoji in emoji_db:
        if emoji["symbol"] in text:
            found.append(f"{emoji['symbol']}: {emoji['bedeutung']} ([Quelle]({emoji['quelle']}))")
    return found

@app.route("/analyze", methods=["POST"])
def analyze():
    try:
        data = request.json
        user_input = data.get("text", "")
        lang = data.get("lang", "de")

        if not user_input.strip():
            return jsonify({"error": "Kein Text übermittelt."}), 400

        prompt = f"""
Du bist ein Datenschutz- und Kommunikationsberater. Analysiere den folgenden Text aus Sicht der Privatsphäre, Datensicherheit und öffentlicher Wirkung.

Antworte in der Sprache: {lang.upper()}.

1. **Erkannte Datenarten**
Liste alle potenziell sensiblen oder identifizierenden Informationen im Text auf.

2. **Datenschutz-Risiko**
Bewerte das Risiko (Ampel: 🟢, 🟡, 🔴).

3. **Bedeutung der gefundenen Elemente**
Erkläre, warum diese Informationen kritisch oder sensibel sein könnten.

4. **achtung.live-Empfehlung (empathisch & konkret)**
Gib eine klare, freundliche Handlungsempfehlung.

5. **Tipp: 1 sinnvoller Rewrite-Vorschlag**
Formuliere den Text so um, dass er datensicher ist, aber die Aussage erhalten bleibt.

6. **Quelle (nur wenn relevant)**
Empfehle vertrauenswürdige Links, um sich zum Thema weiter zu informieren.

Text:
{user_input}
"""

        logging.debug("🔍 Prompt sent to GPT-4")
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}]
        )
        gpt_output = response.choices[0].message.content.strip()

        # Linkprüfung & Emoji-Ergänzung
        link_results = check_links_in_text(gpt_output)
        emoji_info = get_emoji_info(user_input)

        final_output = gpt_output
        if emoji_info:
            final_output += "\n\n🧩 Emoji-Analyse:\n" + "\n".join(emoji_info)
        if link_results:
            final_output += "\n\n🌐 Linkprüfung:\n" + "\n".join(link_results)

        return jsonify({"result": final_output})
    except Exception as e:
        logging.exception("❌ Fehler in /analyze")
        return jsonify({"error": str(e)}), 500
