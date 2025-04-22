from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import openai
import re
import requests

app = Flask(__name__)
CORS(app)

openai.api_key = os.getenv("OPENAI_API_KEY")

# 🟢 Optionale Whitelist sicherer Domains
WHITELIST = ["bund.de", "datenschutz.org", "campact.de", "correctiv.org", "netzpolitik.org"]

def is_valid_link(url):
    try:
        domain_allowed = any(domain in url for domain in WHITELIST)
        if not domain_allowed:
            return False
        response = requests.head(url, timeout=5)
        return response.status_code == 200
    except:
        return False

def sanitize_links(text):
    # 🔎 Finde Markdown-Links: [Text](URL)
    links = re.findall(r'\[([^\]]+)]\(([^)]+)\)', text)

    for label, url in links:
        if is_valid_link(url):
            continue
        else:
            # ⛔️ Ersetze mit Hinweis bei toten oder unerlaubten Links
            replacement = f"❌ {label} – [Link nicht erreichbar oder unsicher]"
            text = text.replace(f"[{label}]({url})", replacement)

    return text

@app.route("/debug-gpt", methods=["POST"])
def debug_gpt():
    data = request.get_json()
    user_input = data.get("text", "")
    user_lang = data.get("lang", "de")

    # 💬 GPT PROMPT mit Sprachwahl
    prompt = f"""
Du bist ein Datenschutz-Experte mit Fokus auf Textsicherheit und emotional sensible Inhalte. Analysiere den folgenden Text auf datenschutzrechtlich kritische Informationen (z. B. Namen, Symptome, Diagnosen, Meinungen, Emojis, etc.):

Antworte bitte strukturiert mit den folgenden Abschnitten:

**Erkannte Datenarten:**  
[Liste]

**Datenschutz-Risiko:**  
🟢 / 🟡 / 🔴 (Ampel nach Sensibilität)

**Bedeutung:**  
[Kurze Einschätzung, was das Problem ist]

**achtung.live-Empfehlung:**  
[Hinweis, wie man das Problem vermeiden kann – empathisch formuliert]

**Tipp:**  
[Rewrite-Vorschlag oder konkreter Hinweis]

**Quelle:**  
[Füge 1–2 seriöse Quellen per Markdown-Link hinzu]

Sprache: {user_lang.upper()}
Hier ist der zu prüfende Text:
\"\"\"{user_input}\"\"\"
"""

    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[{ "role": "user", "content": prompt }],
            temperature=0.7,
            max_tokens=1000,
        )

        gpt_output = response.choices[0].message.content.strip()
        sanitized_output = sanitize_links(gpt_output)

        return jsonify({
            "gpt_output": sanitized_output
        })

    except Exception as e:
        return jsonify({ "error": str(e) }), 500

if __name__ == "__main__":
    app.run(debug=True)
