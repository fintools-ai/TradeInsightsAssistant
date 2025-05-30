# 📊 TradeInsightsAssistant

> **Professional-grade options analysis through conversational AI**

---

## 🚀 **See the Power in Action**

TradeInsightsAssistant transforms complex options data into institutional-quality trading intelligence. Experience what's possible:

### 🎯 **Real Market Analysis Results**

**Recent SPY Analysis (May 29, 2025):**
```
"The market is positioned for significant downward pressure leading into June 20th week. 
Put/Call ratio of 3.31 on June 13th expiration with massive put accumulation suggests 
institutional positioning for SPY decline to $570-$575 range."

📊 Confidence: 75% probability based on historical patterns
🎯 Target: $570-$575 (5-7% decline)
⏰ Timeline: June 13-20th window
```

### 💡 **Cross-Asset Intelligence**

**Coordinated Analysis Across Multiple Assets:**
- **SPY**: P/C Ratio 3.31 → Bearish bias, $570 target
- **VXX**: P/C Ratio 0.63 → Volatility spike expected, $75-$85 target  
- **TLT**: P/C Ratio 0.67 → Flight-to-safety, $90-$94 target

### 📈 **Actionable Trade Setups**

**Example Professional Output:**
```
TRADE: SPY Put Spread
• Buy: $575 Puts, June 20th | Sell: $550 Puts, June 20th
• Entry: SPY above $582 | Target: $565 (70% max profit)
• Risk/Reward: 1:1.22 | Success Probability: 75%
• Position Size: 3-5% of portfolio

TRADE: VXX Call Spread  
• Buy: $60 Calls, June 20th | Sell: $80 Calls, June 20th
• Entry: VXX below $55 | Target: $72 (60% max profit)
• Risk/Reward: 1:1.35 | Success Probability: 70%
```

---

## 🎯 Overview

**TradeInsightsAssistant** is an interactive AI-powered chat interface that helps you analyze **daily options Open Interest (OI)** data to uncover potential market insights. By asking natural language questions, you can understand where large options positions are building, how OI is changing over time, and what these trends may indicate about future price behavior.

---

## 💡 What It Does

* 🧠 **Conversational Understanding of OI Data**

  * Ask about a ticker like “What’s the key OI level for SPY today?”
  * Get simple, human-friendly summaries of the latest OI distribution

* 📈 **OI Trend Tracking**

  * See how open interest is **changing over time** across strikes and expirations
  * Understand whether traders are **building new positions** or **closing old ones**

* ⚖️ **Call/Put Concentration Detection**

  * Identify where large **call walls** or **put floors** exist based on open interest
  * Understand which strikes are acting as potential **support or resistance**

* 📅 **Expiration-Focused Insights**

  * Ask: “What are the top OI strikes for this Friday’s SPY expiration?”
  * Detect areas of **maximum positioning risk or reward**

---

## 💬 Example Interactions

```txt
You: What does the SPY OI look like for this week?

Assistant: The highest call OI is at 510 and 515, while the largest put OI is at 500. There’s growing OI at 505 on both sides, suggesting it could act as a magnet level.

---

You: How did AAPL OI shift from yesterday?

Assistant: There’s a 20% increase in call OI at the 190 strike for next Friday’s expiration. Put OI is unchanged, suggesting a slight bullish skew in positioning.

---

You: Are there any unusual OI builds in TSLA?

Assistant: Yes, TSLA’s 300 strike for next week saw a 40% jump in call OI today — the highest increase across all strikes. Worth watching for directional follow-through.
```

---

## 🏆 **Real Analysis Examples**

### **Comprehensive Market Direction Analysis**
**[📁 View Complete SPY Analysis](storage/output/SPY/20250529/SPY_172302_analysis.md)**
- **152 lines** of detailed institutional positioning analysis
- **Specific price targets** with timeline expectations
- **Multiple trade recommendations** with risk/reward ratios
- **Cross-expiration analysis** across June 6th, 13th, and 20th

### **Professional Hedging Strategies**  
**[📁 View Complete HOOD Analysis](storage/output/HOOD/20250529/HOOD_151123_analysis.md)**
- **360+ lines** comprehensive hedging masterclass
- **Portfolio protection scenarios** for different account sizes
- **Specific hedge structures** with P&L projections
- **Risk management frameworks** with clear guidelines

### **Volatility Intelligence**
**[📁 View Complete VXX Analysis](storage/output/VXX/20250529/VXX_172616_analysis.md)**
- **Advanced volatility positioning** analysis
- **Gamma exposure insights** and acceleration zones
- **Cross-correlation strategies** with equity markets
- **Timeline-based volatility expectations**

### **Multi-Asset Coordination**
**[📁 View Complete Cross-Asset Strategy](storage/output/TLT/20250529/TLT_173818_analysis.md)**
- **584 lines** of coordinated SPY/VXX/TLT analysis
- **Institutional flow analysis** across asset classes
- **Expected move sequences** with probability assessments
- **Portfolio-level allocation strategies**

---

## 🔍 Use Cases

* Spot **high OI strikes** where price might stall or accelerate
* Track **daily changes** in OI to identify positioning shifts
* Use chat to analyze **OI clusters** across expirations
* Understand if **bullish or bearish** bets are increasing
* Plan **risk/reward levels** around where the market is most positioned

---

## 🛠️ Simple, Chat-First Workflow

1. Install the agent 

2. Ask natural language questions like:

   * "Where is the biggest OI on QQQ this week?"
   * "What’s the call/put ratio for SPY 0DTE today?"
   * "Any unusual open interest activity on NVDA?"

3. Receive clear insights, trend summaries, and level-based observations to inform your trades

---

## 💎 **Professional Features**

### **🔬 Data Depth & Intelligence**
- **Real-time Open Interest data** across 20+ expiration dates
- **Put/Call ratio analysis** with historical context
- **Institutional positioning detection** (million-dollar positions)
- **Gamma exposure mapping** for acceleration zones
- **Cross-asset correlation analysis** (SPY, VXX, TLT, bonds)

### **📊 Analysis Quality**
- **Statistical confidence levels** based on historical patterns
- **Kelly Criterion position sizing** for optimal allocation
- **Risk-adjusted return calculations** with success probabilities
- **Timeline-based expectations** tied to options expiration cycles
- **Professional trade structures** (spreads, hedges, directional plays)

### **🎯 Output Excellence**
- **Detailed written reports** automatically saved to file system
- **Specific price targets** with reasoning and data support
- **Risk management guidelines** with clear entry/exit rules
- **Portfolio allocation strategies** for different account sizes
- **Educational content** explaining complex options concepts

---


## 📦 Getting Started

### Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
pip install git+ssh://git@github.com/fintools-ai/mcp-openinterest-server.git
pip install git+ssh://git@github.com/fintools-ai/llm-agent-prompts.git
```

2. Run the application:
```bash
python main.py
```

### Adding MCP Servers

The application uses a JSON-based registry to manage MCP servers. To add new MCP servers:

1. Edit `mcp_servers.json`:
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

2. Restart the application - new servers will be automatically loaded and their tools made available to the AI agent.

**Server Configuration:**
- `name`: Unique identifier for the server
- `command`: Command to start the MCP server
- `args`: Command line arguments for the server