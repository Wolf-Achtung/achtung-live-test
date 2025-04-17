import re
import openai
import os
import json

openai.api_key = os.getenv("OPENAI_API_KEY")

def extract_json_from_codeblock(response_text):
    try:
        match = re.search(r'```json\s*(\{.*?\})\s*```', response_text, re.DOTALL)
        if match:
            return json.loads(match.group(1))
        else:
            match = re.search(r'\{.*?\}', response_text, re.DOTALL)
            if match:
                return json.loads(match.group())
    except Exception:
        return None
    return None

def analyze_text(text):
    score = 5
    message = "🟢 Kein Risiko erkennbar (5 %)"

    patterns = {
        "iban": r"\b[A-Z]{2}[0-9]{2}[ ]?([0-9]{4}[ ]?){3,4}\b|\b[0-9]{8,20}\b",
        "credit_card": r"\b(?:\d[ -]*?){13,16}\b",
        "email": r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b",
        "phone": r"\b(?:\+\d{1,3}[\s.-]?)?(?:\(\d{1,4}\)|\d{1,4})[\s.-]?\d{1,4}[\s.-]?\d{1,9}\b",
    }

    for label, pattern in patterns.items():
        if re.search(pattern, text):
            score = 85
            message = "🔴 Hohes Risiko erkannt (85 %)"
            break

    gpt_tip = ""
    sem_risk_level = ""
    sem_einschaetzung = ""
    sem_empfehlung = ""

    try:
        gpt_response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {
                    "role": "system",
                    "content": "Du bist eine freundliche, klare und hilfreiche GPT-Analyse für Datenschutz und digitale Kommunikation."
                },
                {
                    "role": "user",
                    "content": (
                        "Bewerte den folgenden Text mit einem JSON-Objekt im Markdown-Format. "
                        "Antworte NICHT mit zusätzlichem Text, nur mit:\n"
                        "\n```json\n{\n"
                        "\"sem_risk_level\": \"hoch|mittel|gering\",\n"
                        "\"sem_einschaetzung\": \"...\",\n"
                        "\"sem_empfehlung\": \"...\"\n"
                        "}\n```\n\n"
                        "Text:  + text + "
                    )
                }
            ],
            temperature=0.6
        )

        content = gpt_response['choices'][0]['message']['content']
        sem_data = extract_json_from_codeblock(content)

        if sem_data:
            sem_risk_level = sem_data.get("sem_risk_level", "")
            sem_einschaetzung = sem_data.get("sem_einschaetzung", "")
            sem_empfehlung = sem_data.get("sem_empfehlung", "")
            gpt_tip = sem_empfehlung
        else:
            sem_risk_level = "unbekannt"
            sem_einschaetzung = "Die Einschätzung war unklar."
            sem_empfehlung = "Formuliere lieber neutral – ohne Namen, Bewertungen oder sensible Inhalte."
            gpt_tip = sem_empfehlung

    except Exception:
        gpt_tip = "Keine GPT-Empfehlung möglich."
        sem_einschaetzung = "GPT-Antwort fehlgeschlagen."
        sem_empfehlung = "Verwende lieber eine vorsichtige Formulierung."

    return {
        "score": score,
        "message": message,
        "gpt_tip": gpt_tip,
        "sem_risk_level": sem_risk_level,
        "sem_einschaetzung": sem_einschaetzung,
        "sem_empfehlung": sem_empfehlung
    }