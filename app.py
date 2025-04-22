from flask import Flask, request, jsonify
from flask_cors import CORS
from openai import OpenAI
import os
import json
import requests

app = Flask(__name__)
CORS(app)

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Trusted Links
try:
    with open("trusted_links.json", "r") as f:
        trusted_links = json.load(f)
except Exception as e:
    print(f"⚠️ trusted_links.json konnte nicht geladen werden: {e}")
    trusted_links = []

# Helper: Linkscanner
def scan_links(text):
    import re
    urls = re.findall(r'(https?://\S+)', text)
    results = []
    for url in urls:
        try:
            res = requests.head(url, timeout=5)
            status = "✅ erreichbar" if res.status_code == 200 else f"⚠️ Status: {res.status_code}"
        except:
            status = "❌ nicht erreichbar"
        results.append({"url": url, "status": status})
    return results

@app.route("/analyze", methods=["POST"])
def analyze():
    data = request.get_json()
    user_input = data.get("text", "")
    lang = data.get("language", "de")

    prompt = f"""
Sprache: {lang.upper()}
Sie sind ein Datenschutz-Analysesystem, spezialisiert auf sensible Inhalte wie:

- Medizinische Informationen (Diagnosen, Medikamente)
- Emotionale Aussagen (z. B. Depression)
- Identitätsdaten (Name, Adresse, Arzt)
- Emojis mit kultureller/politischer Bedeutung
- Verlinkte externe Inhalte (URLs)

Analysieren Sie den folgenden Text auf Risiken.
1. **Erkannte Datenarten**
2. **Datenschutz-Risiko** (Ampel: 🟢🟡🔴)
3. **Bedeutung der gefundenen Elemente**
4. **achtung.live-Empfehlung** (konkret, empathisch, professionell)
5. **Tipp: 1 sinnvoller Rewrite-Vorschlag**
6. **Quelle** (falls Emoji oder rechtlicher Kontext)

Geben Sie strukturiertes, hilfreiches Feedback zurück.
Text:
\"\"\"{user_input}\"\"\"
"""

    try:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.6,
        )
        gpt_text = response.choices[0].message.content.strip()
        links = scan_links(gpt_text)
        return jsonify({"gpt_output": gpt_text, "link_check": links})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/")
def root():
    return "🚀 Achtung.live API bereit"

if __name__ == "__main__":
    app.run(debug=True)
