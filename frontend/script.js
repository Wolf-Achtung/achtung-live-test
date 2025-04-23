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

    if (data.result) {
      const resultWithLinks = data.result.replace(/\[([^\]]+)\]\(([^)]+)\)/g, '<a href="$2" target="_blank">$1</a>');
      resultContainer.innerHTML = resultWithLinks;
    } else if (data.error) {
      displayError(`❌ Fehler: ${data.error}`);
    } else {
      displayError("❌ Keine Antwort erhalten.");
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
