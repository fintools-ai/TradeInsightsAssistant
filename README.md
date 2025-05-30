# 📊 TradeInsightsAssistant

> **Conversational AI for Options Intelligence**

![Banner](assets/banner.png)

---

## 🚀 What is TradeInsightsAssistant?

TradeInsightsAssistant is your options research analyst — powered by natural language. It transforms open interest (OI), volatility positioning, and cross-asset flows into precise trading insights using a powerful chat interface backed by LLMs.

Ask it questions like:

* "Where are traders piling on SPY puts this week?"
* "What’s the risk/reward on a June QQQ put spread?"
* "Are there unusual builds in NVDA for Friday’s expiration?"


---

## 🧠 Key Capabilities

### 💬 Conversational Intelligence

* Ask questions in plain English
* Receive clean, structured responses
* Get Markdown-formatted trade setups

### 📈 Options Market Analysis

* Open Interest clustering (per strike and expiry)
* Call/Put ratio skew detection
* Max Pain and magnet zones
* Position buildup and liquidation tracking


### ⚒️ Professional Trade Outputs

* Spreads, hedges, directional trades
* Entry, stop-loss, profit target rules
* Kelly Criterion sizing and confidence score

---

## 🛠️ How It Works

1. Launch the CLI: `python main.py`
2. Choose your LLM backend (Bedrock or Claude API)
3. Start chatting:

```txt
📊 You: What are key OI levels on TSLA this week?
🤖 Agent: The 280 and 300 put strikes show growing OI with strong skew. Gamma risk is concentrated near 290.
```

4. Want to save the response? Just say yes — it writes to Markdown with a full metadata trail.

---

## 🔍 Use Cases

* 0DTE and weekly trade planning
* Institutional flow tracking
* Quantified trade generation
* Hedge scenario simulation
* Risk-layered market analysis

---

## ⚡ Example Prompts

```bash
"Analyze SPY open interest for the next 5 days"
"What’s the options flow telling us about AAPL?"
"Show me support and resistance levels for TSLA"
"Give me a put hedge strategy for HOOD next month"
```

---


### Run the CLI:

```bash
python main.py
```

You’ll be guided to choose your LLM provider (AWS Bedrock or Claude API). From there, start chatting.

---

## 📂 MCP Server Configuration

Servers are defined in `mcp_servers.json`:

```json
{
  "servers": [
    {
      "name": "openinterest",
      "command": "mcp-openinterest-server",
      "args": []
    },
    {
      "name": "news",
      "command": "mcp-news-server",
      "args": ["--api-key", "your-key"]
    }
  ]
}
```

Add/remove servers as needed — the CLI dynamically loads them.

---

## 🧩 Architecture

* ✅ CLI-first UX built on `rich`
* ✅ Orchestrator handles multi-turn LLM conversations
* ✅ Dynamic tool invocation from MCP registry
* ✅ Markdown + JSON output for traceability

---

## 📜 License

[MIT License](LICENSE)

---
