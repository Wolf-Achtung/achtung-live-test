from flask import Flask, request, jsonify
from flask_cors import CORS
import os
from openai import OpenAI

app = Flask(__name__)
CORS(app)

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

@app.route("/debug-gpt", methods=["POST"])
def debug_gpt():
    data = request.get_json()
    user_input = data.get("text", "")
    lang = data.get("lang", "de")  # fallback auf Deutsch

    language_intro = {
        "de": "Sprache: Deutsch",
        "en": "Language: English",
        "fr": "Langue : Français"
    }.get(lang, "Sprache: Deutsch")

    prompt = f"""
# achtung.live Prompt v2.2 – mehrsprachig

🛡️ Du bist achtung.live – ein empathischer KI-Coach für digitale Sicherheit, spezialisiert auf Datenschutz, sensible Inhalte und Emoji-Risiken.

{language_intro}

Bitte analysiere den folgenden Text in der gewählten Sprache auf:
- Gesundheitsdaten, Diagnosen, Medikamente
- politische Meinungen, Symbolik oder Gruppenzugehörigkeit
- Emojis mit kodierter oder kontroverser Bedeutung

Wenn Emojis enthalten sind:
→ Erkläre, welche Gruppierung oder Szene sie nutzt (z. B. AfD, Alt-Right)
→ In welchem Kontext (Plattformen, Symbolik, Kommunikation)
→ Gib mindestens ein Beispiel mit Quelle

📌 Antworte in der gewählten Sprache mit folgendem Format:

**Erkannte Datenarten:**  
...

**Datenschutz-Risiko:**  
🟢 Unbedenklich  
🟡 Achtung! Mögliches Risiko  
🔴 Kritisch – nicht versenden!

**Bedeutung:**  
...

**achtung.live-Empfehlung:**  
...

**Tipp:**  
...

**Quelle:**  
[z. B. Campact – Emoji-Codes](https://www.campact.de/emoji-codes/)

Text zur Analyse:
\"\"\"{user_input}\"\"\"
    """

    try:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=1000
        )
        gpt_output = response.choices[0].message.content.strip()
        return jsonify({ "gpt_output": gpt_output })
    except Exception as e:
        return jsonify({ "gpt_output": f"❌ GPT-Fehler:\n\n{str(e)}" }), 500

if __name__ == "__main__":
    app.run(debug=True)
