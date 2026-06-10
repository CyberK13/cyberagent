# Quickstart

The physical-bottleneck analyst chain. See the [README](../README.md) for the methodology.

## Install & run

```bash
pip install 'cyberagent[stocks,gemini,web]'
echo 'GOOGLE_API_KEY=your_key' > .env     # free key: aistudio.google.com/app/apikey
cyberagent                                # interactive · or: cyberagent serve
```

(Bare `pip install cyberagent` is the zero-dependency core.)

## 60-second example

```python
import asyncio

from cyberagent import AnalystChain

chain = AnalystChain(llm="gemini", api_key="YOUR_GEMINI_KEY", lang="en")

report = asyncio.run(chain.analyze("NVDA"))   # in Jupyter / async code: await chain.analyze("NVDA")

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
