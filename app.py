from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import openai
import re
import requests

app = Flask(__name__)
CORS(app)

openai.api_key = os.getenv("OPENAI_API_KEY")

# ✅ Optionale Whitelist seriöser Domains
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
    # 🔍 Markdown-Link-Muster: [Label](URL)
    links = re.findall(r'\[([^\]]+)]\(([^)]+)\)', text)
    for label, url in links:
        if is_valid_link(url):
            continue
        else:
            # ⚠️ Ersetze mit Warnhinweis
            replacement = f"❌ {label} – [Link nicht erreichbar oder unsicher]"
            text = text.replace(f"[{label}]({url})", replacement)
    return text

@app.route("/debug-gpt", methods=["POST"])
def debug_gpt():
    data = request.get_json()
    user_input = data.get("text", "")
    user_lang = data.get("lang", "de")

    # 💬 GPT-Prompt mit Sprachwahl
    prompt = f"""
Du bist ein Datenschutz-Coach mit medizinischer, emotionaler und rechtlicher Sensibilität. Analysiere folgenden Text:

Gib eine strukturierte Rückmeldung mit folgenden Abschnitten:
**Erkannte Datenarten:**
**Datenschutz-Risiko:** (🟢/🟡/🔴)
**Bedeutung:**
**achtung.live-Empfehlung:**
**Tipp:** (Rewrite oder Hinweis)
**Quelle:** (als Markdown-Link)

Sprache der Antwort: {user_lang.upper()}

Hier ist der Text:
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

        # 🪵 Log in Railway anzeigen
        print("\n🔍 GPT-Rohantwort:")
        print(gpt_output)

        sanitized_output = sanitize_links(gpt_output)

        return jsonify({
            "gpt_output": sanitized_output
        })

    except Exception as e:
        print("\n❌ GPT-Fehler:", str(e))
        return jsonify({ "error": str(e) }), 500

if __name__ == "__main__":
    app.run(debug=True)
