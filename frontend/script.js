const loader = document.getElementById("loader");
const result = document.getElementById("result");
const textInput = document.getElementById("textInput");
const consentCheckbox = document.getElementById("consent");
const languageSelect = document.getElementById("language");

const API_URL = "https://web-production-f8648.up.railway.app/analyze";

function startAnalysis() {
  if (!consentCheckbox.checked) {
    result.innerHTML = "❌ Bitte stimmen Sie der DSGVO-Verarbeitung zu.";
    return;
  }

  const text = textInput.value.trim();
  if (!text) {
    result.innerHTML = "❌ Bitte geben Sie einen Text ein.";
    return;
  }

  loader.innerText = "🧠 Analyse läuft, Optimierung wird erstellt...";
  result.innerHTML = "";

  fetch(API_URL, {
    method: "POST",
    headers: {
      "Content-Type": "application/json"
    },
    body: JSON.stringify({ text })
  })
  .then(response => response.json())
  .then(data => {
    loader.innerText = "";

    if (data.error) {
      result.innerHTML = `❌ Fehler: ${data.error}`;
      return;
    }

    const formatted = formatGPTOutput(data.result);
    result.innerHTML = formatted;

    if (data.emojis && data.emojis.length > 0) {
      injectTooltips(data.emojis);
    }
  })
  .catch(err => {
    loader.innerText = "";
    result.innerHTML = `❌ Fehler: ${err.message}`;
  });
}

// 🔠 GPT-Ergebnis strukturieren
function formatGPTOutput(text) {
  let html = text
    .replace(/\*\*([^*]+)\*\*/g, '<strong style="color:#C9002B;">$1</strong>')
    .replace(/\n\n/g, "<br><br>")
    .replace(/\n/g, "<br>")
    .replace(/\[([^\]]+)\]\(([^)]+)\)/g, '<a href="$2" target="_blank" style="color:#0052cc;">$1</a>');
  return html;
}

// ℹ️ Emojis markieren mit Tooltip
function injectTooltips(emojis) {
  emojis.forEach(emojiData => {
    const tooltip = `
      <span class="emoji-tooltip" title="Bedeutung: ${emojiData.bedeutung} – ${emojiData.kontext}">
        ${emojiData.emoji}
      </span>
    `;
    result.innerHTML = result.innerHTML.replaceAll(emojiData.emoji, tooltip);
  });
}

// ✨ Analyse auch beim Tippen optional starten
textInput.addEventListener("keydown", function (e) {
  if (e.key === "Enter" && e.ctrlKey) {
    startAnalysis();
  }
});
