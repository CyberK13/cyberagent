"""cyberagent — TradingAgents for every market.

A 5-department LLM analyst chain unified across stocks (A-share / HK / US)
and crypto (token / contract address). Bring your own LLM key.

Status: 0.0.1 placeholder. Real release coming. See README + CHANGELOG for roadmap.

Public API (planned, exposed from 0.1.0):
    AnalystChain        — main entry, await chain.analyze(symbol)
    AssetClassifier     — unified routing for A-share / HK / US / crypto / EVM
    LLMAdapter          — OpenAI / Gemini / Claude / DeepSeek + custom
    AnalystReport       — Pydantic structured output
    DeptReport
"""

__version__ = "0.0.1"
__all__ = ["__version__"]
