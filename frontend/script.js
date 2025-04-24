const analyzeButton = document.getElementById("analyze-button");
const inputText = document.getElementById("input-text");
const resultBox = document.getElementById("results");
const rewriteButton = document.getElementById("rewrite-button");
const rewritePopup = document.getElementById("rewrite-popup");
const empathyBox = document.getElementById("empathy-message");
const howtoButton = document.getElementById("howto-button");
const howtoBox = document.getElementById("howto-box");

analyzeButton.addEventListener("click", async () => {
  const text = inputText.value;
  const consent = document.getElementById("consent").checked;

  if (!text || !consent) {
    alert("Bitte Text eingeben und der Analyse zustimmen.");
    return;
  }

  resultBox.innerHTML = "⏳ Analyse läuft…";
  empathyBox.classList.add("hidden");
  rewriteButton.classList.add("hidden");
  howtoButton.classList.add("hidden");

  const response = await fetch("https://web-production-f8648.up.railway.app/analyze", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ text })
  });

  const data = await response.json();

  resultBox.innerHTML = `
    <strong>Erkannte Datenarten:</strong> ${data.detected_data}<br />
    <strong>Datenschutz-Risiko:</strong> ${data.risk_level}<br />
    <strong>achtung.live-Empfehlung:</strong> ${data.explanation}<br />
    <strong>Tipp:</strong> ${data.tip}<br />
    ${data.source ? `<strong>Quelle:</strong> <a href="${data.source}" target="_blank">${data.source}</a>` : ""}
  `;

  if (data.empathy_message) {
    empathyBox.className = `empathy-box ${data.empathy_level}`;
    empathyBox.innerText = data.empathy_message;
    empathyBox.classList.remove("hidden");
  }

  if (data.rewrite_offer) {
    rewriteButton.classList.remove("hidden");
    howtoButton.classList.remove("hidden");
  }
});

rewriteButton.addEventListener("click", async () => {
  const text = inputText.value;
  rewritePopup.innerText = "⏳ Vorschlag wird erstellt…";
  rewritePopup.classList.remove("hidden");

  const response = await fetch("https://web-production-f8648.up.railway.app/rewrite", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ text })
  });

  const data = await response.json();
  rewritePopup.innerText = "Vorschlag für sicheren Text:\n\n" + data.rewritten;
});

howtoButton.addEventListener("click", async () => {
  howtoBox.classList.remove("hidden");
  howtoBox.innerText = "⏳ Anleitung wird geladen…";

  const response = await fetch("https://web-production-f8648.up.railway.app/howto");
  const data = await response.json();
  howtoBox.innerText = data.howto;
});
