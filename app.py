from flask import Flask, request, jsonify
from flask_cors import CORS
from openai import OpenAI
import os
import json
import re
import requests

app = Flask(__name__)
CORS(app)

# GPT-Client (ab openai>=1.0.0)
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Vertrauenswürdige Quellen aus JSON-Datei laden
try:
    with open("trusted_links.json", "r") as f:
        trusted_links = json.load(f)
    print(f"✅ {len(trusted_links)} vertrauenswürdige Links geladen.")
except Exception as e:
    print(f"⚠️ trusted_links.json konnte nicht geladen werden: {e}")
    trusted_links = []

# Linkscanner prüft, ob ein Link gültig ist (Statuscode 200)
def check_link_status(url):
    try:
        response = requests.head(url, timeout=3)
        return response.status_code == 200
    except Exception:
        return False

@app.route("/analyze", methods=["POST"])
def analyze():
    data = request.get_json()
    user_text = data.get("text", "")
    language = data.get("language", "de")

    prompt = f"""
Du bist ein KI-gestützter Datenschutz-Coach für die Plattform achtung.live. Prüfe den folgenden Text auf datenschutzsensible Inhalte, politische oder medizinische Aussagen, Emoji-Bedeutung, Links oder potenzielle Risiken.

Beurteile und antworte im folgenden strukturierten Format in der gewählten Sprache ({language}):

**Erkannte Datenarten:**  
[Auflistung]

**Datenschutz-Risiko:**  
🟢 Unbedenklich  
🟡 Achtung! Mögliches Risiko  
🔴 Kritisch – so nicht senden!

**Bedeutung der gefundenen Elemente:**  
[Kontextbeschreibung inkl. Emoji- oder Linkdeutung]

**achtung.live-Empfehlung:**  
[Empathische, datenschutzfreundliche Empfehlung]

**Tipp:**  
[Konkreter Rewrite oder Sicherheitshinweis – gerne mit Quelle]

**Quelle:**  
[Seriöse Quelle mit Link – z. B. Campact, netzpolitik.org, BSI, etc.]

Hier ist der zu analysierende Text:
\"\"\"{user_text}\"\"\"
    """

    try:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "Du bist ein verantwortungsvoller Datenschutz-Coach."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.6,
            max_tokens=1000
        )
        gpt_output = response.choices[0].message.content.strip()

        # Verlinkte URLs extrahieren und auf Gültigkeit prüfen
        urls = re.findall(r'https?://[^\s\)]+', gpt_output)
        verified_output = gpt_output

        for url in urls:
            if url not in trusted_links or not check_link_status(url):
                verified_output = verified_output.replace(url, f"[⚠️ Link nicht verfügbar oder unsicher]")

        return jsonify({
            "gpt_raw": verified_output,
            "status": "success"
        })

    except Exception as e:
        return jsonify({
            "error": str(e),
            "status": "failed"
        }), 500

if __name__ == "__main__":
    app.run(debug=True)
