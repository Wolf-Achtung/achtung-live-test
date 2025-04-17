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
    if (data.suggestions) {
      output.innerHTML = data.suggestions.map((s, i) => `
        <div><strong>Vorschlag ${i + 1}:</strong><br>${s}</div><br>
      `).join("");
    } else {
     output.innerHTML = "⚠️ Keine Vorschläge gefunden.<br><pre>" + data.gpt_raw + "</pre>";
    }
  } catch (err) {
    output.innerHTML = "❌ Fehler: " + err.message;
  }
}
