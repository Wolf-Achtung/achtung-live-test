import os
import json
import re
import requests
from flask import Flask, request, jsonify
from flask_cors import CORS
from openai import OpenAI

# Initialisierung
app = Flask(__name__)
CORS(app)

# OpenAI-Key aus Umgebungsvariablen
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Vertrauenswürdige Links laden (optional)
trusted_links = []
try:
    with open("trusted_links.json", "r") as f:
        trusted_links = json.load(f)
    print(f"✅ {len(trusted_links)} vertrauenswürdige Links geladen.")
except Exception as e:
    print(f"⚠️ trusted_links.json konnte nicht geladen werden: {e}")

# Funktion: GPT-Prompt mit Sprachoption
def build_prompt(text, language):
    intro = {
        "de": "Du bist ein Datenschutz-Coach mit Schwerpunkt auf DSGVO, medizinische, berufliche, emotionale und behördliche Inhalte.",
        "en": "You are a data protection coach specializing in GDPR, medical, professional, emotional, and official content.",
        "fr": "Vous êtes un coach en protection des données spécialisé dans le RGPD, les contenus médicaux, professionnels, émotionnels et administratifs."
    }

    rewrite_info = {
        "de": "Wenn sensible Inhalte erkannt werden, beschreibe sie kurz und gib einen Rewrite-Vorschlag.",
        "en": "If sensitive content is found, describe it briefly and offer a rewrite suggestion.",
        "fr": "Si du contenu sensible est détecté, décris-le brièvement et propose une reformulation."
    }

    return f"""{intro.get(language, intro['de'])}
Analysiere den folgenden Text auf:
- Persönliche & medizinische Informationen
- Emojis mit möglicher Symbolik
- Vertrauliche Daten (z. B. Berufliches, Finanzen)
- Politisch oder emotional aufgeladene Aussagen
- Links oder Webseiten (auf Vertrauenswürdigkeit prüfen)

{rewrite_info.get(language, rewrite_info['de'])}

Text:
\"\"\"{text}\"\"\"
"""

# Funktion: Linkscanner (prüft HTTP-Status)
def extract_links(text):
    return re.findall(r'https?://\S+', text)

def validate_links(links):
    validated = []
    for url in links:
        try:
            resp = requests.head(url, timeout=5, allow_redirects=True)
            if resp.status_code == 200:
                validated.append({"url": url, "status": "ok"})
            else:
                validated.append({"url": url, "status": f"fehlerhaft ({resp.status_code})"})
        except Exception:
            validated.append({"url": url, "status": "nicht erreichbar"})
    return validated

# API-Endpunkt
@app.route("/analyze", methods=["POST"])
def analyze():
    try:
        data = request.get_json()
        user_text = data.get("text", "")
        lang = data.get("language", "de")

        if not user_text.strip():
            return jsonify({"error": "Text ist leer."}), 400

        prompt = build_prompt(user_text, lang)

        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "Du bist ein Datenschutz-Experte."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=800
        )

        gpt_output = response.choices[0].message.content.strip()
        found_links = extract_links(gpt_output)
        validated_links = validate_links(found_links)

        return jsonify({
            "output": gpt_output,
            "validated_links": validated_links
        })

    except Exception as e:
        print("❌ GPT-Fehler:", e)
        return jsonify({ "error": str(e) }), 500

# Startpunkt
if __name__ == "__main__":
    app.run(debug=True)
