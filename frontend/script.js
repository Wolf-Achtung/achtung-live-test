const backendUrl = "https://web-production-f8648.up.railway.app"; // aktuelle API-URL

async function startAnalysis() {
  const input = document.getElementById("userInput").value.trim();
  const lang = document.getElementById("language").value;
  const consent = document.getElementById("consentCheckbox").checked;
  const result = document.getElementById("result");
  const loader = document.getElementById("loader");

  result.innerHTML = "";
  loader.innerText = "Analyse läuft, bitte warten...";

  if (!consent) {
    loader.innerText = "";
    result.innerHTML = `<p style="color: darkred; font-weight: bold;">❌ Bitte stimmen Sie der Analyse zu, bevor Sie fortfahren.</p>`;
    return;
  }

  try {
    const response = await fetch(`${backendUrl}/analyze`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ text: input, language: lang }),
    });

    const data = await response.json();

    if (data.error) {
      loader.innerText = "";
      result.innerHTML = `<p style="color: darkred;">❌ Fehler: ${data.error}</p>`;
      return;
    }

    const formatted = formatGPT(data.gpt_output || "");
    const links = renderLinkCheck(data.link_check || []);
    result.innerHTML = formatted + links;
    loader.innerText = "";
  } catch (err) {
    loader.innerText = "";
    result.innerHTML = `<p style="color: darkred;">❌ Fehler: ${err.message}</p>`;
  }
}

function formatGPT(text) {
  return (
    "<div style='white-space:pre-line; font-size:1rem; line-height:1.6;'>" +
    text
      .replace(/\*\*(.*?)\*\*/g, "<strong style='color:#b30000;'>$1</strong>")
      .replace(/\n/g, "<br>") +
    "</div>"
  );
}

function renderLinkCheck(linkData) {
  if (!linkData || linkData.length === 0) return "";

  let html = `<div style="margin-top:1.5rem; border-top: 1px solid #ccc; padding-top: 1rem;">
  <strong style="color:#0052cc;">🔗 Link-Analyse:</strong><ul style="padding-left: 1.2rem;">`;

  linkData.forEach(link => {
    html += `<li><a href="${link.url}" target="_blank" style="color: #004080; text-decoration: underline;">${link.url}</a>: <span>${link.status}</span></li>`;
  });

  html += `</ul></div>`;
  return html;
}
