from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import openai
import re
import requests

app = Flask(__name__)
CORS(app)

openai.api_key = os.getenv("OPENAI_API_KEY")

# 🔐 Whitelist für vertrauenswürdige Quellen
WHITELIST = [
    "bund.de",
    "datenschutz.org",
    "campact.de",
    "correctiv.org",
    "netzpolitik.org"
]

# 🔎 Prüft, ob ein Link erreichbar ist
def is_valid_link(url):
    try:
        allowed = any(domain in url for domain in WHITELIST)
        if not allowed:
            return False
        response = requests.head(url, timeout=5)
        return response.status_code == 200
    except:
        return False

# 🧼 Bereinigt GPT-Antwort von toten oder unerwünschten Links
def sanitize_links(text):
    links = re.findall(r'\[([^\]]+)]\(([^)]+)\)', text)
    for label, url in links:
        if not is_valid_link(url):
            text = text.replace(f"[{label}]({url})", f"❌ {label} – Link nicht verfügbar oder unsicher")
    return text

@app.route("/debug-gpt", methods=["POST"])
def debug_gpt():
    data = request.get_json()
    user_input = data.get("text", "")
    user_lang = data.get("lang", "de")

    # 📌 GPT-Prompt: erweitert für Emoji-Kontext & politische Symbolik
    prompt = f"""
Du bist ein KI-System für Datenschutz und digitale Symbolanalyse. Untersuche den folgenden Text auf datenschutzrelevante Inhalte, politische Meinungen, versteckte Symbolik (z. B. Emojis) sowie emotionale oder sensible Aussagen.

Achte besonders auf Emojis mit politischem oder gesellschaftlichem Kontext. Beispiel: 💙 wird in deutschen Telegram-Kanälen oft zur Unterstützung der AfD verwendet. Nenne solche Assoziationen explizit und liefere, wenn möglich, eine Quelle.

Strukturiere deine Antwort in folgenden Abschnitten (Markdown-Format):

**Erkannte Datenarten:**  
Welche sensiblen oder politisch aufgeladenen Informationen enthält der Text?

**Datenschutz-Risiko:**  
🟢 Unbedenklich / 🟡 Mögliches Risiko / 🔴 Kritisch

**Bedeutung:**  
Was bedeutet das Emoji oder die Aussage im Kontext? Welche Gruppen nutzen es?

**achtung.live-Empfehlung:**  
Konkreter Hinweis, was der/die Nutzer:in beachten sollte – auch bei vermeintlich harmlosen Symbolen.

**Tipp:**  
Rewrite oder konkreter Hinweis, wie der Text sicherer oder neutraler formuliert werden kann.

**Quelle:**  
Mindestens ein verlässlicher Link zu Hintergrundinformationen, z. B.:
- https://blog.campact.de/2024/03/geheime-codes-von-rechtsextremen-online-emoji-hashtag/
- https://correctiv.org/aktuelles/recherche/2022/05/20/emoji-code-rechtsradikale-symbole/

Antwortsprache: {user_lang.upper()}

Text zur Analyse:
\"\"\"{user_input}\"\"\"
"""

    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=1000,
        )

        gpt_output = response.choices[0].message.content.strip()

        # 📋 Logausgabe zur Kontrolle
        print("\n🔍 GPT-Rohantwort:")
        print(gpt_output)

        cleaned_output = sanitize_links(gpt_output)

        return jsonify({
            "gpt_output": cleaned_output
        })

    except Exception as e:
        print("\n❌ GPT-Fehler:", str(e))
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)
