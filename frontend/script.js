async function analyzeText() {
  const text = document.getElementById("inputText").value;
  const output = document.getElementById("output");
  output.innerHTML = "⏳ GPT denkt nach...";

  try {
    const res = await fetch("https://web-production-f8648.up.railway.app/debug-gpt", {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify({ text })
    });

    const data = await res.json();

    // 🔎 Debug-Log in der Konsole
    console.log("GPT-Rohantwort:", data.gpt_raw);
    console.log("Antwortobjekt:", data);

    // ✅ Ausgabe – wenn GPT-Vorschläge gefunden wurden
    if (data.suggestions && data.suggestions.length > 0) {
      output.innerHTML = data.suggestions.map((s, i) => `
        <div><strong>🔁 Vorschlag ${i + 1}:</strong><br>${s}</div><br>
      `).join("");
    } else {
      // ⚠️ Keine Vorschläge – zeige GPT-Rohantwort
      output.innerHTML = `
        ⚠️ Keine Vorschläge gefunden.<br><br>
        <strong>GPT-Rohantwort:</strong><br>
        <pre>${data.gpt_raw || 'Keine Antwort erhalten'}</pre>
      `;
    }
  } catch (err) {
    // ❌ Bei technischem Fehler (z. B. Fetch oder Backend down)
    output.innerHTML = `
      ❌ Fehler beim Abrufen von GPT:<br>
      <pre>${err.message}</pre>
      <br>Bitte prüfe, ob dein OpenAI-Key gültig ist und dein Backend läuft.
    `;
  }
}
