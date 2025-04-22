const backendURL = "https://web-production-f8648.up.railway.app/debug-gpt";
const input = document.getElementById("userInput");
const output = document.getElementById("output");
const loader = document.getElementById("loader");
const languageSelector = document.getElementById("language");
const consentCheckbox = document.getElementById("consentCheckbox");

input.addEventListener("input", debounce(() => {
  if (consentCheckbox.checked) {
    startAnalysis();
  } else {
    output.innerHTML = "<span style='color:red;'>Bitte stimmen Sie der Analyse gemäß DSGVO zu.</span>";
  }
}, 1200));

function startAnalysis() {
  const userInput = input.value.trim();
  const lang = languageSelector.value;

  if (!userInput) {
    output.innerHTML = "";
    return;
  }

  loader.innerText = "Analyse läuft, Optimierung wird erstellt...";
  output.innerHTML = "";

  fetch(backendURL, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ text: userInput, lang: lang })
  })
    .then(res => res.json())
    .then(data => {
      loader.innerText = "";
      if (data.error) {
        output.innerHTML = `<span style='color:red;'>❌ Fehler: ${data.error}</span>`;
      } else {
        const formatted = formatGPTOutput(data.formatted || data.gpt_raw || "⚠️ Keine Antwort erhalten");
        output.innerHTML = formatted;
        applyTooltipsToLinks();
      }
    })
    .catch(err => {
      loader.innerText = "";
      output.innerHTML = `<span style='color:red;'>❌ Fehler: ${err.message}</span>`;
    });
}

function formatGPTOutput(text) {
  return text
    .replace(/\*\*(.*?)\*\*/g, "<strong style='color:#b30000;'>$1</strong>")
    .replace(/\n{2,}/g, "<br><br>")
    .replace(/\n/g, "<br>")
    .replace(/(https?:\/\/[^\s]+)/g, (match) => {
      return `<a href="${match}" target="_blank" class="trusted-link">${match}</a>`;
    });
}

function applyTooltipsToLinks() {
  const links = document.querySelectorAll(".trusted-link");
  links.forEach(link => {
    link.classList.add("tooltip");
    link.setAttribute("title", "Diese Quelle wurde als vertrauenswürdig eingestuft.");
  });
}

function debounce(fn, delay) {
  let timeout;
  return function () {
    clearTimeout(timeout);
    timeout = setTimeout(() => fn.apply(this, arguments), delay);
  };
}
