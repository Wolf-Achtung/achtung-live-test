const loader = document.getElementById("loader");
const responseBlock = document.getElementById("responseBlock");
const analysisOutput = document.getElementById("analysis");
const consentCheckbox = document.getElementById("consentCheckbox");

function startAnalysis() {
  const inputText = document.getElementById("inputText").value.trim();

  if (!consentCheckbox.checked) {
    alert("Bitte stimmen Sie der Verarbeitung gemäß Datenschutzerklärung zu.");
    return;
  }

  if (!inputText) {
    alert("Bitte geben Sie einen Text ein.");
    return;
  }

  loader.innerText = "Analyse läuft, bitte warten...";
  responseBlock.style.display = "block";
  analysisOutput.innerHTML = "";

  fetch("https://web-production-f8648.up.railway.app/analyze", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ text: inputText, language: "de" })
  })
    .then((res) => res.json())
    .then((data) => {
      loader.innerText = "";
      if (data.result) {
        const parsed = parseGPTResponse(data.result);
        analysisOutput.innerHTML = parsed;
      } else {
        analysisOutput.innerHTML = "❌ Fehler: " + data.error;
      }
    })
    .catch((err) => {
      loader.innerText = "";
      analysisOutput.innerHTML = "❌ Fehler: " + err.message;
    });
}

function parseGPTResponse(response) {
  let html = response
    .replace(/1\.\s*Erkannte Datenarten/gi, "<span class='heading'>1. Erkannte Datenarten</span>")
    .replace(/2\.\s*Datenschutz-Risiko.*?:/gi, "<span class='heading'>2. Datenschutz-Risiko</span>")
    .replace(/3\.\s*Bedeutung.*?:/gi, "<span class='heading'>3. Bedeutung</span>")
    .replace(/4\.\s*achtung\.live-Empfehlung.*?:/gi, "<span class='heading'>4. achtung.live-Empfehlung</span>")
    .replace(/5\.\s*Tipp.*?:/gi, "<span class='heading'>5. Tipp</span>")
    .replace(/6\.\s*Quelle.*?:/gi, "<span class='heading'>6. Quelle</span>")
    .replace(/(?:\[([^\]]+)\])\(([^)]+)\)/g, '<a href="$2" class="tooltip" target="_blank">$1<span class="tooltiptext">Klick für Quelle</span></a>')
    .replace(/\n/g, "<br>");

  return html;
}
