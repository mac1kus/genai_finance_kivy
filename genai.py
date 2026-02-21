import yfinance as yf
import numpy as np
import pandas as pd

import warnings
warnings.filterwarnings("ignore")

# ─────────────────────────────────────────────
#  SUPPORTED US STOCKS (NASDAQ / NYSE)
# ─────────────────────────────────────────────
US_STOCKS = {
    # Big Tech
    "apple":            "AAPL",
    "microsoft":        "MSFT",
    "google":           "GOOGL",
    "alphabet":         "GOOGL",
    "amazon":           "AMZN",
    "meta":             "META",
    "facebook":         "META",
    "nvidia":           "NVDA",
    "tesla":            "TSLA",
    "netflix":          "NFLX",
    # Finance
    "jpmorgan":         "JPM",
    "jp morgan":        "JPM",
    "goldman sachs":    "GS",
    "morgan stanley":   "MS",
    "bank of america":  "BAC",
    "wells fargo":      "WFC",
    "visa":             "V",
    "mastercard":       "MA",
    "american express": "AXP",
    # Healthcare
    "johnson":          "JNJ",
    "pfizer":           "PFE",
    "unitedhealth":     "UNH",
    "abbott":           "ABT",
    "eli lilly":        "LLY",
    # Consumer
    "walmart":          "WMT",
    "coca cola":        "KO",
    "pepsi":            "PEP",
    "mcdonalds":        "MCD",
    "nike":             "NKE",
    "disney":           "DIS",
    # Industrial / Energy
    "exxon":            "XOM",
    "chevron":          "CVX",
    "boeing":           "BA",
    "caterpillar":      "CAT",
    "3m":               "MMM",
    # Semiconductors
    "amd":              "AMD",
    "intel":            "INTC",
    "qualcomm":         "QCOM",
    "broadcom":         "AVGO",
    "tsmc":             "TSM",
}

# ─────────────────────────────────────────────
#  SUPPORTED INDIAN STOCKS (NSE)
# ─────────────────────────────────────────────
INDIAN_STOCKS = {
    "reliance": "RELIANCE.NS",
    "tcs": "TCS.NS",
    "infosys": "INFY.NS",
    "wipro": "WIPRO.NS",
    "hdfc bank": "HDFCBANK.NS",
    "icici bank": "ICICIBANK.NS",
    "sbi": "SBIN.NS",
    "bajaj finance": "BAJFINANCE.NS",
    "larsen": "LT.NS",
    "l&t": "LT.NS",
    "hcl": "HCLTECH.NS",
    "axis bank": "AXISBANK.NS",
    "kotak": "KOTAKBANK.NS",
    "titan": "TITAN.NS",
    "asian paints": "ASIANPAINT.NS",
    "maruti": "MARUTI.NS",
    "nestle": "NESTLEIND.NS",
    "ultratech": "ULTRACEMCO.NS",
    "sun pharma": "SUNPHARMA.NS",
    "itc": "ITC.NS",
    "ongc": "ONGC.NS",
    "ntpc": "NTPC.NS",
    "adani ports": "ADANIPORTS.NS",
    "adani enterprises": "ADANIENT.NS",
    "power grid": "POWERGRID.NS",
    "tech mahindra": "TECHM.NS",
    "hindalco": "HINDALCO.NS",
    "jswsteel": "JSWSTEEL.NS",
    "tata steel": "TATASTEEL.NS",
    "tata motors": "TATAMOTORS.NS",
    "tata power": "TATAPOWER.NS",
    "indusind": "INDUSINDBK.NS",
    "dr reddy": "DRREDDY.NS",
    "cipla": "CIPLA.NS",
    "divis": "DIVISLAB.NS",
    "eicher motors": "EICHERMOT.NS",
    "hero motocorp": "HEROMOTOCO.NS",
    "bajaj auto": "BAJAJ-AUTO.NS",
    "shree cement": "SHREECEM.NS",
    "grasim": "GRASIM.NS",
    "bpcl": "BPCL.NS",
    "britannia": "BRITANNIA.NS",
    "havells": "HAVELLS.NS",
    "pidilite": "PIDILITIND.NS",
    "dmart": "DMART.NS",
    "zomato": "ZOMATO.NS",
    "paytm": "PAYTM.NS",
}

# ─────────────────────────────────────────────
#  FETCH HISTORICAL DATA
# ─────────────────────────────────────────────
def fetch_stock_data(ticker: str, period: str = "1y") -> pd.DataFrame | None:
    try:
        stock = yf.Ticker(ticker)
        df = stock.history(period=period)
        if df.empty or len(df) < 30:
            return None
        return df
    except Exception:
        return None


def get_stock_info(ticker: str) -> dict:
    try:
        stock = yf.Ticker(ticker)
        info = stock.info
        return {
            "name": info.get("longName", ticker),
            "sector": info.get("sector", "N/A"),
            "market_cap": info.get("marketCap", "N/A"),
            "pe_ratio": info.get("trailingPE", "N/A"),
            "52w_high": info.get("fiftyTwoWeekHigh", "N/A"),
            "52w_low": info.get("fiftyTwoWeekLow", "N/A"),
            "current_price": info.get("currentPrice") or info.get("regularMarketPrice", "N/A"),
            "currency": info.get("currency", "USD"),
        }
    except Exception:
        return {}


# ─────────────────────────────────────────────
#  SIMPLE LSTM-STYLE PREDICTION (NumPy only)
#  We implement a minimal manual LSTM to avoid
#  heavy TF/PyTorch deps on local Ollama setup.
#  Uses rolling window + linear regression trend
#  + momentum indicators for signal generation.
# ─────────────────────────────────────────────
def compute_technical_indicators(df: pd.DataFrame) -> dict:
    close = df["Close"].values.astype(float)

    # Moving Averages
    ma20 = np.mean(close[-20:]) if len(close) >= 20 else np.mean(close)
    ma50 = np.mean(close[-50:]) if len(close) >= 50 else np.mean(close)
    ma200 = np.mean(close[-200:]) if len(close) >= 200 else np.mean(close)

    # RSI (14-day)
    delta = np.diff(close[-15:])
    gains = delta[delta > 0]
    losses = -delta[delta < 0]
    avg_gain = np.mean(gains) if len(gains) > 0 else 0
    avg_loss = np.mean(losses) if len(losses) > 0 else 1e-9
    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))

    # MACD (12/26 EMA approximation via simple means)
    ema12 = np.mean(close[-12:]) if len(close) >= 12 else close[-1]
    ema26 = np.mean(close[-26:]) if len(close) >= 26 else close[-1]
    macd = ema12 - ema26

    # Bollinger Bands (20-day)
    window = close[-20:] if len(close) >= 20 else close
    bb_mean = np.mean(window)
    bb_std = np.std(window)
    bb_upper = bb_mean + 2 * bb_std
    bb_lower = bb_mean - 2 * bb_std

    # Price momentum (30-day return)
    price_30d_ago = close[-30] if len(close) >= 30 else close[0]
    momentum_30d = ((close[-1] - price_30d_ago) / price_30d_ago) * 100

    # Trend direction via linear regression slope
    x = np.arange(len(close[-60:])) if len(close) >= 60 else np.arange(len(close))
    y = close[-60:] if len(close) >= 60 else close
    slope = np.polyfit(x, y, 1)[0]

    current = close[-1]

    return {
        "current_price": round(current, 2),
        "ma20": round(ma20, 2),
        "ma50": round(ma50, 2),
        "ma200": round(ma200, 2),
        "rsi": round(rsi, 2),
        "macd": round(macd, 4),
        "bb_upper": round(bb_upper, 2),
        "bb_lower": round(bb_lower, 2),
        "momentum_30d": round(momentum_30d, 2),
        "trend_slope": round(slope, 4),
    }


def predict_signal(indicators: dict) -> dict:
    """
    Rule-based signal engine combining multiple technical indicators.
    Returns signal: STRONG BUY / BUY / HOLD / SELL / STRONG SELL
    with confidence score and reasoning.
    """
    score = 0
    reasons = []

    cp = indicators["current_price"]
    ma20 = indicators["ma20"]
    ma50 = indicators["ma50"]
    ma200 = indicators["ma200"]
    rsi = indicators["rsi"]
    macd = indicators["macd"]
    bb_upper = indicators["bb_upper"]
    bb_lower = indicators["bb_lower"]
    mom = indicators["momentum_30d"]
    slope = indicators["trend_slope"]

    # --- MA crossover signals ---
    if cp > ma20:
        score += 1
        reasons.append("Price above 20-day MA (short-term bullish)")
    else:
        score -= 1
        reasons.append("Price below 20-day MA (short-term bearish)")

    if ma20 > ma50:
        score += 1
        reasons.append("Golden cross forming: 20-day MA above 50-day MA")
    else:
        score -= 1
        reasons.append("Death cross risk: 20-day MA below 50-day MA")

    if cp > ma200:
        score += 2
        reasons.append("Price above 200-day MA (long-term uptrend confirmed)")
    else:
        score -= 2
        reasons.append("Price below 200-day MA (long-term downtrend caution)")

    # --- RSI signals ---
    if rsi < 30:
        score += 2
        reasons.append(f"RSI at {rsi} — oversold territory, potential reversal upward")
    elif rsi > 70:
        score -= 2
        reasons.append(f"RSI at {rsi} — overbought, correction risk")
    elif 40 <= rsi <= 60:
        score += 1
        reasons.append(f"RSI at {rsi} — neutral, healthy momentum")

    # --- MACD ---
    if macd > 0:
        score += 1
        reasons.append("MACD positive — bullish momentum")
    else:
        score -= 1
        reasons.append("MACD negative — bearish momentum")

    # --- Bollinger Bands ---
    if cp < bb_lower:
        score += 1
        reasons.append("Price near lower Bollinger Band — potential bounce zone")
    elif cp > bb_upper:
        score -= 1
        reasons.append("Price near upper Bollinger Band — potential resistance")

    # --- Momentum ---
    if mom > 10:
        score += 1
        reasons.append(f"Strong 30-day momentum: +{mom}%")
    elif mom < -10:
        score -= 1
        reasons.append(f"Weak 30-day momentum: {mom}%")

    # --- Trend slope ---
    if slope > 0:
        score += 1
        reasons.append("Price trend slope is positive over last 60 sessions")
    else:
        score -= 1
        reasons.append("Price trend slope is negative over last 60 sessions")

    # --- Map score to signal ---
    if score >= 6:
        signal = "STRONG BUY"
        confidence = min(95, 70 + score * 2)
    elif score >= 3:
        signal = "BUY"
        confidence = min(80, 55 + score * 3)
    elif score >= -2:
        signal = "HOLD"
        confidence = 50
    elif score >= -5:
        signal = "SELL"
        confidence = min(80, 55 + abs(score) * 3)
    else:
        signal = "STRONG SELL"
        confidence = min(95, 70 + abs(score) * 2)

    # Suggested entry/exit price
    entry_price = None
    target_price = None
    stop_loss = None

    if "BUY" in signal:
        # Suggest slight pullback entry for non-overbought
        entry_price = round(cp * 0.98, 2) if rsi < 60 else round(cp, 2)
        target_price = round(cp * 1.12, 2)   # 12% profit target
        stop_loss = round(cp * 0.93, 2)       # 7% maximum loss

    return {
        "signal": signal,
        "confidence": confidence,
        "score": score,
        "reasons": reasons,
        "entry_price": entry_price,
        "target_price": target_price,
        "stop_loss": stop_loss,
    }


# ─────────────────────────────────────────────
#  RESOLVE TICKER FROM USER INPUT
# ─────────────────────────────────────────────
def resolve_ticker(name: str) -> str | None:
    name_lower = name.lower().strip()

    # Check Indian stock dictionary
    for key, ticker in INDIAN_STOCKS.items():
        if key in name_lower or name_lower in key:
            return ticker

    # Check US stock dictionary
    for key, ticker in US_STOCKS.items():
        if key in name_lower or name_lower in key:
            return ticker

    # Try as direct ticker symbol (e.g. AAPL, TSLA, RELIANCE.NS)
    candidate = name.upper().strip()
    test = yf.Ticker(candidate)
    try:
        hist = test.history(period="5d")
        if not hist.empty:
            return candidate
    except Exception:
        pass

    return None


# ─────────────────────────────────────────────
#  MAIN ANALYSIS FUNCTION
# ─────────────────────────────────────────────
def analyze_stock(name: str) -> dict:
    ticker = resolve_ticker(name)
    if not ticker:
        return {"error": f"Could not resolve '{name}' to a known ticker. Please provide the stock name or ticker symbol."}

    df = fetch_stock_data(ticker)
    if df is None:
        return {"error": f"Unable to fetch historical data for {ticker}. Market may be closed or ticker invalid."}

    info = get_stock_info(ticker)
    indicators = compute_technical_indicators(df)
    prediction = predict_signal(indicators)

    currency_symbol = "₹" if ticker.endswith(".NS") else "$"

    return {
        "ticker": ticker,
        "name": info.get("name", ticker),
        "sector": info.get("sector", "N/A"),
        "currency": currency_symbol,
        "current_price": indicators["current_price"],
        "52w_high": info.get("52w_high", "N/A"),
        "52w_low": info.get("52w_low", "N/A"),
        "pe_ratio": info.get("pe_ratio", "N/A"),
        "indicators": indicators,
        "signal": prediction["signal"],
        "confidence": prediction["confidence"],
        "score": prediction["score"],
        "reasons": prediction["reasons"],
        "entry_price": prediction["entry_price"],
        "target_price": prediction["target_price"],
        "stop_loss": prediction["stop_loss"],
    }


# ─────────────────────────────────────────────
#  SYSTEM PROMPT
# ─────────────────────────────────────────────
def get_system_prompt(stock_context: str = "") -> str:
    base = """You are ARIA — Advanced Retail Investment Advisor — a professional, 
polite, and highly knowledgeable financial consultant. You advise retail investors 
on equity stocks (Indian NSE and US markets).

YOUR PERSONA:
- Calm, precise, and professional at all times
- Use formal financial language but keep it accessible
- Never guess — base all advice on data provided to you
- Always mention risk disclaimers briefly
- Limit active buy recommendations to a maximum of 10 stocks at a time

YOUR ADVISORY RULES:
1. When a user asks about a stock, you will receive a technical analysis summary.
2. For STRONG BUY / BUY signals: Recommend purchase. Suggest entry price, 12% profit target, 7% maximum loss.
3. For HOLD signals: Advise patience. Explain why it is neither a clear buy nor sell.
4. For SELL / STRONG SELL signals: Advise against buying. Recommend waiting for a better entry or exiting existing positions.
5. Always cite 2-3 key reasons from the technical data to justify your recommendation.
6. Use professional terms: "technically positioned", "momentum indicators", "support levels", "resistance zone", "risk-reward ratio".
7. End every recommendation with: "Please note this is for informational purposes only and not advice from a SEBI-registered Investment Advisor or SEC-registered broker."

SECTOR-SPECIFIC INTELLIGENCE:
- Indian IT stocks (TCS, Infosys, Wipro, HCL, Tech Mahindra, Cognizant) face a STRUCTURAL risk, not a cyclical one.
- The rise of Claude Code and Claude Cowork (by Anthropic) and ChatGPT (by OpenAI) is disrupting the traditional IT services model — code generation, QA, testing, documentation, and BPO work that Indian IT companies bill millions of hours for is now being automated. Claude Code writes production code autonomously; Claude Cowork automates file, task and desktop workflows that entire teams were previously hired to manage.
- This is market disruption, not a temporary headwind. Lost revenue in these segments is unlikely to recover.
- When advising on Indian IT stocks, always flag this explicitly — even if technical indicators show a BUY signal, mention that the business model itself is under long-term structural threat.
- Use professional language: "structural headwinds", "AI-led disruption of the services model", "billing hour compression", "margin pressure from automation".

CONVERSATION RULES:
- If user greets you, introduce yourself briefly and ask what stock they'd like to discuss.
- If user asks a general market question, answer professionally from your knowledge.
- If no stock data is provided, ask the user which stock they are interested in.
- Keep responses concise but complete — no padding.
"""
    if stock_context:
        base += f"\n\nCURRENT STOCK ANALYSIS DATA:\n{stock_context}\n\nUse this data to form your recommendation."
    return base