const backendUrl = "https://web-production-f8648.up.railway.app/analyze";

const textarea = document.getElementById("userText");
const loader = document.getElementById("loader");
const resultDiv = document.getElementById("result");
const consentCheckbox = document.getElementById("consentCheckbox");

// Tooltip bei Mouseover für Quellen
function showTooltip(text, event) {
  const tooltip = document.getElementById("tooltip");
  tooltip.innerHTML = text;
  tooltip.style.display = "block";
  tooltip.style.top = event.pageY + 15 + "px";
  tooltip.style.left = event.pageX + 15 + "px";
}

function hideTooltip() {
  document.getElementById("tooltip").style.display = "none";
}

// Analyse starten
async function startAnalysis() {
  const text = textarea.value.trim();

  // Consent prüfen
  if (!consentCheckbox.checked) {
    resultDiv.innerHTML = "⚠️ Bitte stimmen Sie der Verarbeitung gemäß Datenschutzerklärung zu.";
    return;
  }

  if (text.length === 0) {
    resultDiv.innerHTML = "Bitte geben Sie einen Text ein.";
    return;
  }

  loader.innerText = "Analyse läuft, bitte warten...";
  resultDiv.innerHTML = "";

  try {
    const response = await fetch(backendUrl, {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify({ text: text })
    });

    const data = await response.json();

    loader.innerText = "";

    console.log("Antwort vom Backend:", data);

    if (data.result) {
      let formatted = data.result.replace(/\n/g, "<br>").replace(/\*\*(.*?)\*\*/g, "<strong>$1</strong>");
      resultDiv.innerHTML = formatted;

      // Tooltips nachträglich aktivieren
      const sourceLinks = resultDiv.querySelectorAll(".source-tooltip");
      sourceLinks.forEach(link => {
        link.addEventListener("mouseover", (e) => showTooltip(link.getAttribute("data-tooltip"), e));
        link.addEventListener("mouseout", hideTooltip);
      });

    } else if (data.error) {
      resultDiv.innerHTML = `❌ Fehler: ${data.error}`;
    } else {
      resultDiv.innerHTML = "⚠️ Keine Vorschläge gefunden.<br><br>GPT-Rohantwort: Keine Antwort erhalten";
    }

  } catch (error) {
    console.error("Fehler beim Abrufen:", error);
    loader.innerText = "";
    resultDiv.innerHTML = `❌ Fehler: ${error.message}`;
  }
}
