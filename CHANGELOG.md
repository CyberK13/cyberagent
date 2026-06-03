# Changelog

All notable changes to `cyberagent` are recorded here.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Planned for 0.1.0
- `AnalystChain` main entry: `await chain.analyze(symbol)` returns `AnalystReport`
- `AssetClassifier`: unified routing for A-share / HK / US / crypto / EVM contract
- Data adapters: Tushare (CN) / yfinance + EDGAR (US) / yfinance (HK) / CoinGecko + DefiLlama (crypto)
- 5 departments: industry / financial / risk / valuation / strategy
- LLM adapter: OpenAI / Gemini / Claude / DeepSeek + custom
- LangChain Tool wrapper (`cyberagent.langchain.analyze_asset_tool`)
- MCP server (`python -m cyberagent.mcp_server`)
- CLI (`cyberagent analyze NVDA --llm gemini`)
- Pydantic models for structured output
- 5-department system prompts — fully open-source (no paywall)

## [0.0.1] - 2026-05-28

### Added
- Placeholder release reserving the PyPI name and GitHub repo.
- LICENSE (MIT).
- README with product vision + roadmap.
- tea.yaml constitution scaffold.
- Empty `src/cyberagent/` package structure.
