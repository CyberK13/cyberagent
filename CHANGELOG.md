# Changelog

All notable changes to `cyberagent` are recorded here.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added (working, pre-tag)
- `AnalystChain.analyze(symbol)` → `AnalystReport`; Phase 0 positioning + 5-department
  physical-bottleneck chain: `physical` · `human_dev` · `economics` · `financials` · `leaders`.
- `AssetClassifier`: unified routing for A-share / HK / US / crypto / EVM contract.
- Data adapters: yfinance (CN/HK/US, with price-action + analyst-consensus signals)
  and CoinGecko + DefiLlama (crypto).
- LLM adapter: OpenAI / Gemini / Claude / DeepSeek + custom + offline `MockLLM`;
  Gemini real-time grounding on by default.
- Open-source system prompts (the physical-bottleneck methodology + anti-narrative
  discipline) + the *Situational Awareness* canon in `references/sa-canon.md`.
- CLI (`cyberagent analyze …`) and a local web page (`cyberagent serve`) with
  language + model selection.

### Planned
- LangChain tool wrapper; MCP server; EDGAR / Tushare / Etherscan adapters;
  segment-level chains; structured per-department gate verdicts.

## [0.0.1] - 2026-05-28

### Added
- Placeholder release reserving the PyPI name and GitHub repo.
- LICENSE (MIT).
- README with product vision + roadmap.
- tea.yaml constitution scaffold.
- Empty `src/cyberagent/` package structure.
