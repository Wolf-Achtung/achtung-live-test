async function startAnalysis() {
  const inputText = document.getElementById("textInput").value.trim();
  if (!inputText) return displayError("❗ Bitte gib einen Text ein.");

  const resultContainer = document.getElementById("result");
  resultContainer.innerHTML = "⏳ Analyse läuft…";

  try {
    const res = await fetchWithTimeout("https://web-production-f8648.up.railway.app/analyze", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ text: inputText }),
      timeout: 20000
    });

    const contentType = res.headers.get("content-type");
    if (!contentType || !contentType.includes("application/json")) {
      const raw = await res.text();
      return displayError("❌ Serverfehler:\n" + raw);
    }

    const data = await res.json();
    let html = `
      <div class="feedback-box">
        <p><strong>Erkannte Datenarten:</strong> ${data.detected_data}</p>
        <p><strong>Datenschutz-Risiko:</strong> ${data.risk_level}</p>
        <p><strong>achtung.live-Empfehlung:</strong> ${data.explanation}</p>
        <p><strong>Tipp:</strong> ${data.tip}</p>
        ${data.source ? `<p><strong>Quelle:</strong> <a href="${data.source}" target="_blank">${data.source}</a></p>` : ""}
      </div>
    `;

    // 📂 Medienhilfe laden aus frontend/data/
    if (data.explanation_media?.types?.length) {
      const mediaRes = await fetch("data/helpContent.json");
      const mediaDB = await mediaRes.json();

      data.explanation_media.types.forEach(type => {
        const media = mediaDB[type];
        if (!media) return;

        html += `<div class="media-help"><h4>${media.title}</h4><div class="slides">`;
        media.slides.forEach((src, i) => {
          html += `<img src="media/${src.split('/').pop()}" class="slide ${i === 0 ? 'active' : ''}">`;
        });
        html += `</div><div class="media-buttons">`;
        media.buttons.forEach(btn => {
          html += `<a href="${btn.link}" target="_blank">${btn.label}</a>`;
        });
        html += `</div></div>`;
      });
    }

    resultContainer.innerHTML = html;
    initSlideshow();
  } catch (err) {
    displayError("❌ Fehler: " + err.message);
  }
}

function displayError(msg) {
  const resultContainer = document.getElementById("result");
  resultContainer.innerHTML = `<div class="error">${msg}</div>`;
}

function initSlideshow() {
  const slides = document.querySelectorAll(".slide");
  if (slides.length <= 1) return;
  let current = 0;
  setInterval(() => {
    slides[current].classList.remove("active");
    current = (current + 1) % slides.length;
    slides[current].classList.add("active");
  }, 4000);
}

async function fetchWithTimeout(resource, options = {}) {
  const { timeout = 20000 } = options;
  const controller = new AbortController();
  const id = setTimeout(() => controller.abort(), timeout);
  const response = await fetch(resource, {
    ...options,
    signal: controller.signal
  });
  clearTimeout(id);
  return response;
}
