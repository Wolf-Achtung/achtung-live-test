from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import openai

app = Flask(__name__)
CORS(app)

client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

@app.route("/debug-gpt", methods=["POST"])
def debug_gpt():
    data = request.get_json()
    user_input = data.get("text", "")

    prompt = f'''
#prompt-v1.8-emo-explain#temp0.7#max1000

🔐 Du bist ein KI-Coach für Datenschutz und Digitalkompetenz, spezialisiert auf medizinische, politische und symbolische Inhalte.

📌 Bitte prüfe:
- Gesundheitsdaten, Medikamente, Symptome
- Namen, Diagnosen, persönliche Infos
- Emotionale oder berufliche Offenbarungen
- Emojis mit symbolischem Kontext (💙, 🐸, 🔫, 🧿, ☠️, 🏴‍☠️ etc.)

📌 Bei Emojis:
→ Erkläre exakt, in welchen Online-Szenen oder politischen Gruppen das Emoji vorkommt (z. B. Telegram, TikTok, AfD, Alt-Right, Verschwörungsszene)
→ Nenne auch harmlose Verwendungen
→ Ziel: technisch unerfahrene Nutzer:innen aufklären

---

**Erkannte Datenarten:**  
[List der problematischen Begriffe + Emojis]

**Datenschutz-Risiko:**  
🟢 / 🟡 / 🔴 (nur eins verwenden)

**Bedeutung:**  
[Erkläre in Klartext und Alltagssprache]

**achtung.live-Empfehlung:**  
[Praktische Empfehlung mit HTML-Link]

**Tipp:**  
[Z. B. Emoji vermeiden oder verschlüsselt versenden]

---

Text zur Prüfung:
\"\"\"{user_input}\"\"\"
'''

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
