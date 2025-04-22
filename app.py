from flask import Flask, request, jsonify
from flask_cors import CORS
import os, json, uuid, datetime
from openai import OpenAI

app = Flask(__name__)
CORS(app)

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# 🔐 DSGVO-konformes Audit-Log
LOG_FILE = "logs/audit_log.jsonl"

@app.route("/debug-gpt", methods=["POST"])
def debug_gpt():
    data = request.get_json()
    user_input = data.get("text", "")
    lang = data.get("lang", "de")  # fallback
    timestamp = datetime.datetime.utcnow().isoformat()
    session_id = str(uuid.uuid4())

    # 🔤 Sprachpräfix
    language_intro = {
        "de": "Sprache: Deutsch",
        "en": "Language: English",
        "fr": "Langue : Français"
    }.get(lang, "Sprache: Deutsch")

    # 🎯 Audit-fähiger Prompt mit Rewrite & Emoji-Warnung
    prompt = f"""
# achtung.live Datenschutzanalyse (v2.3)
{language_intro}

Bitte analysieren Sie den folgenden Text auf:
- sensible Inhalte (Diagnosen, Medikamente, Namen, Adressen, Konten, intime Aussagen)
- politische Aussagen, Symbolik oder Emojis mit potenziell problematischem Hintergrund

Wenn Emojis enthalten sind:
→ Erklären Sie, ob sie harmlos oder politisch/ideologisch aufgeladen sind (z. B. 💙 = Sympathie, aber auch AfD-Code)
→ Geben Sie mind. 1 reale Quelle oder journalistische Referenz (z. B. Campact, Belltower.News)

Antwortstruktur:

**Erkannte Datenarten:**  
(Liste der Datenarten)

**Datenschutz-Risiko:**  
🟢 Unbedenklich  
🟡 Mögliches Risiko  
🔴 Kritisch – nicht versenden!

**Bedeutung:**  
(Kontext zur Gefahr oder Bedeutung)

**achtung.live-Empfehlung:**  
(Sicherheits-Tipp für User:innen)

**Tipp:**  
(Empfohlener Rewrite-Vorschlag – anonymisiert & bedeutungserhaltend)

**Quelle:**  
[Campact – Emoji-Codes](https://www.campact.de/emoji-codes/)  
[Belltower.News](https://www.belltower.news)

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

        # 🔍 JSONL-Log für Transparenz & Kontrolle
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
