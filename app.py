import re
import requests
from flask import Flask, request, jsonify
from flask_cors import CORS
import openai
import os

app = Flask(__name__)
CORS(app)

openai.api_key = os.getenv("OPENAI_API_KEY")

# ⚠️ Spam-/Phishing-Domains (kann regelmäßig erweitert/automatisiert werden)
BLACKLISTED_DOMAINS = [
    "phishingsite.com",
    "malware-badlink.net",
    "example-hack.ru",
    "dangerous-link.xyz"
]

# 🔍 Linkscanner mit Domainprüfung
def check_links_in_text(text):
    links = re.findall(r'(https?://[^\s]+)', text)
    results = []
    for link in links:
        domain = re.sub(r"https?://(www\.)?", "", link).split("/")[0].lower()
        status = ""
        if domain in BLACKLISTED_DOMAINS:
            status = "🔴 Blockiert (bekannte Spam-/Phishing-Domain)"
        else:
            try:
                resp = requests.head(link, timeout=3)
                if resp.status_code == 200:
                    status = "🟢 Erreichbar"
                else:
                    status = f"🟡 Antwort mit Statuscode: {resp.status_code}"
            except:
                status = "🔴 Nicht erreichbar"
        results.append({"url": link, "status": status})
    return results

@app.route("/debug-gpt", methods=["POST"])
def debug_gpt():
    data = request.get_json()
    user_input = data.get("text", "")
    language = data.get("language", "de")

    # Linkprüfung
    checked_links = check_links_in_text(user_input)

    # GPT-Prompt (vereinfachtes Beispiel)
    gpt_prompt = f"""
Du bist ein Datenschutz-Coach. Analysiere den folgenden Text auf sensible Daten und Emojis mit Kontext.
Gib verständliche Empfehlungen, eine Datenschutz-Risiko-Ampel und einen Rewrite-Tipp für Laien.
Text: \"\"\"{user_input}\"\"\"
Sprache: {language}
"""

    try:
        response = openai.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": gpt_prompt}],
            temperature=0.7
        )
        gpt_text = response.choices[0].message.content.strip()
        return jsonify({
            "gpt_output": gpt_text,
            "link_check": checked_links
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)
