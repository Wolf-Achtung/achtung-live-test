async function startAnalysis() {
  const inputText = document.getElementById("textInput").value.trim();
  if (!inputText) return alert("Bitte gib einen Text ein.");

  const resultContainer = document.getElementById("result");
  resultContainer.innerHTML = "⏳ Analyse läuft…";

  const res = await fetch("https://web-production-f8648.up.railway.app/analyze", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ text: inputText })
  });

  const data = await res.json();
  let html = `
    <div class="feedback-box">
      <p><strong>Erkannte Datenarten:</strong> ${data.detected_data}</p>
      <p><strong>Datenschutz-Risiko:</strong> ${data.risk_level}</p>
      <p><strong>achtung.live-Empfehlung:</strong> ${data.explanation}</p>
      <p><strong>Tipp:</strong> ${data.tip}</p>
      ${data.source ? `<p><strong>Quelle:</strong> <a href="${data.source}" target="_blank">${data.source}</a></p>` : ""}
    </div>
  `;

  if (data.empathy_message) {
    html += `<div class="empathy-box ${data.empathy_level}">${data.empathy_message}</div>`;
  }

  if (data.risk_level !== "🟢 Kein Risiko") {
    html += `
      <div class="rewrite-box">
        ${data.rewrite_offer ? `<button onclick="triggerRewrite()">🤖 Text schützen</button>` : ""}
        <button onclick="loadHowTo()">📩 Anleitung: Sicher senden</button>
      </div>
      <div id="howto-output" class="howto-box"></div>
    `;
  }

  resultContainer.innerHTML = html;
}

async function triggerRewrite() {
  const inputText = document.getElementById("textInput").value.trim();
  const result = await fetch("https://web-production-f8648.up.railway.app/rewrite", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ text: inputText })
  });
  const data = await result.json();
  alert("🔐 Vorschlag für sicheren Text:\n\n" + data.rewritten);
}

async function loadHowTo() {
  const output = document.getElementById("howto-output");
  output.innerHTML = "⏳ Anleitung wird geladen…";
  const res = await fetch("https://web-production-f8648.up.railway.app/howto");
  const data = await res.json();
  output.innerHTML = `<pre>${data.howto}</pre>`;
}
