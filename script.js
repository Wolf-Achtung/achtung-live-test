document.addEventListener("DOMContentLoaded", function () {
  const analyzeButton = document.getElementById("analyzeButton");
  const resultContainer = document.getElementById("result");
  const loader = document.getElementById("loader");
  const emojiWarningsContainer = document.getElementById("emojiWarnings");

  // Emoji-Datenbank für Warnhinweise
  const emojiMap = {
    "💙": {
      title: "Blaues Herz 💙",
      text: "Kann als Symbol für rechtspopulistische Gruppen wie die Identitäre Bewegung oder AfD verwendet werden. Auch bei Ukraine-Solidarität gebräuchlich – Kontext entscheidet.",
      link: "https://www.campact.de/emoji-codes/"
    },
    "🐸": {
      title: "Frosch-Emoji 🐸",
      text: "Oft Symbol der Alt-Right-Bewegung ('Pepe the Frog'), verwendet in rechtsextremen Memes.",
      link: "https://www.adl.org/resources/hate-symbol/pepe-the-frog"
    },
    "🔫": {
      title: "Pistole 🔫",
      text: "Kann auf Gewalt, Bedrohung oder toxische Subkulturen hinweisen.",
      link: "https://www.bpb.de"
    },
    "🧿": {
      title: "Nazar-Auge 🧿",
      text: "Im religiösen oder spirituellen Kontext verbreitet. In Verschwörungsszenen teils als okkultes Zeichen fehlgedeutet.",
      link: "https://de.wikipedia.org/wiki/Nazar_(Amulett)"
    },
    "☠️": {
      title: "Totenkopf ☠️",
      text: "Kann als Symbol von Gewalt oder in subkulturellen Codes wie Darknet-Chats erscheinen.",
      link: "https://www.bpb.de"
    }
    // Weitere Emojis ergänzbar
  };

  function showEmojiWarnings(text) {
    let warnings = "";
    Object.keys(emojiMap).forEach((emoji) => {
      if (text.includes(emoji)) {
        const info = emojiMap[emoji];
        warnings += `
          <div style="background:#fff3cd; border-left:4px solid #ffc107; padding:12px; margin:12px 0; border-radius:4px;">
            <strong>${info.title}</strong><br>
            ${info.text}<br>
            <a href="${info.link}" target="_blank">Mehr erfahren</a>
          </div>
        `;
      }
    });
    emojiWarningsContainer.innerHTML = warnings;
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
      console.error("Fehler beim Abrufen:", error);
      resultContainer.innerHTML = `❌ Fehler beim Verbinden mit dem Server.<br>${error.message}`;
    }
  });
});
