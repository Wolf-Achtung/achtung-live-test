from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import openai
import re
import requests

app = Flask(__name__)
CORS(app)

openai.api_key = os.getenv("OPENAI_API_KEY")

# ✅ Whitelist für vertrauenswürdige Quellen
WHITELIST = [
    "bund.de",
    "datenschutz.org",
    "campact.de",
    "correctiv.org",
    "netzpolitik.org"
]

# 🔍 Link-Prüfung
def is_valid_link(url):
    try:
        allowed = any(domain in url for domain in WHITELIST)
        if not allowed:
            return False
        response = requests.head(url, timeout=5)
        return response.status_code == 200
    except:
        return False

# 🧼 Ersetze defekte Links in GPT-Antwort
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

    # 📌 GPT-Prompt mit Emoji-Kontext
    prompt = f"""
Du bist ein Datenschutz- und Kommunikationsanalyst. Untersuche den folgenden Text auf sensible Inhalte, einschließlich medizinischer, emotionaler, beruflicher oder politischer Natur. Achte auch auf Emojis, die möglicherweise versteckte Bedeutungen tragen, z. B. politische Symbolik (💙, 🐸), psychologische Andeutungen oder Szenecodes.

Analysiere, ob solche Emojis mit politischen Parteien, Verschwörungstheorien, extremistischen Gruppen oder anderen kritischen Bedeutungen assoziiert werden.

Antworte strukturiert in folgenden Abschnitten (in Markdown):

**Erkannte Datenarten:**  
[Kurze Liste: z. B. Name, politische Meinung, Emoji-Kontext]

**Datenschutz-Risiko:**  
🟢 / 🟡 / 🔴

**Bedeutung:**  
Erläutere, warum diese Inhalte kritisch sein könnten – inklusive Emoji-Erklärung, wer diese typischerweise nutzt, und wo sie problematisch wirken können.

**achtung.live-Empfehlung:**  
Was sollte der/die Nutzer:in beachten oder ändern?

**Tipp:**  
Konkreter Rewrite-Vorschlag (anonymisierend, datensparsam)

**Quelle:**  
Mind. 1 seriöser Link in Markdown – z. B. Campact, Correctiv, Netzpolitik etc.

Sprache: {user_lang.upper()}

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

        # 🪵 Log für Debug-Zwecke
        print("\n🔍 GPT-Rohantwort:")
        print(gpt_output)

        # 🔗 Linkprüfung
        checked_output = sanitize_links(gpt_output)

        return jsonify({
            "gpt_output": checked_output
        })

    except Exception as e:
        print("\n❌ GPT-Fehler:", str(e))
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)
