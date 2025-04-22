document.addEventListener("DOMContentLoaded", () => {
  const analyzeButton = document.getElementById("analyzeButton");
  const userTextArea = document.getElementById("userText");
  const resultContainer = document.getElementById("result");
  const emojiWarningsContainer = document.getElementById("emojiWarnings");
  const loader = document.getElementById("loader");
  const consentCheckbox = document.getElementById("consentCheckbox");
  const languageSelect = document.getElementById("languageSelect");

  let emojiData = {};
  let debounceTimer;

  fetch("emojiDatabase.json")
    .then((res) => res.json())
    .then((data) => emojiData = data);

  function showEmojiWarnings(text) {
    emojiWarningsContainer.innerHTML = "";
    Object.keys(emojiData).forEach((emoji) => {
      if (text.includes(emoji)) {
        const info = emojiData[emoji];
        const box = document.createElement("div");
        box.innerHTML = `
          <strong>${info.title}</strong><br>
          ${info.text}<br>
          <em>Szenenzuordnung: ${info.group}</em><br>
          <a href="${info.link}" target="_blank">🔗 Quelle</a>
        `;
        emojiWarningsContainer.appendChild(box);
      }
    });
  }

  async function analyzeText() {
    const text = userTextArea.value.trim();
    const selectedLang = languageSelect.value;

    if (!text) return;

    if (!consentCheckbox || !consentCheckbox.checked) {
      loader.style.display = "none";
      resultContainer.innerHTML = "❌ Bitte stimmen Sie der Verarbeitung Ihrer Eingabe gemäß DSGVO zu.";
      return;
    }

    resultContainer.innerHTML = "";
    emojiWarningsContainer.innerHTML = "";
    loader.innerText = "Analyse läuft, Optimierung wird erstellt...";
    loader.style.display = "block";
    document.getElementById("rewriteSection").style.display = "none";

    try {
      const response = await fetch("https://web-production-f8648.up.railway.app/debug-gpt", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ text, lang: selectedLang })
      });

      const data = await response.json();
      loader.style.display = "none";

      if (data.gpt_output) {
        let output = data.gpt_output;

        // ✅ Markdown-Links in HTML konvertieren + Tooltip
        let htmlOutput = output
          .replace(/\[([^\]]+)]\(([^)]+)\)/g, '<a href="$2" target="_blank" class="trusted-link" data-description="$1">$1</a>')
          .replace(/\*\*Erkannte Datenarten:\*\*/g, '<span class="gpt-label">Erkannte Datenarten:</span>')
          .replace(/\*\*Datenschutz-Risiko:\*\*/g, '<span class="gpt-label">Datenschutz-Risiko:</span>')
          .replace(/\*\*Bedeutung:\*\*/g, '<span class="gpt-label">Bedeutung:</span>')
          .replace(/\*\*achtung\.live-Empfehlung:\*\*/g, '<span class="gpt-label">achtung.live-Empfehlung:</span>')
          .replace(/\*\*Tipp:\*\*/g, '<span class="gpt-label">Tipp:</span>')
          .replace(/\*\*Quelle:\*\*/g, '<span class="gpt-label">Quelle:</span>');

        resultContainer.innerHTML = `<div>${htmlOutput}</div>`;
        showEmojiWarnings(text);

        // Tooltip bei Hover anzeigen
        document.querySelectorAll(".trusted-link").forEach(link => {
          link.addEventListener("mouseenter", () => {
            const tip = document.createElement("div");
            tip.className = "tooltip-box";
            tip.innerText = "✅ Geprüfte Quelle: " + link.dataset.description;
            document.body.appendChild(tip);
            const rect = link.getBoundingClientRect();
            tip.style.left = rect.left + "px";
            tip.style.top = (rect.bottom + 5) + "px";
          });
          link.addEventListener("mouseleave", () => {
            const tip = document.querySelector(".tooltip-box");
            if (tip) tip.remove();
          });
        });

        // Rewrite-Tipp extrahieren
        const match = output.match(/(?:\*\*Tipp:\*\*|Rewrite-Vorschlag:?)\s*([\s\S]*?)(?:\n|$)/i);
        if (match && match[1]) {
          const clean = match[1].trim();
          document.getElementById("rewriteText").innerText = clean;
          document.getElementById("rewriteSection").style.display = "block";
        }
      } else {
        resultContainer.innerHTML = "⚠️ Keine Vorschläge gefunden.";
      }
    } catch (err) {
      loader.style.display = "none";
      resultContainer.innerHTML = `❌ Fehler: ${err.message}`;
    }
  }

  analyzeButton.addEventListener("click", analyzeText);
  userTextArea.addEventListener("input", () => {
    clearTimeout(debounceTimer);
    debounceTimer = setTimeout(analyzeText, 1000);
  });
});
