# Quickstart

The physical-bottleneck analyst chain. See the [README](../README.md) for the methodology.

## Install

```bash
pip install cyberagent
pip install 'cyberagent[stocks]'   # yfinance, for stock data
pip install 'cyberagent[gemini]'   # Gemini + real-time grounding
```

## 60-second example

```python
from cyberagent import AnalystChain

chain = AnalystChain(llm="gemini", api_key="YOUR_GEMINI_KEY", lang="en")

report = await chain.analyze("NVDA")

print(report.final_decision)                       # ACCUMULATE / HOLD / REDUCE / AVOID
print(report.confidence)                           # 0.0 - 1.0
print(report.positioning)                          # Phase 0 — core business + physical position
print(report.departments["physical"].markdown)     # bottleneck identity
print(report.departments["economics"].markdown)    # priced-in? / move decomposition
print(report.departments["leaders"].markdown)      # two-axis verdict
```

Departments (the order they run in): `physical` · `human_dev` · `economics` · `financials` · `leaders`.

## Supported markets

| Input | Example | Data source |
|------|---------|----|
| A-share (Shanghai / Shenzhen / 北交所) | `"600519"`, `"000001"` | yfinance |
| HK stock | `"0700"`, `"9988"` | yfinance |
| US stock | `"NVDA"`, `"AAPL"` | yfinance |
| Crypto token | `"BTC"`, `"ETH"`, `"SOL"` | CoinGecko + DefiLlama |
| EVM contract | `"0x6B17474E89094C44Da98b954EedeAC495271d0F"` | on-chain (LLM reasoning) |

## Bring your own LLM

```python
from cyberagent import AnalystChain, LLMAdapter, MockLLM

AnalystChain(llm="openai",   api_key="sk-...")
AnalystChain(llm="gemini",   api_key="...")
AnalystChain(llm="claude",   api_key="...")
AnalystChain(llm="deepseek", api_key="...")
AnalystChain(llm=MockLLM())            # offline, no key — try the flow
```

## CLI & web

```bash
cyberagent                       # interactive: pick language + model, then a symbol
cyberagent analyze NVDA --llm gemini
cyberagent serve                 # local web page at http://127.0.0.1:8000
```

## Prompts

All department system prompts ship in `src/cyberagent/prompts/departments.py` and
are fully open-source — no API key, no paywall.
