from flask import Flask, request, jsonify
from flask_cors import CORS
import openai
import os
import json
import requests

app = Flask(__name__)
CORS(app)

# GPT-API-Key laden
openai.api_key = os.getenv("OPENAI_API_KEY")

# ✅ trusted_links.json sicher laden (Fallback bei Fehler)
try:
    with open("trusted_links.json", "r") as f:
        trusted_links = json.load(f)
        print(f"✅ {len(trusted_links)} vertrauenswürdige Links geladen.")
except Exception as e:
    print(f"⚠️ trusted_links.json konnte nicht geladen werden: {e}")
    trusted_links = {}

@app.route("/debug-gpt", methods=["POST"])
def debug_gpt():
    data = request.get_json()
    user_input = data.get("text", "")
    lang = data.get("lang", "de")

    # GPT-Prompt für mehrsprachige Analyse inkl. Emojis & DSGVO
    prompt = f"""
Du bist ein vertrauenswürdiger KI-Assistent für datenschutzkonforme Textanalyse im Sinne der DSGVO und des EU AI Act. Deine Aufgabe:

1. Erkenne sensible Daten wie:
   - medizinische Begriffe, Symptome, Diagnosen
   - Behördeninformationen oder persönliche Äußerungen
   - Emojis mit symbolischer Bedeutung (z. B. 💙)

2. Bewerte das Datenschutzrisiko:
   - 🟢 Unbedenklich
   - 🟡 Mögliches Risiko
   - 🔴 Kritisch – nicht versenden!

3. Gib eine verständliche, empathische Einschätzung und konkrete Tipps.

Sprache der Antwort: {lang.upper()}

Hier ist der zu analysierende Text:
\"\"\"{user_input}\"\"\"
"""

    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.6,
            max_tokens=1000
        )
        gpt_output = response.choices[0].message.content.strip()

        # Link-Validierung (optional in späterer Ausbaustufe prüfen)
        for label, entry in trusted_links.items():
            if entry["url"] not in gpt_output:
                continue
            try:
                link_check = requests.head(entry["url"], timeout=5)
                if link_check.status_code != 200:
                    gpt_output = gpt_output.replace(
                        entry["url"], f"(❌ Link deaktiviert: {entry['label']})"
                    )
            except:
                gpt_output = gpt_output.replace(
                    entry["url"], f"(❌ Link nicht erreichbar: {entry['label']})"
                )

        return jsonify({
            "gpt_output": gpt_output,
            "trusted_links": list(trusted_links.keys())
        })
    except Exception as e:
        return jsonify({ "error": str(e) }), 500

if __name__ == "__main__":
    app.run(debug=True)
