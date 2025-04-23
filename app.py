from flask import Flask, request, jsonify
from flask_cors import CORS
from openai import OpenAI
import os
import json

app = Flask(__name__)
CORS(app)

# Initialisierung des OpenAI-Clients mit aktuellem API-Client (>=1.0.0)
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Hilfsfunktion: Lade trusted_links.json und suche nach Kategorie
def get_trusted_link_by_category(category):
    try:
        with open("trusted_links.json", "r", encoding="utf-8") as f:
            trusted_links = json.load(f)
            for entry in trusted_links:
                if entry["kategorie"].lower() == category.lower():
                    return entry["quelle"]
    except Exception as e:
        print(f"⚠️ trusted_links.json konnte nicht gelesen werden: {e}")
    return None

@app.route("/analyze", methods=["POST"])
def analyze():
    try:
        data = request.get_json()
        user_input = data.get("text", "")
        selected_language = data.get("language", "DE")

        if not user_input:
            return jsonify({"error": "Kein Text übergeben"}), 400

        # GPT Prompt definieren
        prompt = f"""
Du bist ein Datenschutz- und Kommunikations-Experte. Analysiere folgenden Text auf sensible Inhalte, Datenschutzrisiken, riskante Emojis oder problematische Formulierungen. Gib das Ergebnis strukturiert und klar zurück – mit einer Ampelbewertung, einer Empfehlung und einem konkreten Tipp (Rewrite-Vorschlag). Antworte in der Sprache: {selected_language}.

Text:
\"\"\"{user_input}\"\"\"

Strukturierte Antwort in Markdown:
1. Erkannte Datenarten
- …

2. Datenschutz-Risiko
- Ampel: 🟢, 🟡 oder 🔴

3. Bedeutung der gefundenen Elemente
- …

4. achtung.live-Empfehlung:
- …

5. Tipp:
- Konkreter Rewrite oder Handlungsempfehlung

6. Quelle (nur wenn relevant):
- passende, vertrauenswürdige Quelle (z. B. zum Thema Kreditkarten, Gesundheitsdaten, Emojis, etc.)
"""

        # Anfrage an OpenAI senden
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
        )

        # Rohantwort analysieren
        gpt_text = response.choices[0].message.content

        # Themen-Kategorie erkennen (einfaches Mapping, später dynamisch)
        if "kreditkarte" in user_input.lower():
            category = "Finanzdaten"
        elif "arzt" in user_input.lower() or "befund" in user_input.lower():
            category = "Gesundheitsdaten"
        elif "💙" in user_input:
            category = "Emojis"
        else:
            category = None

        # Quelle aus JSON holen
        source_link = get_trusted_link_by_category(category) if category else None

        # Link am Ende anhängen
        if source_link:
            gpt_text += f"\n\n🔗 [Mehr zur Sicherheit bei {category}]({source_link})"

        return jsonify({"result": gpt_text})

    except Exception as e:
        print(f"❌ Interner Fehler: {e}")
        return jsonify({"error": f"Fehler: {str(e)}"}), 500

# App starten
if __name__ == "__main__":
    app.run(debug=True)
