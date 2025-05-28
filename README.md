# 📊 TradeInsightsAssistant

> **Your chat-based assistant to explore and interpret Open Interest (OI) data**

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


## 📦 Getting Started

*Coming Soon* — Instructions for running the assistant will be provided in the upcoming release.


# The idea is that we use prism mcp to get the details
# The config and api will be saved in another file which will be private for now and we don't want to share that information


# Install dependencies

```commandline
pip install git+ssh://git@github.com/fintools-ai/mcp-openinterest-server.git

pip install git+ssh://git@github.com/fintools-ai/llm-agent-prompts.git

```