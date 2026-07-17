# Changelog

All notable changes to `cyberagent` are recorded here.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Machine-readable verdict line: the closing (leaders) department must now end
  its report with `FINAL DECISION: <label> | CONFIDENCE: <0-100>/100`, and the
  verdict parser prefers that line — verified end-to-end with DeepSeek.
- SA-arc reality check in prompts: the Situational Awareness ladder/OOM
  timeline is now framed as a mid-2024 working hypothesis; departments must
  anchor "today" to the data fetch date and check whether the arc has tracked,
  instead of treating unrealized forecasts as facts.
- Injected fundamentals now note that growth/margin/ROE figures are decimal
  fractions (0.25 = 25%), so models don't misread ratio units.

### Changed
- Claude default model: `claude-sonnet-4-5` → `claude-sonnet-5` (current
  Sonnet tier). The adapter no longer sends `temperature` unless explicitly
  set (Sonnet 5+ rejects non-default sampling params) and `max_tokens` is
  raised 4096 → 8192 so long zh reports aren't truncated mid-verdict.
- Price statements in prompts now require the data block's currency instead of
  a hardcoded `$` (A-share/HK prices are not USD).

### Fixed
- Verdict parsing could report ACCUMULATE for an AVOID report when the model
  echoed the output template's "ACCUMULATE / HOLD / REDUCE / AVOID" menu line;
  the parser now skips enumeration lines and reads the real verdict.
- Confidence parsing now handles the real-world heading shape
  (`### 置信度（0-100）+ 扣分依据` with the number on the next line) and the
  new `NN/100` machine line; previously it silently returned 0.

## [0.1.4] - 2026-07-04

### Added
- Live data injection for ALL providers: the stock adapter now fetches recent
  news headlines and analyst rating actions (with dates and price targets) at
  runtime and injects them into every department's context — so non-grounded
  models (DeepSeek / OpenAI / Claude) analyze today's catalysts instead of
  falling back on stale training memory.
- A-share live news via akshare (Eastmoney; free, no key or signup): yfinance
  has no CN-market news, so A-share symbols now automatically fall back to
  akshare for recent headlines. Bundled into the `stocks` / `all` extras.
- Capability-aware prompts: adapters expose `supports_search`; models without
  live search get an explicit no-search notice — current facts may only come
  from the injected live blocks, and memory-based claims must be tagged as
  possibly stale and downgraded to [Needs verification].

### Fixed
- A failed live-data fetch is no longer silent: the chain now injects a loud
  "LIVE DATA UNAVAILABLE" notice telling the model to state its knowledge
  cutoff and cap confidence, instead of letting it run blind on memory.

## [0.1.3] - 2026-06-22

### Added
- Interactive CLI wizard: `cyberagent` now walks through it step by step —
  language → model → API key → symbol. Missing keys are prompted for (hidden
  input) and can be saved to `.env` for next time.

### Changed
- README: install no longer splits by provider — `pip install 'cyberagent[all]'`
  bundles every provider, and the runtime wizard handles model + key. Lean
  single-provider installs are still documented.

## [0.1.2] - 2026-06-22

### Added
- `deepseek` install extra (alias for `openai`, since DeepSeek is OpenAI-API
  compatible): `pip install 'cyberagent[deepseek]'` now just works.
- Python 3.13 classifier.

### Changed
- README: safer install path — create a venv and use `python3 -m pip` (bare
  `pip` is often missing on macOS, and recent Python blocks system-env installs).
  DeepSeek now documented via its own `deepseek` extra.

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
