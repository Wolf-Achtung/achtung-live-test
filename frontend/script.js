async function analyzeText() {
  const text = document.getElementById("text").value;
  const consent = document.getElementById("consent").checked;
  const lang = document.getElementById("language").value;
  const resultDiv = document.getElementById("result");
  const loader = document.getElementById("loader");

  if (!consent) {
    alert("Bitte stimmen Sie der Verarbeitung gemäß Datenschutzerklärung zu.");
    return;
  }

  if (!text.trim()) {
    alert("Bitte geben Sie einen Text ein.");
    return;
  }

  loader.innerText = "Analyse läuft, Optimierung wird erstellt...";
  resultDiv.innerHTML = "";

  try {
    const response = await fetch("https://web-production-f8648.up.railway.app/analyze", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ text, language: lang }),
    });

    const data = await response.json();

    if (data.error) {
      resultDiv.innerHTML = `<p style="color:red;">❌ Fehler: ${data.error}</p>`;
    } else {
      const output = data.gpt_raw || data.suggestions?.join("<br><br>") || "⚠️ Keine Vorschläge gefunden.";
      resultDiv.innerHTML = formatOutput(output);
    }
  } catch (error) {
    resultDiv.innerHTML = `<p style="color:red;">❌ Serverfehler: ${error.message}</p>`;
  }

  loader.innerText = "";
}

function formatOutput(text) {
  // Highlights bestimmte Rubriken
  const sections = [
    "Erkannte Datenarten", "Datenschutz-Risiko", "Bedeutung", "achtung.live-Empfehlung", 
    "Tipp", "Vorschlag zur Formulierung", "Quelle"
  ];

  sections.forEach((title) => {
    const regex = new RegExp(`\\*\\*?${title}:?\\*\\*?`, "gi");
    text = text.replace(regex, `<strong>${title}:</strong>`);
  });

  // Links klickbar machen
  text = text.replace(/https?:\/\/[^\s)]+/g, url => `<a href="${url}" target="_blank">${url}</a>`);

  return `<div id="resultBox">${text}</div>`;
}
