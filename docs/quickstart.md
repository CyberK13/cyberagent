# Quickstart

Status: 0.0.1 placeholder. Full docs land at 0.1.0.

## Install

```bash
pip install cyberagent
```

## 60-second example

```python
from cyberagent import AnalystChain

chain = AnalystChain(llm='gemini', api_key='YOUR_GEMINI_KEY')

report = await chain.analyze('NVDA')

print(report.final_decision)                      # ACCUMULATE / HOLD / REDUCE / AVOID
print(report.confidence)                          # 0.0 - 1.0
print(report.departments['industry'].markdown)    # 行业部 report
print(report.departments['financial'].markdown)
print(report.departments['risk'].markdown)
print(report.departments['valuation'].markdown)
print(report.departments['strategy'].markdown)
```

## Supported markets

| Input | Example | Adapter |
|------|---------|----|
| A-share (Shenzhen / Shanghai / 北交所) | `'600519'`, `'000001'` | Tushare |
| HK stock | `'0700'`, `'9988'` | yfinance |
| US stock | `'NVDA'`, `'AAPL'` | yfinance + EDGAR |
| Crypto token | `'BTC'`, `'ETH'`, `'SOL'` | CoinGecko + DefiLlama |
| EVM contract | `'0x6B17474E89094C44Da98b954EedeAC495271d0F'` | Etherscan + on-chain |

## Bring your own LLM

```python
from cyberagent import LLMAdapter

chain = AnalystChain(llm=LLMAdapter.openai(api_key='sk-...'))
chain = AnalystChain(llm=LLMAdapter.gemini(api_key='...'))
chain = AnalystChain(llm=LLMAdapter.claude(api_key='...'))
chain = AnalystChain(llm=LLMAdapter.deepseek(api_key='...'))
```

## Prompts

All 5-department system prompts ship in `src/cyberagent/prompts/` and are fully
open-source — no API key, no paywall. The package works end-to-end out of the box.
