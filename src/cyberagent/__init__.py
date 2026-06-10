"""cyberagent — TradingAgents for every market.

A 5-department LLM analyst chain unified across stocks (A-share / HK / US) and
crypto (token / contract address). The analytical soul is a physical-bottleneck
reverse-consensus 5-step chain. Bring your own LLM key.

    from cyberagent import AnalystChain

    chain = AnalystChain(llm="gemini", api_key="...", lang="zh")
    report = await chain.analyze("NVDA")
    print(report.final_decision, report.confidence)
    print(report.departments["industry"].markdown)

Public API:
    AnalystChain     — main entry, await chain.analyze(symbol)
    AssetClassifier  — unified routing for A-share / HK / US / crypto / EVM
    classify         — functional form of the classifier
    LLMAdapter       — OpenAI / Gemini / Claude / DeepSeek + custom
    MockLLM          — offline adapter for tests/examples
    AnalystReport / DeptReport / AssetInfo — Pydantic structured output
"""

from .chain import AnalystChain
from .classifier import AssetClassifier, classify
from .llm_adapter import LLMAdapter, MockLLM
from .models import AnalystReport, AssetInfo, DeptReport

__version__ = "0.1.1"

__all__ = [
    "__version__",
    "AnalystChain",
    "AssetClassifier",
    "classify",
    "LLMAdapter",
    "MockLLM",
    "AnalystReport",
    "DeptReport",
    "AssetInfo",
]
