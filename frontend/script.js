async function analyzeText() {
  const text = document.getElementById("inputText").value;
  const output = document.getElementById("output");
  output.innerHTML = "⏳ GPT denkt nach...";

  try {
    const res = await fetch("https://web-production-f8648.up.railway.app/debug-gpt", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ text })
    });

    const data = await res.json();
    if (data.suggestions && data.suggestions.length > 0) {
      output.innerHTML = data.suggestions.map((s, i) => `
        <div><strong>Vorschlag ${i + 1}:</strong><br>${s}</div><br>
      `).join("");
    } else {
     output.innerHTML = `
  ❌ Fehler beim Abrufen von GPT:<br>
  <pre>${err.message}</pre>
  <br>Bitte prüfe, ob der OpenAI-Key aktiv ist und das Modell verfügbar ist.
`;
  }
}
