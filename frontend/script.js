async function startAnalysis() {
  const input = document.getElementById("user-input").value;
  const output = document.getElementById("output");
  const loader = document.getElementById("loader");

  if (!input.trim()) {
    output.innerHTML = "⚠️ Bitte geben Sie einen Text ein.";
    return;
  }

  if (!document.getElementById("consentCheckbox").checked) {
    output.innerHTML = "⚠️ Bitte stimmen Sie der Datenschutzerklärung zu.";
    return;
  }

  loader.innerText = "Analyse läuft, bitte warten...";
  output.innerHTML = "";

  try {
    const response = await fetch("https://web-production-f8648.up.railway.app/analyze", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ text: input })
    });

    const data = await response.json();
    loader.innerText = "";
    if (data.result) {
      output.innerHTML = formatGPTOutput(data.result);
    } else {
      output.innerHTML = "❌ Fehler: Keine Antwort erhalten.";
    }
  } catch (error) {
    loader.innerText = "";
    output.innerHTML = "❌ Fehler: " + error.message;
  }
}

function formatGPTOutput(text) {
  const highlights = [
    "1. Erkannte Datenarten",
    "2. Datenschutz-Risiko",
    "3. Bedeutung der gefundenen Elemente",
    "4. achtung.live-Empfehlung",
    "5. Tipp: 1 sinnvoller Rewrite-Vorschlag",
    "6. Quelle",
    "Emoji-Analyse",
    "🌐 Linkprüfung"
  ];

  highlights.forEach(heading => {
    const re = new RegExp(`(${heading})`, "g");
    text = text.replace(re, `<span style="color: #cc0000; font-weight: bold;">$1</span>`);
  });

  return text.replace(/\n/g, "<br>");
}

function toggleButton() {
  const checkbox = document.getElementById("consentCheckbox");
  const button = document.getElementById("analyze-btn");
  button.disabled = !checkbox.checked;
}
