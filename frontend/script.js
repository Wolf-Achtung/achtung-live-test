async function startAnalysis() {
  const inputText = document.getElementById("textInput").value.trim();
  if (!inputText) return alert("Bitte gib einen Text ein.");

  const resultContainer = document.getElementById("result");
  resultContainer.innerHTML = "⏳ Analyse läuft…";

  const res = await fetch("https://web-production-f8648.up.railway.app/analyze", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ text: inputText })
  });

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

  // 📂 Medientypen nachladen aus JSON
  if (data.explanation_media?.types?.length) {
    const response = await fetch("/data/helpContent.json");
    const mediaDB = await response.json();

    data.explanation_media.types.forEach(type => {
      const media = mediaDB[type];
      if (!media) return;

      html += `<div class="media-help"><h4>${media.title}</h4><div class="slides">`;
      media.slides.forEach((src, i) => {
        html += `<img src="${src}" class="slide ${i === 0 ? 'active' : ''}">`;
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
