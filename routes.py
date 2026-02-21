from flask import render_template, request, jsonify, session
from groq import Groq
import os
import uuid  # ⬅️ ADDED THIS BACK
import re
from dotenv import load_dotenv
from genai import get_system_prompt, analyze_stock, INDIAN_STOCKS, US_STOCKS
from app_creator import app  # Import app from the neutral file
#import ollama

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))
conversations = {}

def get_history(sid):
    if sid not in conversations:
        conversations[sid] = []
    return conversations[sid]

# ─────────────────────────────────────────────
#  STOCK NAME EXTRACTOR
# ─────────────────────────────────────────────

def extract_stock_name(message: str) -> str | None:
    msg_lower = message.lower()

    # Check against known Indian stock names
    for key in INDIAN_STOCKS:
        if key in msg_lower:
            return key

    # Check against known US stock names
    for key in US_STOCKS:
        if key in msg_lower:
            return key

    # Check for all-caps ticker pattern (e.g. AAPL, TSLA, MSFT)
    matches = re.findall(r'\b[A-Z]{2,5}\b', message)
    for m in matches:
        skip = {"I", "A", "THE", "AND", "OR", "BUY", "SELL", "MY", "IN", "ON",
                "FOR", "TO", "AT", "IS", "IT", "US", "DO", "NSE", "BSE", "PE"}
        if m not in skip:
            return m

    # Keyword-after-pattern
    patterns = [
        r"(?:about|analyse|analyze|check|look at|invest in|buy|sell|thoughts on|opinion on)\s+([A-Za-z\s&]+?)(?:\?|$|\.|\s+stock|\s+share)",
        r"([A-Za-z\s&]+?)\s+(?:stock|share|equity|scrip)\b",
    ]
    for pat in patterns:
        match = re.search(pat, message, re.IGNORECASE)
        if match:
            candidate = match.group(1).strip()
            if 2 < len(candidate) < 30:
                return candidate

    return None


def format_stock_context(analysis: dict) -> str:
    if "error" in analysis:
        return f"STOCK LOOKUP ERROR: {analysis['error']}"

    ind = analysis["indicators"]
    reasons_text = "\n".join(f"  • {r}" for r in analysis["reasons"])
    currency = analysis["currency"]

    entry = f"{currency}{analysis['entry_price']}" if analysis["entry_price"] else "N/A"
    target = f"{currency}{analysis['target_price']}" if analysis["target_price"] else "N/A"
    stop = f"{currency}{analysis['stop_loss']}" if analysis["stop_loss"] else "N/A"

    return f"""
Stock: {analysis['name']} ({analysis['ticker']})
Sector: {analysis['sector']}
Current Price: {currency}{analysis['current_price']}
52-Week High: {currency}{analysis['52w_high']} | Low: {currency}{analysis['52w_low']}
P/E Ratio: {analysis['pe_ratio']}

--- Technical Indicators ---
MA20: {currency}{ind['ma20']} | MA50: {currency}{ind['ma50']} | MA200: {currency}{ind['ma200']}
RSI (14): {ind['rsi']}
MACD: {ind['macd']}
Bollinger Upper: {currency}{ind['bb_upper']} | Lower: {currency}{ind['bb_lower']}
30-Day Momentum: {ind['momentum_30d']}%
Trend Slope (60-day): {ind['trend_slope']}

--- Signal ---
Recommendation: {analysis['signal']}
Confidence: {analysis['confidence']}%
Technical Score: {analysis['score']}/10

--- Price Levels ---
Suggested Entry: {entry}
Target Price (12% profit): {target}
Stop-Loss (7% maximum loss): {stop}

--- Key Reasons ---
{reasons_text}
"""

# ─────────────────────────────────────────────
#  ROUTES
# ─────────────────────────────────────────────

@app.route("/")
def index():
    if "session_id" not in session:
        # This line requires 'import uuid'
        session["session_id"] = str(uuid.uuid4())
        #session["session_id"] = "default_user"
    return render_template("index.html")


@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json()
    user_msg = data.get("message", "").strip()

    if not user_msg:
        return jsonify({"reply": "Please type your query."})

    sid = session.get("session_id", "default")
    history = get_history(sid)

    # ── Detect stock mention and run analysis ──
    stock_name = extract_stock_name(user_msg)
    stock_context = ""
    stock_meta = {}

    if stock_name:
        try:
            analysis = analyze_stock(stock_name)
            stock_context = format_stock_context(analysis)
            stock_meta = {
                "ticker": analysis.get("ticker", ""),
                "signal": analysis.get("signal", ""),
                "confidence": analysis.get("confidence", ""),
                "current_price": analysis.get("current_price", ""),
                "currency": analysis.get("currency", ""),
                "prices_20d": analysis.get("prices_20d", []),
                "dates_20d": analysis.get("dates_20d", []),
            }
        except Exception as e:
            stock_context = f"STOCK DATA ERROR: {str(e)}"

    history.append({"role": "user", "content": user_msg})

    try:
        # # 🟢 LOCAL OLLAMA FIX
        # response = ollama.chat(
        #     model="llama3.2",
        #     #model="codellama",
        #     options={
        #         "num_ctx": 4096  # This limits memory usage to ~200MB
        #         #instead of ~800MB
        #     },
        #     messages=[{"role": "system", "content": get_system_prompt(stock_context)}] + history
        # )
        # reply = response['message']['content']  # Ollama returns a dictionary-style object

        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "system", "content": get_system_prompt(stock_context)}] + history,
            max_tokens=512,
        )
        reply = response.choices[0].message.content

        history.append({"role": "assistant", "content": reply})
        return jsonify({"reply": reply, "stock_meta": stock_meta})

    except Exception as e:
        return jsonify({"reply": f"I apologise, I encountered an error: {str(e)}"})

    #ollama chat() is short cut for local computers
    #client.chat.completions.create standard format meant for GROQ
    # for massive cloud networks.(it follows open API STANDARD)
    #both of the above are libraries
    #client object manages connections, security keys, and
    #complex traffic for thousands of users at once.

@app.route("/reset", methods=["POST"])
def reset():
    sid = session.get("session_id", "default")
    conversations[sid] = []
    return jsonify({"status": "ok"})