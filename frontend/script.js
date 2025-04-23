const loader = document.getElementById("loader");
const resultDiv = document.getElementById("result");
const analyzeBtn = document.getElementById("analyze-btn");
const languageSelect = document.getElementById("language");

function startAnalysis() {
  const input = document.getElementById("userInput").value.trim();
  const lang = languageSelect.value;

  if (!input) return;

  loader.innerText = "Analyse läuft, bitte warten...";
  loader.style.display = "block";
  resultDiv.innerHTML = "";

  fetch("https://web-production-f8648.up.railway.app/analyze", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ text: input, lang: lang }),
  })
    .then((res) => res.json())
    .then((data) => {
      loader.style.display = "none";
      if (data.result) {
        resultDiv.innerHTML = formatGPTOutput(data.result);
      } else {
        resultDiv.innerHTML = "❌ Fehler: " + data.error;
      }
    })
    .catch((err) => {
      loader.style.display = "none";
      resultDiv.innerHTML = "❌ Fehler: " + err.message;
    });
}

function formatGPTOutput(text) {
  // Fett hervorheben
  return text
    .replace(/(\*\*.*?\*\*)/g, "<strong style='color:#b80000;'>$1</strong>")
    .replace(/\n/g, "<br>");
}
