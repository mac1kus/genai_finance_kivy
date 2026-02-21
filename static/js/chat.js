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

function updateSignalCard(meta) {
  if (!meta || !meta.ticker) {
    signalCard.classList.remove("visible");
    return;
  }

  signalTicker.textContent = meta.ticker;
  signalPrice.textContent = `${meta.currency}${meta.current_price}`;
  signalBadge.textContent = meta.signal;
  signalConf.textContent = `Confidence: ${meta.confidence}%`;

  // Set badge colour based on signal
  signalBadge.className = "signal-badge";
  const sig = meta.signal || "";
  if (sig.includes("BUY"))  signalBadge.classList.add("badge-buy");
  else if (sig.includes("SELL")) signalBadge.classList.add("badge-sell");
  else signalBadge.classList.add("badge-hold");

  signalCard.classList.add("visible");
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