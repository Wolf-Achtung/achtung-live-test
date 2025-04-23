from flask import Flask, request, jsonify
from flask_cors import CORS
from openai import OpenAI
import os
import re
import json
import requests

app = Flask(__name__)
CORS(app)

# GPT-Client mit aktuellem API-Modell
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Trusted Links laden
try:
    with open("trusted_links.json", "r") as f:
        trusted_links = json.load(f)
except Exception as e:
    print("⚠️ trusted_links.json konnte nicht geladen werden:", e)
    trusted_links = {}

# Emojis laden
try:
    with open("emojiDatabase.json", "r", encoding="utf-8") as f:
        emoji_db = json.load(f)
except Exception as e:
    print("⚠️ emojiDatabase.json konnte nicht geladen werden:", e)
    emoji_db = {}

# Linkscanner
def check_links(links):
    results = []
    for url in links:
        try:
            response = requests.get(url, timeout=5, allow_redirects=True)
            status = "✅ Link erreichbar" if response.status_code == 200 else f"❌ Fehlercode: {response.status_code}"
        except Exception:
            status = "❌ Link nicht erreichbar"
        results.append(f"{status}: {url}")
    return results

# Emojierkennung
def analyze_emojis(text):
    found = []
    for emoji, info in emoji_db.items():
        if emoji in text:
            found.append(f"{emoji}: {info['bedeutung']}")
    return found

# Trusted Quelle zur Kategorie
def get_trusted_link(topic):
    for k, v in trusted_links.items():
        if topic.lower() in k.lower():
            return f"[{v['name']}]({v['url']})"
    return "Keine verlässliche Quelle gefunden."

@app.route("/analyze", methods=["POST"])
def analyze():
    data = request.get_json()
    user_input = data.get("text", "")
    language = data.get("lang", "de")

    emojis = analyze_emojis(user_input)
    links = re.findall(r'(https?://\S+)', user_input)
    link_feedback = check_links(links) if links else []

    # GPT-Antwort generieren
    system_message = "Du bist ein empathischer Datenschutz-Coach. Analysiere sensibel, verständlich, konkret und warnend."

    prompt = f"""
Analysiere diesen Text aus datenschutzrechtlicher Sicht. Gliedere deine Antwort exakt in folgende 6 Punkte:

1. **Erkannte Datenarten** (z. B. Name, Adresse, Gesundheitsdaten, politische Aussagen)
2. **Datenschutz-Risiko** (Ampel: 🟢, 🟡, 🔴)
3. **Bedeutung der gefundenen Elemente** (Warum problematisch?)
4. **achtung.live-Empfehlung** (empathisch & konkret)
5. **Tipp: 1 sinnvoller Rewrite-Vorschlag** (sicher, empathisch, nutzbar)
6. **Quelle** (nur wenn relevant – ideal: DSGVO, BfDI, trusted_links.json)

Text: \"\"\"{user_input}\"\"\"
"""

    try:
        completion = client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "system", "content": system_message}, {"role": "user", "content": prompt}],
            temperature=0.6,
            max_tokens=800
        )
        raw_response = completion.choices[0].message.content

        # Emojis + Links ins Ergebnis einfügen
        if emojis:
            raw_response += "\n\n**🧩 Emoji-Analyse:**\n" + "\n".join(emojis)
        if link_feedback:
            raw_response += "\n\n**🌐 Linkprüfung:**\n" + "\n".join(link_feedback)

        return jsonify({
            "result": raw_response.strip(),
            "raw": raw_response
        })

    except Exception as e:
        return jsonify({ "error": str(e) }), 500

if __name__ == "__main__":
    app.run(debug=True)
