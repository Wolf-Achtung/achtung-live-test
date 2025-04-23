const backendURL = "https://web-production-f8648.up.railway.app/analyze";

async function startAnalysis() {
  const input = document.getElementById("text-input").value;
  const consent = document.getElementById("consent").checked;
  const loader = document.getElementById("loader");
  const output = document.getElementById("output");
  output.innerHTML = "";

  if (!consent) {
    output.innerHTML = "<p style='color:red;'>❌ Bitte Zustimmung zur Analyse erteilen.</p>";
    return;
  }

  loader.innerText = "Analyse läuft, bitte warten...";

  try {
    const res = await fetch(backendURL, {
      method: "POST",
      headers: {"Content-Type": "application/json"},
      body: JSON.stringify({ text: input })
    });

    const data = await res.json();
    loader.innerText = "";

    if (data.error) {
      output.innerHTML = `<p style="color:red;">❌ Fehler: ${data.error}</p>`;
      return;
    }

    let html = `<div class="response-block">${data.feedback.replace(/\n/g, "<br>")}</div>`;

    if (data.emoji_analysis && data.emoji_analysis.length > 0) {
      html += `<div class="emoji-block"><strong>🧩 Emoji-Analyse:</strong><ul>`;
      data.emoji_analysis.forEach(e => {
        html += `<li><strong>${e.title} (${e.symbol})</strong><br>${e.text}
        <br><small>Kontext: ${e.group}</small><br>
        <a href="${e.link}" target="_blank" rel="noopener noreferrer">🔗 Quelle</a></li><br>`;
      });
      html += `</ul></div>`;
    }

    output.innerHTML = html;
  } catch (err) {
    loader.innerText = "";
    output.innerHTML = `<p style="color:red;">❌ Fehler: ${err.message}</p>`;
  }
}
