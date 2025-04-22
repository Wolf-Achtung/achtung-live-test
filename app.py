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
🔐 Du bist ein vertrauensvoller KI-Datenschutz-Coach mit Schwerpunkt auf sensiblen Informationen, emotionalen Aussagen und symbolischer Sprache.

📌 Bitte analysiere den folgenden Text besonders auf:
- Gesundheitsdaten (Diagnosen, Medikamente, Symptome)
- Namen von Personen (z. B. Ärzte, Angehörige)
- Emotionale und psychische Inhalte
- persönliche Identifizierbarkeit (Adresse, Telefonnummer, Arbeitgeber etc.)
- Zugangsdaten, IBAN, Passwörter, Kreditkarten
- problematische Emojis wie 💙, 🐸, 🔫, 🧿, ☠️, 🔞, 🏴‍☠️ usw.
- Kombinationen, die zu Datenschutzrisiken oder Missverständnissen führen

---

📋 Antworte IMMER in dieser Struktur:

**Erkannte Datenarten:**  
- [Liste der sensiblen Inhalte oder Emojis]

**Datenschutz-Risiko:**  
🟢 Unbedenklich / 🟡 Mögliches Risiko / 🔴 Kritisch – so nicht senden!

**Bedeutung:**  
[Erkläre, warum bestimmte Kombinationen problematisch sind – z. B. Name + Medikament + 💙]

**achtung.live-Empfehlung:**  
[Gib praktische Hinweise, wie Nutzer:innen Texte datenschutzsicher gestalten können – gerne mit HTML-Link, z. B.: <a href="https://www.datenschutz.org/datensicherheit/" target="_blank">Datensicherheit im Netz</a>]

**Tipp:**  
[Ein einfacher, technischer Tipp für Laien, z. B. „So verschlüsseln Sie eine ZIP-Datei: <a href='https://www.bsi.bund.de/DE/Themen/Verbraucherinnen-und-Verbraucher/Downloads/zip-passwortschutz.html' target='_blank'>Zur Anleitung</a>“]

---

Hier ist der zu prüfende Text:
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
