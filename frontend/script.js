const backendUrl = "https://web-production-f8648.up.railway.app/debug-gpt";

const loader = document.getElementById("loader");
const resultContainer = document.getElementById("result");
const textarea = document.getElementById("user-input");
const consentCheckbox = document.getElementById("consent");
const languageSelector = document.getElementById("language");

function startAnalysis() {
  const userText = textarea.value.trim();
  const language = languageSelector.value;

  if (!consentCheckbox.checked) {
    alert("Bitte stimmen Sie der Verarbeitung gemäß DSGVO zu.");
    return;
  }

  if (userText === "") {
    alert("Bitte geben Sie einen Text ein.");
    return;
  }

  loader.style.display = "block";
  loader.innerText = "Analyse läuft, Optimierung wird erstellt...";

  fetch(backendUrl, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ text: userText, language: language })
  })
    .then(response => {
      if (!response.ok) throw new Error("Netzwerkfehler");
      return response.json();
    })
    .then(data => {
      loader.style.display = "none";
      if (data.gpt_raw) {
        resultContainer.innerHTML = formatOutput(data.gpt_raw);
      } else {
        resultContainer.innerHTML = "⚠️ Keine Vorschläge gefunden.<br><br><i>GPT-Rohantwort:</i><br>" + (data.error || "Keine Antwort erhalten");
      }
    })
    .catch(error => {
      loader.style.display = "none";
      resultContainer.innerHTML = `❌ Fehler: ${error.message}`;
    });
}

function formatOutput(raw) {
  const withLineBreaks = raw
    .replace(/\*\*(.*?)\*\*/g, '<strong style="color: #c20000;">$1</strong>') // fette Titel rot
    .replace(/\n{2,}/g, "<br><br>")
    .replace(/\n/g, "<br>")
    .replace(/(https?:\/\/[^\s]+)/g, match => {
      return `<a href="${match}" target="_blank" rel="noopener noreferrer">${match}</a>`;
    });

  return `<div class="result-text" style="font-size: 1rem; line-height: 1.6;">${withLineBreaks}</div>`;
}

// Optional: Barrierefreiheit verbessern
document.addEventListener("DOMContentLoaded", () => {
  const skipLink = document.createElement("a");
  skipLink.href = "#maincontent";
  skipLink.className = "sr-only sr-only-focusable";
  skipLink.innerText = "Direkt zum Inhalt springen";
  document.body.prepend(skipLink);
});
