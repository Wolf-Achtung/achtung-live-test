from flask import Flask, request, jsonify
from flask_cors import CORS
from openai import OpenAI
import os
import json
import requests
import re
from datetime import datetime

app = Flask(__name__)
CORS(app)

# OpenAI Client ab Version 1.x
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Logging aktivieren
LOGFILE = "debug_log.txt"

def log_debug(info):
    with open(LOGFILE, "a") as f:
        f.write(f"[{datetime.now()}] {info}\n")

# Lade Emoji-Datenbank
try:
    with open("emojiDatabase.json", "r", encoding="utf-8") as f:
        emoji_db = json.load(f)
except Exception as e:
    emoji_db = {}
    log_debug(f"⚠️ Emoji-Datenbank konnte nicht geladen werden: {e}")

# Lade Trusted Links
try:
    with open("trusted_links.json", "r", encoding="utf-8") as f:
        trusted_links = json.load(f)
        log_debug(f"✅ {len(trusted_links)} vertrauenswürdige Links geladen.")
except Exception as e:
    trusted_links = []
    log_debug(f"⚠️ trusted_links.json konnte nicht geladen werden: {e}")

def check_links_status(links):
    result = []
    for link in links:
        try:
            response = requests.get(link, timeout=3)
            if response.status_code == 200:
                result.append(f"[{link}]({link})")
            else:
                result.append(f"❌ Link nicht erreichbar: {link}")
        except Exception:
            result.append(f"❌ Fehlerhafter Link: {link}")
    return result

def extract_links(text):
    return re.findall(r"https?://[^\s]+", text)

def find_emoji_meaning(text):
    used_emojis = [char for char in text if char in emoji_db]
    results = []
    for emoji in used_emojis:
        entry = emoji_db.get(emoji)
        if entry:
            meaning = entry.get("bedeutung", "Unbekannt")
            quelle = entry.get("quelle", "Unbekannt")
            results.append(f"{emoji}: {meaning} ([Quelle]({quelle}))")
    return results

@app.route("/analyze", methods=["POST"])
def analyze():
    try:
        data = request.get_json()
        user_input = data.get("text", "")
        language = data.get("language", "de")

        log_debug(f"📥 Eingangstext: {user_input} / Sprache: {language}")

        # Emoji-Kontextanalyse
        emoji_analysis = find_emoji_meaning(user_input)
        log_debug(f"🔍 Emoji-Analyse: {emoji_analysis}")

        # GPT-Aufruf vorbereiten
        messages = [
            {
                "role": "system",
                "content": f"""
Du bist ein verantwortungsbewusster Datenschutz-Coach. Analysiere den folgenden Text auf sensible Inhalte wie Gesundheitsinformationen, politische Aussagen, emotionale Inhalte, Klarnamen, Finanzdaten oder Emojis mit verdeckter Bedeutung.

Erstelle eine strukturierte Antwort in dieser Form:

1. Erkannte Datenarten
- ...

2. Datenschutz-Risiko
- Ampel: 🟢, 🟡 oder 🔴

3. Bedeutung der gefundenen Elemente
- ...

4. achtung.live-Empfehlung (empathisch & konkret)
- ...

5. Tipp: 1 sinnvoller Rewrite-Vorschlag
- ...

6. Quelle (nur wenn relevant)
- ...

Emoji-Analyse:
- Falls Emojis enthalten sind, gib deren Bedeutung mit Link aus.

Antworte in der Sprache: {language.upper()}
"""
            },
            {
                "role": "user",
                "content": user_input
            }
        ]

        response = client.chat.completions.create(
            model="gpt-4",
            messages=messages,
            temperature=0.6,
            max_tokens=800
        )

        raw_output = response.choices[0].message.content.strip()

        # Links extrahieren & prüfen
        found_links = extract_links(raw_output)
        link_results = check_links_status(found_links)

        final_output = raw_output + "\n\n🌐 Linkprüfung:\n" + "\n".join(link_results)
        if emoji_analysis:
            final_output += "\n\n🧩 Emoji-Analyse:\n" + "\n".join(emoji_analysis)

        log_debug(f"✅ GPT-Antwort erfolgreich empfangen.")

        return jsonify({ "result": final_output })

    except Exception as e:
        log_debug(f"❌ Fehler: {e}")
        return jsonify({ "error": str(e) }), 500

if __name__ == "__main__":
    app.run(debug=True)
