from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import openai
import json
import re
import requests

app = Flask(__name__)
CORS(app)

openai.api_key = os.getenv("OPENAI_API_KEY")

# 🔐 Lade & prüfe vertrauenswürdige Links aus JSON-Datei
trusted_links_dict = {}
try:
    with open("trusted_links.json", "r") as f:
        loaded = json.load(f)
        if isinstance(loaded, list):
            trusted_links_dict = {entry["url"]: entry for entry in loaded if "url" in entry}
        elif isinstance(loaded, dict):
            trusted_links_dict = loaded
    print(f"✅ {len(trusted_links_dict)} vertrauenswürdige Links geladen.")
except Exception as e:
    print("⚠️ trusted_links.json konnte nicht geladen werden:", e)

def check_links_in_text(text):
    urls = re.findall(r'https?://\S+', text)
    result = []
    for url in urls:
        try:
            response = requests.get(url, timeout=4)
            status = response.status_code
            if status == 200:
                result.append((url, "✅ erreichbar"))
            else:
                result.append((url, f"⚠️ Status {status}"))
        except:
            result.append((url, "❌ nicht erreichbar"))
    return result

@app.route("/debug-gpt", methods=["POST"])
def debug_gpt():
    data = request.get_json()
    user_input = data.get("text", "")
    language = data.get("language", "de")

    prompt = f"""
Du bist ein Datenschutz- und Kommunikations-Coach. Analysiere den folgenden Text auf sensible Inhalte, Emojis mit Bedeutung, politische oder gesundheitliche Aussagen.

Erstelle einen strukturierten Bericht mit folgenden Abschnitten (in **Markdown-Format**):

**Erkannte Datenarten:**  
(Liste)

**Datenschutz-Risiko:**  
🟢 / 🟡 / 🔴

**Bedeutung der gefundenen Elemente:**  
(kurz, verständlich, mit Beispielen)

**achtung.live-Empfehlung:**  
(Kurze präzise Empfehlung)

**Tipp: 1 sinnvoller Rewrite-Vorschlag**  
(Satz umformuliert, anonymisiert)

**Quelle:**  
Wenn Emoji oder Datenschutzthema: verlinke eine vertrauenswürdige Quelle. Wenn unbekannt: „Nicht verfügbar“.

Hier ist der Nutzertext:  
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

        # Links validieren
        checked_links = check_links_in_text(gpt_output)
        for url, status in checked_links:
            if "nicht erreichbar" in status:
                gpt_output = gpt_output.replace(url, f"{url} ⚠️ (Link nicht erreichbar)")

        return jsonify({ "gpt_raw": gpt_output })

    except Exception as e:
        return jsonify({ "error": str(e) }), 500

if __name__ == "__main__":
    app.run(debug=True)
