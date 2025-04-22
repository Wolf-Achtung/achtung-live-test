from flask import Flask, request, jsonify
from flask_cors import CORS
import openai
import os
import json
import requests

app = Flask(__name__)
CORS(app)

# OpenAI-API-Key aus Umgebungsvariable
openai.api_key = os.getenv("OPENAI_API_KEY")

# ✅ Fallback-freundlich geladen: trusted_links.json
try:
    with open("trusted_links.json", "r", encoding="utf-8") as f:
        trusted_links = json.load(f)
except Exception as e:
    print("⚠️ Fehler beim Laden von trusted_links.json:", e)
    trusted_links = {}

# ✅ Prüft, ob ein Link erreichbar ist
def check_link_reachability(url):
    try:
        response = requests.get(url, timeout=5)
        return response.status_code == 200
    except Exception:
        return False

# ✅ Ersetzt Labels durch anklickbare Links – oder Warnung
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

@app.route("/debug-gpt", methods=["POST"])
def debug_gpt():
    data = request.get_json()
    user_input = data.get("text", "")
    lang = data.get("lang", "de")  # Standard: Deutsch

    # 🔁 GPT-Prompt mit Emoji- und Datenschutzanalyse
    prompt = f"""
Sie sind ein datenschutzsensibler KI-Coach, spezialisiert auf medizinische, berufliche und emotionale Online-Kommunikation. Ihre Aufgabe ist es, den folgenden Text auf sensible Inhalte zu prüfen und passende datenschutzsichere Vorschläge zu machen.

Achten Sie besonders auf:
- persönliche Angaben
- gesundheitliche Informationen
- emotionale oder politische Meinungen
- Emojis mit symbolischer Bedeutung
- vertrauliche Links

Identifizieren Sie:
1. **Erkannte Datenarten**
2. **Datenschutz-Risiko** (Ampel: 🟢/🟡/🔴)
3. **Bedeutung** der gefundenen Elemente
4. **achtung.live-Empfehlung**
5. **Tipp**: 1 sinnvoller Rewrite-Vorschlag (anonymisiert, klar, datenschutzkonform)
6. **Quelle**: Falls Emojis oder Begriffe politisch oder missverständlich verwendet werden, fügen Sie seriöse Quellen bei (z. B. [Campact](https://blog.campact.de/...)) – **bitte als klickbare Markdown-Links**

Sprache: {lang.upper()}  
Hier ist der zu analysierende Text:
\"\"\"{user_input}\"\"\"
    """

    try:
        # 🔁 GPT-4-Kommunikation über Chat-Completion (ab OpenAI >= 1.0.0)
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                { "role": "system", "content": "Du bist ein sensibler, datenschutzfreundlicher Rewrite-Assistent." },
                { "role": "user", "content": prompt }
            ],
            temperature=0.6,
            max_tokens=1000
        )

        gpt_output = response.choices[0].message["content"].strip()
        gpt_output = enrich_links_with_check(gpt_output)

        return jsonify({
            "gpt_output": gpt_output
        })

    except Exception as e:
        print("❌ GPT-Fehler:", e)
        return jsonify({ "error": str(e) }), 500

if __name__ == "__main__":
    app.run(debug=True)
