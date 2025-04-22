from flask import Flask, request, jsonify
from flask_cors import CORS
import openai
import os
import json
import requests

app = Flask(__name__)
CORS(app)

openai.api_key = os.getenv("OPENAI_API_KEY")

# Trusted Links laden (z. B. DSGVO, Emojipedia etc.)
try:
    with open("trusted_links.json", "r", encoding="utf-8") as f:
        trusted_links = json.load(f)
except Exception as e:
    print("⚠️ trusted_links.json konnte nicht geladen werden:", e)
    trusted_links = {}

def check_link_reachability(url):
    try:
        response = requests.get(url, timeout=5)
        return response.status_code == 200
    except Exception:
        return False

def enrich_links_with_check(text):
    for key, info in trusted_links.items():
        label = info["label"]
        url = info["url"]
        if label in text:
            is_ok = check_link_reachability(url)
            if is_ok:
                replacement = f"[{label}]({url})"
            else:
                replacement = f"❌ [{label}]({url} – nicht erreichbar)"
            text = text.replace(label, replacement)
    return text

def format_gpt_response(text):
    sections = [
        ("Erkannte Datenarten", r"\*\*Erkannte Datenarten\*\*"),
        ("Datenschutz-Risiko", r"\*\*Datenschutz-Risiko\*\*"),
        ("Bedeutung", r"\*\*Bedeutung(?: der gefundenen Elemente)?\*\*"),
        ("achtung.live-Empfehlung", r"\*\*achtung\.live-Empfehlung\*\*"),
        ("Tipp", r"\*\*Tipp(?:\: 1 sinnvoller Rewrite-Vorschlag)?\*\*"),
        ("Quelle", r"\*\*Quelle\*\*")
    ]

    for label, marker in sections:
        text = text.replace(f"**{label}**", f'<span class="rubrik">{label}</span>')

    # Optional: "Vorschlag zum Kopieren" entfernen, wenn kein Rewrite enthalten ist
    if "Vorschlag zum Kopieren" in text and "Tipp" not in text:
        text = text.replace("Vorschlag zum Kopieren", "")
    return text

@app.route("/debug-gpt", methods=["POST"])
def debug_gpt():
    data = request.get_json()
    user_input = data.get("text", "")
    lang = data.get("lang", "de")

    prompt = f"""
Sie sind ein datenschutzsensibler Rewrite-Coach. Analysieren Sie den folgenden Text auf sensible Daten wie Gesundheitsangaben, politische Aussagen oder bedeutungsbeladene Emojis.

Bitte liefern Sie:
1. **Erkannte Datenarten**
2. **Datenschutz-Risiko** (🟢/🟡/🔴)
3. **Bedeutung der gefundenen Elemente**
4. **achtung.live-Empfehlung**
5. **Tipp: 1 sinnvoller Rewrite-Vorschlag**
6. **Quelle** (mit verifizierbarem Link)

Sprache: {lang.upper()}

Text:
\"\"\"{user_input}\"\"\"
    """

    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                { "role": "system", "content": "Du bist ein DSGVO-konformer Datenschutz- und Sprach-Coach." },
                { "role": "user", "content": prompt }
            ],
            temperature=0.6,
            max_tokens=1000
        )

        gpt_output = response.choices[0].message["content"].strip()
        gpt_output = enrich_links_with_check(gpt_output)
        gpt_output = format_gpt_response(gpt_output)

        return jsonify({ "gpt_output": gpt_output })

    except Exception as e:
        return jsonify({ "error": str(e) }), 500

if __name__ == "__main__":
    app.run(debug=True)
