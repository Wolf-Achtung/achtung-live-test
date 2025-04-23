from flask import Flask, request, jsonify
from flask_cors import CORS
from openai import OpenAI
import os
import json
import requests

app = Flask(__name__)
CORS(app)

# Lade OpenAI-Client (ab Version 1.0.0+)
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Lade Emoji-Datenbank
try:
    with open("emojiDatabase.json", "r", encoding="utf-8") as f:
        emoji_database = json.load(f)
except Exception as e:
    emoji_database = {}
    print("❌ Emoji-Datenbank konnte nicht geladen werden:", e)

@app.route("/analyze", methods=["POST"])
def analyze():
    data = request.get_json()
    user_input = data.get("text", "")

    # Emoji-Analyse
    emoji_analysis = []
    for emoji, meta in emoji_database.items():
        if emoji in user_input:
            emoji_analysis.append({
                "symbol": emoji,
                "title": meta.get("title", ""),
                "text": meta.get("text", ""),
                "group": meta.get("group", ""),
                "link": meta.get("link", "")
            })

    # Prompt für GPT
    prompt = f"""
Sie sind ein empathischer Datenschutz-Coach. Analysieren Sie den folgenden Text auf:

1. Erkannte Datenarten
2. Datenschutz-Risiko (Ampel: 🟢, 🟡, 🔴)
3. Bedeutung der gefundenen Elemente
4. achtung.live-Empfehlung (empathisch & konkret)
5. Tipp: 1 sinnvoller Rewrite-Vorschlag
6. Quelle (nur wenn relevant)

Text:
\"\"\"{user_input}\"\"\"
"""

    try:
        completion = client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
        )
        response = completion.choices[0].message.content.strip()

        return jsonify({
            "feedback": response,
            "emoji_analysis": emoji_analysis
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)
