from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import json
import re
import requests
from openai import OpenAI
from random import choice

app = Flask(__name__)
CORS(app)

# OpenAI-Client initialisieren
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Trusted Links laden
try:
    with open("trusted_links.json", "r") as f:
        trusted_links = json.load(f)
except Exception as e:
    print(f"⚠️ trusted_links.json konnte nicht geladen werden: {e}")
    trusted_links = []

def get_trusted_link():
    for _ in range(len(trusted_links)):
        link = choice(trusted_links)
        try:
            if requests.head(link["url"], timeout=5).status_code == 200:
                return f"[{link['name']}]({link['url']})"
        except:
            continue
    return "*Keine verlässliche Quelle verfügbar*"

@app.route("/analyze", methods=["POST"])
def analyze():
    data = request.get_json()
    user_input = data.get("text", "")
    lang = data.get("language", "de")

    prompt = f"""
Du bist ein Datenschutz-Coach mit medizinischem Feingefühl. Analysiere folgenden Text auf sensible Inhalte:

Text:
\"\"\"{user_input}\"\"\"

Identifiziere:
1. Welche Arten sensibler Daten kommen vor?
2. Wie hoch ist das Datenschutz-Risiko (Ampel: 🟢, 🟡, 🔴)?
3. Warum ist das riskant? (Begründung)
4. Welche Empfehlung gibst du?
5. Optional: 1 Rewrite-Vorschlag
6. Quelle: Empfohlener Link (wenn sinnvoll)

Antwort strukturiert im folgenden Format:

1. **Erkannte Datenarten**  
- [Liste der sensiblen Inhalte]

2. **Datenschutz-Risiko**  
- [Ampelsymbol]

3. **Bedeutung der gefundenen Elemente**  
- [Kurze Erklärung]

4. **achtung.live-Empfehlung**  
- [Empathische, klare Handlungsanweisung]

5. **Tipp: 1 sinnvoller Rewrite-Vorschlag**  
- "[Rewrite]"

6. **Quelle**  
- {get_trusted_link()}

Wichtig: Der Rewrite-Vorschlag soll dem User konkret helfen. Wenn keine Überarbeitung nötig ist, diesen Punkt weglassen.
"""

    try:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[{ "role": "user", "content": prompt }],
            temperature=0.7
        )
        result = response.choices[0].message.content
        return jsonify({ "result": result.strip() })
    except Exception as e:
        return jsonify({ "error": str(e) }), 500

if __name__ == "__main__":
    app.run(debug=True)
