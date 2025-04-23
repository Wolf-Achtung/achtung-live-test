const loader = document.getElementById("loader");
const result = document.getElementById("result");
const form = document.getElementById("form");
const languageSelect = document.getElementById("language");
const consentCheckbox = document.getElementById("consent");

async function startAnalysis() {
  if (!consentCheckbox.checked) {
    result.innerHTML = `<p style="color:red;">❗Bitte stimmen Sie der Analyse zu (DSGVO-Zustimmung erforderlich).</p>`;
    return;
  }

  const userText = document.getElementById("userInput").value;
  if (!userText.trim()) {
    result.innerHTML = `<p style="color:red;">Bitte geben Sie einen Text ein.</p>`;
    return;
  }

  loader.innerText = "🧠 Analyse läuft, bitte warten...";
  result.innerHTML = "";

  try {
    const response = await fetch("https://web-production-f8648.up.railway.app/analyze", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        text: userText,
        language: languageSelect.value
      }),
    });

    const data = await response.json();

    if (data.error) {
      result.innerHTML = `<p style="color:red;">❌ Fehler: ${data.error}</p>`;
      loader.innerText = "";
      return;
    }

    const formattedGPT = formatGPT(data.gpt_response);
    const emojiHints = data.emojis.map(e =>
      `<li title="${e.bedeutung} – ${e.kontext}"><strong>${e.emoji}</strong>: ${e.bedeutung} (${e.kontext})</li>`
    ).join("");

    const links = data.links.map(l =>
      `<li><a href="${l.url}" target="_blank">${l.url}</a> – <span title="Verifiziert durch Linkprüfung">${l.status}</span></li>`
    ).join("");

    result.innerHTML = `
      <div class="box">
        ${formattedGPT}
        ${emojiHints ? `<h4>🧩 Emoji-Analyse:</h4><ul>${emojiHints}</ul>` : ""}
        ${links ? `<h4>🔗 Linkprüfung:</h4><ul>${links}</ul>` : ""}
      </div>`;
    loader.innerText = "";
  } catch (error) {
    result.innerHTML = `<p style="color:red;">❌ Fehler: ${error}</p>`;
    loader.innerText = "";
  }
}

function formatGPT(text) {
  const labels = [
    "Erkannte Datenarten", "Datenschutz-Risiko", "Bedeutung",
    "achtung.live-Empfehlung", "Tipp", "Quelle"
  ];
  let html = text;
  labels.forEach(label => {
    const regex = new RegExp(`\\*{0,2}${label}\\*{0,2}`, "gi");
    html = html.replace(regex, `<strong style="color:#b30000;">${label}</strong>`);
  });

  html = html.replace(/\n{2,}/g, "<br><br>").replace(/\n/g, "<br>");
  return `<div>${html}</div>`;
}
