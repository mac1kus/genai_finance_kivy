const chatBox = document.getElementById("chat-box");
const typingRow = document.getElementById("typing-row");
const chatPopup = document.getElementById("chatPopup");
const botPrompt = document.getElementById("botPrompt");
const signalCard = document.getElementById("signalCard");
const signalTicker = document.getElementById("signalTicker");
const signalPrice = document.getElementById("signalPrice");
const signalBadge = document.getElementById("signalBadge");
const signalConf = document.getElementById("signalConf");

let chatOpened = false;
let stockChart = null;

function toggleChat() {
  const isOpen = chatPopup.classList.toggle("open");
  if (isOpen) {
    botPrompt.style.display = "none";
    if (!chatOpened) {
      chatOpened = true;
      setTimeout(() => {
        appendMessage("bot", "Good day! I'm ARIA, your Advanced Retail Investment Advisor. 📈\n\nI can analyse stocks on the Indian NSE and US markets — just tell me which stock you'd like to discuss.");
      }, 300);
    }
  }
}

function renderMarkdown(text) {
  return text
    .replace(/\*\*(.*?)\*\*/g, "<strong>$1</strong>")
    .replace(/\*(.*?)\*/g, "<em>$1</em>")
    .replace(/\n/g, "<br/>");
}

function appendMessage(from, text) {
  const row = document.createElement("div");
  row.className = `msg-row ${from}`;

  const avatar = document.createElement("div");
  avatar.className = `msg-avatar ${from}`;
  avatar.textContent = from === "bot" ? "🤖" : "🙋";

  const right = document.createElement("div");
  const bubble = document.createElement("div");
  bubble.className = `bubble ${from}`;
  bubble.innerHTML = renderMarkdown(text);
  right.appendChild(bubble);

  if (from === "bot") {
    row.appendChild(avatar);
    row.appendChild(right);
  } else {
    row.appendChild(right);
    row.appendChild(avatar);
  }

  chatBox.appendChild(row);
  chatBox.scrollTop = chatBox.scrollHeight;
}

function showTyping(show) {
  typingRow.classList.toggle("visible", show);
  if (show) chatBox.scrollTop = chatBox.scrollHeight;
}

function drawChart(meta) {
  const container = document.getElementById("chartContainer");
  const canvas = document.getElementById("stockChart");

  if (!meta || !meta.prices_20d || meta.prices_20d.length === 0) {
    container.style.display = "none";
    return;
  }

  container.style.display = "block";

  const prices = meta.prices_20d;
  const labels = meta.dates_20d.map(d => d.slice(5)); // show MM-DD
  const ma20 = prices.reduce((a, b) => a + b, 0) / prices.length;
  const ma20Line = new Array(prices.length).fill(parseFloat(ma20.toFixed(2)));
  const currentPrice = prices[prices.length - 1];
  const isUp = currentPrice >= prices[0];

  if (stockChart) stockChart.destroy();

  stockChart = new Chart(canvas, {
    type: "line",
    data: {
      labels: labels,
      datasets: [
        {
          label: `${meta.ticker} Price`,
          data: prices,
          borderColor: isUp ? "#1A7F5A" : "#C0392B",
          backgroundColor: isUp ? "rgba(26,127,90,0.08)" : "rgba(192,57,43,0.08)",
          borderWidth: 2,
          pointRadius: 2,
          fill: true,
          tension: 0.3,
        },
        {
          label: "20-Day MA",
          data: ma20Line,
          borderColor: "#C9A84C",
          borderWidth: 1.5,
          borderDash: [5, 4],
          pointRadius: 0,
          fill: false,
        }
      ]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: { labels: { font: { size: 10 }, color: "#0A1628" } },
        tooltip: { mode: "index", intersect: false }
      },
      scales: {
        x: { ticks: { font: { size: 9 }, color: "#8892A4", maxTicksLimit: 7 }, grid: { display: false } },
        y: { ticks: { font: { size: 9 }, color: "#8892A4" }, grid: { color: "rgba(0,0,0,0.05)" } }
      }
    }
  });

  chatBox.scrollTop = chatBox.scrollHeight;
}

function updateSignalCard(meta) {
  if (!meta || !meta.ticker) {
    signalCard.classList.remove("visible");
    return;
  }

  signalTicker.textContent = meta.ticker;
  signalPrice.textContent = `${meta.currency}${meta.current_price}`;
  signalBadge.textContent = meta.signal;
  signalConf.textContent = `Confidence: ${meta.confidence}%`;

  signalBadge.className = "signal-badge";
  const sig = meta.signal || "";
  if (sig.includes("BUY"))  signalBadge.classList.add("badge-buy");
  else if (sig.includes("SELL")) signalBadge.classList.add("badge-sell");
  else signalBadge.classList.add("badge-hold");

  signalCard.classList.add("visible");
  drawChart(meta);
}

async function sendMsg(text) {
  if (!text.trim()) return;
  appendMessage("user", text);
  document.getElementById("user-input").value = "";
  autoResize(document.getElementById("user-input"));
  showTyping(true);

  try {
    const res = await fetch("/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message: text })
    });
    const data = await res.json();
    showTyping(false);
    appendMessage("bot", data.reply);
    updateSignalCard(data.stock_meta);
  } catch (e) {
    showTyping(false);
    appendMessage("bot", "I apologise — there seems to be a server error. Please ensure Flask is running.");
  }
}

function sendFromInput() {
  const val = document.getElementById("user-input").value.trim();
  if (val) sendMsg(val);
}

function handleKey(e) {
  if (e.key === "Enter" && !e.shiftKey) {
    e.preventDefault();
    sendFromInput();
  }
}

function autoResize(el) {
  el.style.height = "auto";
  el.style.height = Math.min(el.scrollHeight, 80) + "px";
}