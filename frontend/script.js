let selectedLanguage = 'de';
const inputField = document.getElementById('inputText');
const output = document.getElementById('output');
const consentCheckbox = document.getElementById('consentCheckbox');
const consentWarning = document.getElementById('consentWarning');

function setLanguage(lang) {
  selectedLanguage = lang;
  analyzeText(); // neue Analyse bei Sprachwechsel
}

function showLoader() {
  output.innerHTML = '<p><em>🔄 Analyse läuft, Optimierung wird erstellt...</em></p>';
}

function analyzeText() {
  const input = inputField.value.trim();

  if (!consentCheckbox.checked) {
    consentWarning.style.display = 'block';
    return;
  }

  consentWarning.style.display = 'none';
  if (!input) return;

  showLoader();

  fetch("https://web-production-f8648.up.railway.app/analyze", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ text: input, language: selectedLanguage }),
  })
    .then((res) => res.json())
    .then((data) => {
      if (!data || !data.result) {
        output.innerHTML = "⚠️ Keine Vorschläge gefunden.";
        return;
      }

      let result = data.result;

      // Link-Tooltips einbauen
      result = result.replace(
        /\[([^\]]+)\]\((https?:\/\/[^\)]+)\)/g,
        `<a href="$2" target="_blank" title="Geprüfter Link – sicher laut Quelle">$1</a>`
      );

      // Abschnitte optisch strukturieren
      const sectionLabels = [
        'Erkannte Datenarten',
        'Datenschutz-Risiko',
        'Bedeutung',
        'achtung.live-Empfehlung',
        'Tipp',
        'Quelle',
      ];

      sectionLabels.forEach((label) => {
        const regex = new RegExp(`\\*\\*${label}\\*\\*`, 'g');
        result = result.replace(
          regex,
          `<span class="label">${label}</span>`
        );
      });

      // Vorschlag extrahieren
      const match = result.match(/"Vorschlag zum Kopieren:"\s*\n\s*["“](.+?)["”]/);
      let copyBox = '';
      if (match && match[1]) {
        const suggestion = match[1];
        copyBox = `
          <div style="margin-top: 20px; padding: 10px; background: #f4f4f4; border-left: 4px solid #cc0000;">
            <strong>Vorschlag zum Kopieren:</strong><br>
            <code id="copyText">${suggestion}</code><br>
            <button onclick="copySuggestion()" style="margin-top: 5px; background: #cc0000; color: white; border: none; padding: 5px 10px;">📋 Vorschlag kopieren</button>
          </div>
        `;
      }

      output.innerHTML = `<div>${result}</div>${copyBox}`;
    })
    .catch((error) => {
      output.innerHTML = `❌ Fehler: ${error}`;
    });
}

function copySuggestion() {
  const copyText = document.getElementById("copyText");
  if (copyText) {
    navigator.clipboard.writeText(copyText.textContent).then(() => {
      alert("✅ Vorschlag wurde in die Zwischenablage kopiert.");
    });
  }
}

// Auto-Analyse beim Tippen (mit Pause)
let typingTimer;
inputField.addEventListener('input', () => {
  clearTimeout(typingTimer);
  typingTimer = setTimeout(() => {
    if (inputField.value.trim().length > 5) {
      analyzeText();
    }
  }, 800);
});
