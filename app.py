from flask import Flask, request, jsonify
from flask_cors import CORS
import os, json, uuid, datetime
from openai import OpenAI

app = Flask(__name__)
CORS(app)

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# 🔒 Logfile-Konfiguration
LOG_FILE = "logs/audit_log.jsonl"  # JSONL = eine Zeile pro Logeintrag

@app.route("/debug-gpt", methods=["POST"])
def debug_gpt():
    data = request.get_json()
    user_input = data.get("text", "")
    lang = data.get("lang", "de")  # Fallback = Deutsch

    timestamp = datetime.datetime.utcnow().isoformat()
    session_id = str(uuid.uuid4())

    # 🌍 Sprach-Markierung
    language_intro = {
        "de": "Sprache: Deutsch",
        "en": "Language: English",
        "fr": "Langue : Français"
    }.get(lang, "Sprache: Deutsch")

    # 🧠 Mehrsprachiger Prompt mit Emoji-, Risiko- und Rewrite-Analyse
    prompt = f"""
# achtung.live Audit-Prompt (Multilingual + Emojis + Rewrite)

{language_intro}

Bitte analysiere den folgenden Text auf:
- sensible Gesundheitsdaten, Diagnosen, Medikamente
- politische Aussagen oder Emojis mit Symbolcharakter
- doppeldeutige Emojis (z. B. 💙, 🐸, 🧿)

Wenn Emojis enthalten sind:
→ Erkläre ihre Bedeutung in Communitys (AfD, Alt-Right, Queer-Szene etc.)
→ Gib ein konkretes Beispiel
→ Gib eine Quelle (z. B. [Campact – Emoji-Codes](https://campact.de/emoji-codes/))

Antworte im folgenden Format:

**Erkannte Datenarten:**  
...

**Datenschutz-Risiko:**  
🟢 Unbedenklich  
🟡 Mögliches Risiko  
🔴 Kritisch – nicht versenden!

**Bedeutung:**  
...

**achtung.live-Empfehlung:**  
...

**Tipp:**  
(Rewrite-Vorschlag für sicheren Ausdruck)

**Quelle:**  
[z. B. Campact – Emoji-Codes](https://campact.de/emoji-codes/)

Text zur Analyse:
\"\"\"{user_input}\"\"\"
"""

    try:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[{ "role": "user", "content": prompt }],
            temperature=0.7,
            max_tokens=1000
        )

        gpt_output = response.choices[0].message.content.strip()

        # 🔍 Audit-Log-Eintrag vorbereiten
        log_entry = {
            "timestamp": timestamp,
            "session_id": session_id,
            "language": lang,
            "input": user_input,
            "gpt_output": gpt_output
        }

        os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)
        with open(LOG_FILE, "a", encoding="utf-8") as logfile:
            logfile.write(json.dumps(log_entry, ensure_ascii=False) + "\n")

        return jsonify({ "gpt_output": gpt_output })

    except Exception as e:
        return jsonify({ "gpt_output": f"❌ GPT-Fehler:\n\n{str(e)}" }), 500

if __name__ == "__main__":
    app.run(debug=True)
