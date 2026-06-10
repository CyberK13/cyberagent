# Changelog

All notable changes to `cyberagent` are recorded here.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.1] - 2026-06-10

### Changed
- `financials` prompt: the non-linear upside dimension is now labeled plainly
  "Fat Tail / Dragon King" (internal framework prefix removed).
- Housekeeping: tidied `.gitignore` comments; docs present the framework as
  stock analysis (A-share / HK / US); README diagrams replaced with designed
  pipeline posters.

## [0.1.0] - 2026-06-10

First real release.

### Added
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

### Changed
- README / quickstart examples are now copy-paste runnable (`asyncio.run(...)`);
  install docs recommend `cyberagent[stocks,gemini,web]`.
- `.env.example` trimmed to the variables the code actually reads (4 LLM
  providers); future adapter keys moved to a clearly-marked roadmap block.

### Removed
- `tea.yaml` placeholder constitution (tea Protocol registration is deferred).

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
