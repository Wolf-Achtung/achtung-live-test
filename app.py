from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import openai

app = Flask(__name__)
CORS(app)

# Neue OpenAI-Client-Struktur ab openai>=1.0.0
client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

@app.route("/debug-gpt", methods=["POST"])
def debug_gpt():
    data = request.get_json()
    user_input = data.get("text", "")

    prompt = f"""
Sie sind ein auf Datenschutz spezialisierter Textanalyst. Ihre Aufgabe ist es, den folgenden Text zu analysieren und sensibel zu bewerten:

1. Welche Arten vertraulicher Daten enthält der Text?
2. Wie hoch ist das Datenschutzrisiko? (Ampel-Kennzeichnung)
3. Warum ist der Inhalt unter Datenschutzaspekten sensibel?
4. Formulieren Sie einen konkreten, praktischen Tipp für die betroffene Person (z. B. wie man Inhalte anonymisieren oder sicher verschicken kann). Der Hinweis soll klar, leicht verständlich und direkt anwendbar sein.
5. Bieten Sie **einen Rewrite-Vorschlag** an – aber nur, wenn Sie diesen für sinnvoll und hilfreich erachten.
6. Verwenden Sie ausschließlich Sie-Form, verzichten Sie auf Icons außer der Datenschutz-Ampel.
7. Betonen Sie vulnerable Gruppen wie Kinder, ältere Menschen, Menschen mit psychischen Belastungen und Personen mit Sprachbarrieren besonders vorsichtig.

Struktur der Ausgabe:

---
**Erkannte Datenarten:**  
[List der sensiblen Inhalte]

**Datenschutz-Risiko:** 🟢 / 🟡 / 🔴

**Bedeutung:**  
[Warum ist dieser Inhalt kritisch?]

**achtung.live-Empfehlung:**  
[Praxis-Tipp – inklusive Link zu seriöser Info (z. B. datenschutz.org oder bund.de)]

**Optionaler Vorschlag zur Umformulierung:**  
[Nur wenn wirklich hilfreich – eine datenschutzsensible, empathische Version des Originaltexts.]

---
Hier ist der zu prüfende Text:  
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
        print("✅ GPT-Antwort:", gpt_output)
        return jsonify({ "gpt_output": gpt_output })

    except Exception as e:
        print("❌ GPT-Fehler:", str(e))
        return jsonify({ "gpt_output": f"❌ GPT-Fehler:\n\n{str(e)}" })

if __name__ == "__main__":
    app.run(debug=True)
