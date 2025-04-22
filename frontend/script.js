document.addEventListener("DOMContentLoaded", function () {
  const analyzeButton = document.getElementById("analyzeButton");
  const resultContainer = document.getElementById("result");
  const loader = document.getElementById("loader");

  analyzeButton.addEventListener("click", async () => {
    const userText = document.getElementById("userText").value.trim();

    resultContainer.innerHTML = "";
    loader.style.display = "block";

    if (!userText) {
      loader.style.display = "none";
      resultContainer.innerHTML = "⚠️ Bitte einen Text eingeben.";
      return;
    }

    try {
      const response = await fetch("https://web-production-f8648.up.railway.app/debug-gpt", {
        method: "POST",
        headers: {
          "Content-Type": "application/json"
        },
        body: JSON.stringify({ text: userText })
      });

      const data = await response.json();
      loader.style.display = "none";

      if (data.gpt_output) {
        resultContainer.innerHTML = `<div style="white-space: pre-wrap;">${data.gpt_output}</div>`;
        
      } else {
        resultContainer.innerHTML = "⚠️ Keine Vorschläge gefunden.<br><br><strong>GPT-Rohantwort:</strong><br>Keine Antwort erhalten.";
      }
    } catch (error) {
      loader.style.display = "none";
      console.error("Fehler beim Abrufen:", error);
      resultContainer.innerHTML = `❌ Fehler beim Verbinden mit dem Server.<br>${error.message}`;
    }
  });
});
