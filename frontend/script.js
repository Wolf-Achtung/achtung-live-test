async function startAnalysis() {
  const consent = document.getElementById("consentCheckbox").checked;
  if (!consent) {
    displayError("❗ Bitte stimmen Sie der Analyse gemäß Datenschutzbestimmungen zu.");
    return;
  }

  const inputText = document.getElementById("textInput").value.trim();
  if (!inputText) {
    displayError("❗ Bitte geben Sie einen Text zur Analyse ein.");
    return;
  }

  const resultContainer = document.getElementById("result");
  const loader = document.getElementById("loader");
  resultContainer.innerHTML = "";
  loader.style.display = "block";

  try {
    const response = await fetch("https://web-production-f8648.up.railway.app/analyze", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        text: inputText,
        language: document.getElementById("languageSelect").value,
      }),
    });

    const data = await response.json();
    loader.style.display = "none";

    if (data) {
      const html = `
        <div class="feedback-box">
          <p><strong>Erkannte Datenarten:</strong> ${data.detected_data}</p>
          <p><strong>Datenschutz-Risiko:</strong> ${data.risk_level}</p>
          <p><strong>achtung.live-Empfehlung:</strong> ${data.explanation}</p>
          <p><strong>Tipp:</strong> ${data.tip}</p>
          ${data.source ? `<p><strong>Quelle:</strong> <a href="${data.source}" target="_blank">${data.source}</a></p>` : ""}
          <button onclick="copySuggestion()">📋 Vorschlag kopieren</button>
        </div>
      `;
      resultContainer.innerHTML = html;
    } else {
      displayError("❌ Keine verwertbare Analyse erhalten.");
    }
  } catch (error) {
    loader.style.display = "none";
    displayError(`❌ Fehler: ${error.message}`);
  }
}

function displayError(message) {
  const resultContainer = document.getElementById("result");
  resultContainer.innerHTML = `<div class="error">${message}</div>`;
}

function copySuggestion() {
  const text = document.getElementById("result").innerText;
  navigator.clipboard.writeText(text);
  alert("✅ Textvorschlag wurde kopiert.");
}
