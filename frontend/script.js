const backendUrl = "https://web-production-f8648.up.railway.app/analyze";

function startAnalysis() {
  const input = document.getElementById("userInput").value.trim();
  const consent = document.getElementById("consentCheckbox").checked;
  const language = document.getElementById("languageSelect").value;
  const resultArea = document.getElementById("resultArea");
  const loader = document.getElementById("loader");

  if (!input) {
    alert("Bitte geben Sie einen Text ein.");
    return;
  }

  if (!consent) {
    alert("Bitte stimmen Sie der DSGVO-Verarbeitung zu.");
    return;
  }

  loader.style.display = "block";
  loader.innerText = "Analyse läuft, Optimierung wird erstellt...";
  resultArea.innerHTML = "";

  fetch(backendUrl, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      text: input,
      language: language
    }),
  })
    .then((res) => res.json())
    .then((data) => {
      loader.style.display = "none";

      if (data.result) {
        resultArea.innerHTML = formatResultWithTooltips(data.result);
      } else {
        resultArea.innerHTML = `<p style="color:red;">❌ Fehler: ${data.error || "Keine Antwort erhalten"}</p>`;
      }
    })
    .catch((err) => {
      loader.style.display = "none";
      resultArea.innerHTML = `<p style="color:red;">❌ Fehler: ${err.message}</p>`;
    });
}

function formatResultWithTooltips(text) {
  const linkRegex = /\[(.*?)\]\((https?:\/\/.*?)\)/g;
  return text.replace(linkRegex, (match, label, url) => {
    return `<a href="${url}" target="_blank" class="tooltip">${label}<span class="tooltiptext">Verifizierte Quelle</span></a>`;
  }).replace(/\*\*(.*?)\*\*/g, "<strong style='color:#B80000;'>$1</strong>").replace(/\n/g, "<br>");
}
