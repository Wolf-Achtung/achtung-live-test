document.addEventListener("DOMContentLoaded", function () {
  const analyzeButton = document.getElementById("analyzeButton");
  const resultContainer = document.getElementById("result");
  const loader = document.getElementById("loader");
  const emojiWarningsContainer = document.getElementById("emojiWarnings");

  let emojiData = {};

  fetch("emojiDatabase.json")
    .then(response => response.json())
    .then(data => {
      emojiData = data;
    });

  function showEmojiWarnings(text) {
    emojiWarningsContainer.innerHTML = "";
    Object.keys(emojiData).forEach((emoji) => {
      if (text.includes(emoji)) {
        const info = emojiData[emoji];

        const box = document.createElement("div");
        const label = document.createElement("strong");
        const textEl = document.createElement("p");
        const link = document.createElement("a");
        const tooltip = document.createElement("span");

        box.appendChild(label);
        box.appendChild(textEl);
        box.appendChild(link);
        box.appendChild(tooltip);

        label.textContent = info.title;
        textEl.textContent = info.text;
        link.href = info.link;
        link.textContent = "Mehr erfahren";
        link.target = "_blank";

        tooltip.textContent = "ⓘ";
        tooltip.title = info.text;

        box.appendChild(label);
        emojiWarningsContainer.appendChild(box);

        Object.assign(box.style, {
          background: "#fff3cd",
          borderLeft: "4px solid #ffc107",
          padding: "12px",
          margin: "12px 0",
          borderRadius: "4px",
          position: "relative"
        });
      }
    });
  }

  analyzeButton.addEventListener("click", async () => {
    const userText = document.getElementById("userText").value.trim();

    resultContainer.innerHTML = "";
    emojiWarningsContainer.innerHTML = "";
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
        showEmojiWarnings(data.gpt_output);
      } else {
        resultContainer.innerHTML = "⚠️ Keine Vorschläge gefunden.<br><br><strong>GPT-Rohantwort:</strong><br>Keine Antwort erhalten.";
      }
    } catch (error) {
      loader.style.display = "none";
      resultContainer.innerHTML = `❌ Fehler: ${error.message}`;
    }
  });
});
