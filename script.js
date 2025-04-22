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

    try {
      const response = await fetch("https://web-production-f8648.up.railway.app/debug-gpt", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ text, lang: selectedLang })
      });

      const data = await response.json();
      loader.style.display = "none";

      if (data.gpt_output) {
        resultContainer.innerHTML = `<div>${data.gpt_output}</div>`;
        showEmojiWarnings(text);
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
    debounceTimer = setTimeout(analyzeText, 1000); // Auto-Analyse nach 1 Sekunde
  });

  languageSelect.addEventListener("change", () => {
    const lang = languageSelect.value;
    const intro = document.getElementById("introText");

    if (lang === "en") {
      intro.textContent = "Rewrite & privacy check with emoji analysis";
      analyzeButton.textContent = "Start analysis";
      consentCheckbox.nextSibling.textContent = " I agree to the analysis as per the ";
    } else if (lang === "fr") {
      intro.textContent = "Révision & vérification de confidentialité avec emoji";
      analyzeButton.textContent = "Démarrer l'analyse";
      consentCheckbox.nextSibling.textContent = " J'accepte l'analyse de mon texte selon la ";
    } else {
      intro.textContent = "Rewrite- & Emoji-Datenschutzanalyse";
      analyzeButton.textContent = "Analyse starten";
      consentCheckbox.nextSibling.textContent = " Ich stimme der Verarbeitung meiner Eingabe gemäß der ";
    }
  });
});
