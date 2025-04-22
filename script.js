const backendUrl = "https://web-production-f8648.up.railway.app/analyze"; // deine Backend-Route

async function startAnalysis() {
  const text = document.getElementById("userInput").value.trim();
  const consent = document.getElementById("consentCheckbox").checked;
  const lang = document.getElementById("language").value;
  const loader = document.getElementById("loader");
  const output = document.getElementById("output");

  if (!consent) {
    output.innerHTML = "⚠️ Bitte stimmen Sie der Datenschutzerklärung zu, um fortzufahren.";
    return;
  }

  if (!text) {
    output.innerHTML = "⚠️ Bitte geben Sie einen Text ein.";
    return;
  }

  loader.innerText = "Analyse läuft, Optimierung wird erstellt...";
  output.innerHTML = "";

  try {
    const response = await fetch(backendUrl, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ text: text, language: lang })
    });

    const result = await response.json();
    if (result.error) {
      output.innerHTML = `❌ Fehler: ${result.error}`;
      loader.innerText = "";
      return;
    }

    let formatted = result.output || result.gpt_raw || "⚠️ Keine Rückmeldung vom System.";

    // Ersetze Linkformate wie [Text](URL) mit echten anklickbaren HTML-Links
    formatted = formatted.replace(/\[([^\]]+)]\((https?:\/\/[^\s)]+)\)/g, (match, text, url) => {
      return `<a href="${url}" target="_blank" rel="noopener noreferrer" class="trusted-link tooltip" title="Geprüfte Quelle">${text}</a>`;
    });

    // Fettformatierung beibehalten
    formatted = formatted.replace(/\*\*(.*?)\*\*/g, "<strong style='color:#b30000;'>$1</strong>");

    // Zeilenumbrüche erhalten
    formatted = formatted.replace(/\n/g, "<br>");

    output.innerHTML = formatted;
  } catch (error) {
    output.innerHTML = `❌ Fehler: ${error.message}`;
  } finally {
    loader.innerText = "";
  }
}
