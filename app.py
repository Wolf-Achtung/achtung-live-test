from flask import Flask, request, jsonify
from flask_cors import CORS
import openai
import os
import json
import re

app = Flask(__name__)
CORS(app)

# OpenAI-Key aus Umgebungsvariable
openai.api_key = os.getenv("OPENAI_API_KEY")

# Emoji-Datenbank laden
try:
    with open("emojiDatabase.json", encoding="utf-8") as f:
        emoji_db = json.load(f)
except Exception as e:
    emoji_db = {}
    print(f"⚠️ emojiDatabase.json konnte nicht geladen werden: {e}")

# Trusted Links laden
try:
    with open("trusted_links.json", encoding="utf-8") as f:
        trusted_links = json.load(f)
except Exception as e:
    trusted_links = []
    print(f"⚠️ trusted_links.json konnte nicht geladen werden: {e}")

# 🔍 Linkprüfung gegen Liste erlaubter Domains
def get_verified_source(text):
    for link in trusted_links:
        if link.get("keyword", "").lower() in text.lower():
            return link.get("url")
    return None

# 🧠 Emoji-Kontext abrufen
def analyze_emojis(text):
    findings = []
    for emoji_char, data in emoji_db.items():
        if emoji_char in text:
            findings.append({
                "emoji": emoji_char,
                "bedeutung": data.get("bedeutung", "Keine Bedeutung gefunden."),
                "kontext": data.get("kontext", "Kein Kontext vorhanden."),
                "quelle": data.get("quelle", ""),
                "risiko": data.get("risiko", "🟢")
            })
    return findings

# 💬 GPT-Auswertung
@app.route("/analyze", methods=["POST"])
def analyze():
    data = request.get_json()
    user_input = data.get("text", "")

    # Emojis analysieren
    emoji_analysis = analyze_emojis(user_input)

    # GPT-Prompt definieren
    prompt = f"""
Du bist ein Datenschutz- und Ethik-Coach. Analysiere folgenden Text auf sensible Daten, Emojis und risikobehaftete Inhalte.

Text: \"\"\"{user_input}\"\"\"

1. Erkannte Datenarten
2. Datenschutz-Risiko (🟢/🟡/🔴)
3. Bedeutung der gefundenen Elemente
4. achtung.live-Empfehlung
5. Tipp: 1 sinnvoller Rewrite-Vorschlag
6. Quelle: seriöse, verlinkbare Website, falls vorhanden (z. B. datenschutz.org)

Antwort strukturiert ausgeben.
"""

    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=800
        )
        gpt_text = response["choices"][0]["message"]["content"]

        # Emojis als Ergänzung einfügen
        emoji_extras = ""
        for item in emoji_analysis:
            quelle_link = f"[Mehr dazu]({item['quelle']})" if item["quelle"] else "Keine Quelle vorhanden."
            emoji_extras += (
                f"\n🔍 Emoji erkannt: {item['emoji']}\n"
                f"- Bedeutung: {item['bedeutung']}\n"
                f"- Kontext: {item['kontext']}\n"
                f"- Datenschutz-Risiko: {item['risiko']}\n"
                f"- Quelle: {quelle_link}\n"
            )

        # Quelle automatisch validieren
        verified = get_verified_source(gpt_text)
        if verified:
            gpt_text += f"\n\n**🔗 Verifizierte Quelle:** [{verified}]({verified})"

        return jsonify({ "result": gpt_text.strip(), "emojis": emoji_analysis })

    except Exception as e:
        return jsonify({ "error": str(e) }), 500

if __name__ == "__main__":
    app.run(debug=True)
