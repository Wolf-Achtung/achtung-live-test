from flask import Flask, request, jsonify
from flask_cors import CORS
from openai import OpenAI
import os
import json
import re
import requests

app = Flask(__name__)
CORS(app)

# OpenAI-Client (ab openai>=1.0.0)
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Lade Emoji-Datenbank
with open("emojiDatabase.json", "r", encoding="utf-8") as f:
    emoji_db = json.load(f)

# Lade vertrauenswürdige Quellen
try:
    with open("trusted_links.json", "r", encoding="utf-8") as f:
        trusted_links = json.load(f)
except Exception as e:
    trusted_links = []
    print("⚠️ trusted_links.json konnte nicht geladen werden:", e)

# Extrahiere Links aus Text
def extract_links(text):
    return re.findall(r'https?://\S+', text)

# Linkcheck mit Statuscode 200
def check_links(link_list):
    results = []
    for url in link_list:
        try:
            response = requests.head(url, timeout=5)
            results.append({
                "url": url,
                "status": "✅ erreichbar" if response.status_code == 200 else "⚠️ nicht erreichbar"
            })
        except Exception:
            results.append({
                "url": url,
                "status": "❌ Fehler bei Prüfung"
            })
    return results

# Emoji-Kontext prüfen
def analyze_emojis(text):
    found = []
    for emoji, info in emoji_db.items():
        if emoji in text:
            found.append({
                "emoji": emoji,
                "bedeutung": info.get("bedeutung", "Keine Beschreibung"),
                "kontext": info.get("kontext", "Unbekannt"),
                "quelle": info.get("quelle", "Keine Quelle")
            })
    return found

# Trusted Link-Vorschlag basierend auf Kategorie
def get_trusted_link(kategorie):
    for item in trusted_links:
        if item.get("kategorie") == kategorie:
            return item.get("link")
    return None

# API-Endpunkt
@app.route("/analyze", methods=["POST"])
def analyze():
    try:
        data = request.get_json()
        user_input = data.get("text", "")
        lang = data.get("language", "de")

        # GPT-Prompt zusammenstellen
        system_prompt = (
            "Du bist ein sensibler, verantwortungsvoller Datenschutz-Coach. "
            "Analysiere den folgenden Text auf datenschutzrechtlich kritische Inhalte, insbesondere:\n"
            "- Gesundheitsdaten\n- Namen\n- berufliche Details\n- politische Meinungen\n"
            "- finanzielle Daten\n- Emojis mit verdeckter Bedeutung\n\n"
            "Gib folgende Abschnitte zurück:\n\n"
            "1. Erkannte Datenarten\n"
            "2. Datenschutz-Risiko (Ampel: 🟢, 🟡, 🔴)\n"
            "3. Bedeutung der gefundenen Elemente\n"
            "4. achtung.live-Empfehlung (empathisch & konkret)\n"
            "5. Tipp: 1 sinnvoller Rewrite-Vorschlag\n"
            "6. Quelle (nur wenn relevant)"
        )

        # OpenAI GPT-Aufruf (Chat-Modell)
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_input}
            ],
            temperature=0.7,
            max_tokens=1000
        )

        gpt_response = response.choices[0].message.content.strip()

        # Emoji-Analyse
        emoji_infos = analyze_emojis(user_input)

        # Linkanalyse
        links = extract_links(user_input)
        link_infos = check_links(links)

        return jsonify({
            "gpt_response": gpt_response,
            "emojis": emoji_infos,
            "links": link_infos
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)
