from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import openai

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

openai.api_key = os.getenv("OPENAI_API_KEY")
if not openai.api_key:
    raise ValueError("❌ OPENAI_API_KEY fehlt – bitte in Railway setzen!")

@app.route("/", methods=["GET"])
def home():
    return "🚀 Achtung.live API läuft!"

@app.route("/debug-gpt", methods=["POST"])
def debug_gpt():
    data = request.get_json()
    user_input = data.get("text", "")

    system_prompt = """
Du bist ein empathischer Datenschutz-Coach mit medizinischem Feingefühl. Deine Aufgabe ist es, den folgenden Text auf sensible Inhalte zu prüfen und – falls nötig – sichere, bedeutungserhaltende Alternativen vorzuschlagen.

Achte besonders auf:
- medizinische Informationen (Krankheiten, Diagnosen, Symptome, Medikamente)
- Namen von Ärzt:innen oder Kliniken
- finanzielle Details (z. B. Gehalt, Kontonummern, Kredite)
- emotionale oder intime Aussagen (z. B. über Beziehung, mentale Gesundheit)
- persönliche Identifizierbarkeit (Namen, Telefonnummern, Adressen)
- vertrauliche Unternehmensinformationen oder Geheimnisse

Wenn du sensible Inhalte findest, analysiere sie kurz und formuliere drei Rewrite-Vorschläge in verschiedenen Tonalitäten. Achte dabei auf Empathie, Anonymität und Klarheit.

---
🛑 Sensible Inhalte erkannt:
[List der sensiblen Begriffe/Stellen im Originaltext]

🔁 Rewrite-Vorschläge:

1. 🌱 Diskret-neutral  
Eine anonyme, aber verständliche Variante – für maximale Privatsphäre.

2. 💬 Locker-umgangssprachlich  
Eine lockere, alltagsnahe Version – für informelle Kommunikation.

3. 🏥 Professionell & medizinisch korrekt  
Eine sachliche, fachlich fundierte Version – für professionelle Kontexte.

✨ Bonus (optional):  
Erkläre in 1–2 Sätzen, warum der Originaltext datenschutzrechtlich problematisch war – und wie deine Rewrites helfen, das Risiko zu reduzieren.
"""

    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",  # Alternativ: "gpt-4o"
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Bitte prüfe folgenden Text:\n\n{user_input}"}
            ],
            temperature=0.7,
            max_tokens=800,
            top_p=1,
            frequency_penalty=0.3,
            presence_penalty=0.1
        )

        gpt_output = response.choices[0].message.content.strip()
        suggestions = gpt_output.split("\n\n")
        return jsonify({ "suggestions": suggestions, "gpt_raw": gpt_output })

    except Exception as e:
        print("❌ GPT-Fehler:", str(e))
        return jsonify({ "error": str(e) }), 500

if __name__ == "__main__":
    app.run(debug=True)
