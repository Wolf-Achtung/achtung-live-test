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
    if (!consentCheckbox.checked) {
      resultContainer.innerHTML = "❌ Bitte stimmen Sie der Datenverarbeitung zu.";
      return;
    }

    resultContainer.innerHTML = "";
    emojiWarningsContainer.innerHTML = "";
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
        const output = data.gpt_output;

        // Links im Markdown-Stil zu echten HTML-Links umwandeln
        const htmlOutput = output.replace(/\[([^\]]+)]\(([^)]+)\)/g, '<a href="$2" target="_blank">$1</a>');

        resultContainer.innerHTML = `<div>${htmlOutput}</div>`;
        showEmojiWarnings(text);

        // Rewrite-Vorschlag extrahieren
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

  languageSelect.addEventListener("change", () => {
    const lang = languageSelect.value;
    const intro = document.getElementById("introText");

    if (lang === "en") {
      intro.textContent = "Data protection analysis and rewriting (incl. emojis)";
      analyzeButton.textContent = "Start analysis";
    } else if (lang === "fr") {
      intro.textContent = "Analyse de confidentialité et réécriture (avec emojis)";
      analyzeButton.textContent = "Lancer l'analyse";
    } else {
      intro.textContent = "Datenschutzanalyse und Korrektur (inkl. Emojis)";
      analyzeButton.textContent = "Analyse starten";
    }
  });

  // 📋 Kopierfunktion für Rewrite
  document.getElementById("copyRewriteBtn").addEventListener("click", () => {
    const rewrite = document.getElementById("rewriteText").innerText;
    navigator.clipboard.writeText(rewrite)
      .then(() => alert("✅ Vorschlag in Zwischenablage kopiert!"))
      .catch(() => alert("❌ Fehler beim Kopieren."));
  });
});
