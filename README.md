<div align="center">

# 🧠 cyberagent

### Physical-bottleneck, reverse-consensus investment analysis — for *every* market

A chain of LLM agents that traces any asset down to the **physical constraint**
that caps its industry, checks whether the market has **already priced it**, and
**refuses to chase a narrative-driven top**. A-share / HK / US stocks.
Bring your own LLM key.

[![PyPI](https://img.shields.io/pypi/v/cyberagent.svg)](https://pypi.org/project/cyberagent/)
[![Python](https://img.shields.io/badge/python-3.9%2B-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![X](https://img.shields.io/badge/X-@CyberK013-black.svg)](https://x.com/CyberK013)

### 🌐 Language / 语言

**English** &nbsp;|&nbsp; [简体中文](README.zh.md)

</div>

---


## What makes it different

Most open-source "AI analyst" frameworks ask *"is this a good company?"* and
return a textbook SWOT. cyberagent asks a sharper, **falsifiable, reverse-consensus**
question, in a fixed order:

> **Physical bottleneck → uniqueness → commercialization → financial elasticity → consensus correction**
>
> *Where is the physical constraint in this asset's supply chain? Is it unique?
> Can it be monetized? Does it have non-linear financial elasticity? And has the
> market already priced it in?*

It is built on one idea from Leopold Aschenbrenner's *[Situational Awareness](https://situational-awareness.ai/)*:
**AI scaling is a massive *industrial* process**, bottlenecked by physical inputs —
power, transformers, HBM, CoWoS packaging, specific materials. cyberagent
operationalizes that thesis: it walks the supply chain down to the link
*"no amount of money can buy"*, and then applies hard anti-narrative discipline so
it doesn't mistake a headline-driven spike for an opportunity.

It does **not** predict prices. It produces facts, a falsifiable logic chain, and
monitorable physical signals — the final decision is yours.

---

## Intellectual foundations

cyberagent stands on two ideas and turns them into a reproducible, falsifiable
agent chain.

### Leopold Aschenbrenner — *Situational Awareness* (the **why**)

In *[Situational Awareness: The Decade Ahead](https://situational-awareness.ai/)*,
Aschenbrenner argues that **AI scaling is a massive *industrial* process**, not a
software one: every frontier model needs a bigger cluster, then bigger power
plants, then bigger fabs. So the binding limits are **physical** — power,
transformers, HBM, CoWoS packaging, specific materials — and effective compute
compounds at roughly an order of magnitude (OOM) per year (GPT‑2 → GPT‑4 → ~2027
AGI). The people with *situational awareness* build conviction from the trendlines
**years before consensus prices them**. cyberagent treats the market as that
physical system; the thesis is distilled in [`references/sa-canon.md`](references/sa-canon.md).

### Serenity & Crux — the bottleneck method (the **how**)

The practitioner discipline comes from supply-chain bottleneck hunters such as
**Serenity** ([@aleabitoreddit](https://x.com/aleabitoreddit)) and **Crux Capital**.
Instead of asking *"which stock goes up?"*, they **take the machine apart and look
for the chokepoint**:

> *What does the machine actually look like? Which part of its BOM is the hardest
> to replace? If one supplier stopped shipping tomorrow, how long would the whole
> chain wait?*

- **Serenity** is *narrow and deep* — find one decisive choke point and concentrate.
- **Crux** is *wide and disciplined* — map a ~6-layer stack and size each layer by execution certainty, separating proven executors from early optionality.

cyberagent distills that discipline into a fixed, falsifiable chain that any LLM
can run across any market.

> We borrow their **method** — tracing a supply chain to its physical chokepoint,
> asking *"where does the chain break"*, separating execution from optionality. We
> do **not** impersonate them, quote them, or present their positions as fact.

---

## How it works

The chain is a **telescope** — it zooms from physical reality down to the specific,
actionable name, one grounded LLM call per stage (each reads the upstream reports):

> **Positioning → Physical World → Human Development → Economics → Company Financials → Leaders & Verdict**

That telescope is how the five-step *method* above (bottleneck → uniqueness →
commercialization → elasticity → consensus) actually gets executed.

![AnalystChain — physical-bottleneck analysis pipeline](https://raw.githubusercontent.com/CyberK13/cyberagent/main/docs/assets/analystchain-en.png)

**Phase 0 — Positioning.** From the fundamentals, lock down what the company
actually sells, then pin it to a specific layer of the physical / AI supply chain
(materials → substrate → equipment → packaging → device → module → system → end
demand) and a concrete machine (e.g. a *GB300 NVL72 rack*, a *1.6T optical link*).

**Five departments**, run in sequence, each reading the upstream reports:

| Dept | `key` | What it does |
|---|---|---|
| 🪨 Physical World | `physical` | Locate the binding bottleneck on the SA ladder (power > CoWoS/HBM > raw logic); classify the asset as **owner / adjacent / derivative / none**. Non-owner ⇒ downgraded, scarcity-rent logic forbidden. |
| 🌍 Human Development | `human_dev` | Place the demand on the AGI / OOM arc — early (runway left) or mature/peaked? |
| 💱 Economics | `economics` | ore-seller vs processor; **decompose the price move into earnings-growth vs multiple-expansion**; detect valuation-framework switches; is it *already priced* (Gray Rhino vs loud consensus)? |
| 📈 Company Financials | `financials` | Fundamentals + financial elasticity (linear vs non-linear); attribute earnings anomalies *before* flagging them. |
| 🎯 Leaders & Verdict | `leaders` | Two-axis verdict — **bottleneck identity (a) vs pricing position (b)** — steelman + Munger inversion, monitorable exit signals, final decision. |

### The discipline (why it won't chase a top)

This is the part textbook frameworks skip:

- **Real-time grounding** — with Gemini it *searches why a price moved* (the catalyst, who said what), instead of trusting model memory.
- **Price-action guardrail** — the data layer flags parabolic / near-high moves; a stock that doubled in days on one headline is an **AVOID / observe** form, never a buy.
- **Evidence ladder** — every key claim is tagged `Confirmed / Inferred / Weak`; a load-bearing `Inferred` claim caps the confidence.
- **Two independent axes** — *"is it a bottleneck"* (classification) and *"should you buy it here"* (pricing) are never conflated. A non-bottleneck can be a fine trade at a price; a real bottleneck at a top can be a bad one.
- **Honest "too late"** — parabolic move + extreme valuation + loud consensus ⇒ the label is *"too late / top"*, not an opportunity.

> Educational and research use only. Output quality varies with the model, data,
> and many non-deterministic factors. **This is not financial, investment, or
> trading advice.**

---

## Quickstart — 30 seconds

```bash
python3 -m venv .venv && source .venv/bin/activate   # isolated env (Win: .venv\Scripts\activate)
python3 -m pip install 'cyberagent[all]'             # everything: market data + all LLM providers + web UI
cyberagent                                            # launches the interactive wizard
```

No need to pick a provider at install time. `cyberagent` then walks you through it
step by step — **① language → ② model → ③ paste your API key → ④ enter a symbol**
(`NVDA` / `600519` / `0700`) — and prints the report. That's it. (Prefer the
browser? `cyberagent serve` for the local web UI.)

> Use `python3 -m pip` (not bare `pip`) and the venv above — on macOS a plain
> `pip` is often missing (`command not found`) and recent Python blocks installs
> into the system environment. The venv sidesteps both.

Want a leaner install? You don't need every provider — install just one with its
extra (`gemini` / `deepseek` / `openai` / `claude`), e.g.
`python3 -m pip install 'cyberagent[stocks,web,deepseek]'`. The wizard then offers
that provider; for non-interactive use pass `--llm <provider>` (see below).

## Use it from Python

```python
import asyncio
from cyberagent import AnalystChain

chain = AnalystChain(llm="gemini", api_key="...", lang="en")
report = asyncio.run(chain.analyze("NVDA"))

print(report.final_decision)                   # ACCUMULATE / HOLD / REDUCE / AVOID
print(report.departments["leaders"].markdown)
```

(Inside Jupyter or an async app, `await chain.analyze("NVDA")` directly. Pick the
report language with `lang="en"` / `"zh"` — the whole report is generated in it.
Full API: [`docs/quickstart.md`](docs/quickstart.md).)

<details>
<summary><b>More — other LLM providers · custom adapter · install options · CLI flags</b></summary>

<br>

**Providers.** Gemini is the default and the only one with real-time grounding;
any of these works:

```python
from cyberagent import AnalystChain, LLMAdapter, MockLLM

AnalystChain(llm="openai",   api_key="sk-...")
AnalystChain(llm="claude",   api_key="...")
AnalystChain(llm="deepseek", api_key="...")
AnalystChain(llm=MockLLM())                    # offline, no key — try the flow

class MyLLM(LLMAdapter):
    async def complete(self, system: str, user: str) -> str: ...
AnalystChain(llm=MyLLM())
```

Keys come from the argument, the environment, or a local `.env`
(all variables: [`.env.example`](.env.example)). Get one:
[Gemini (free)](https://aistudio.google.com/app/apikey) ·
[OpenAI](https://platform.openai.com/api-keys) ·
[Anthropic](https://console.anthropic.com/) ·
[DeepSeek](https://platform.deepseek.com/).

**Install options.** Bare `pip install cyberagent` is the zero-dependency core.
Extras: `stocks` (yfinance) · `gemini` / `openai` / `claude` / `deepseek`
(providers) · `web` (local UI) · `all` (everything). DeepSeek is OpenAI-API
compatible, so the `deepseek` extra is an alias for `openai` — install with
`python3 -m pip install 'cyberagent[deepseek]'`, set `DEEPSEEK_API_KEY`, run
`--llm deepseek`.

**CLI.**

```bash
cyberagent analyze NVDA --llm gemini --lang en
cyberagent analyze AAPL --depts physical,economics,leaders   # subset, faster
cyberagent serve                              # local web UI at http://127.0.0.1:8000
```

The CLI and web UI auto-load `.env` and show a model picker (✓ next to every key
found), live per-department progress, and the rendered report.

</details>

---


## Use as a Claude Skill — no install

The whole methodology is also packaged as a self-contained **Claude Skill** in
[`SKILL.md`](SKILL.md) — it runs the same physical-bottleneck chain in pure-prompt
form, no Python required. To install it in **Claude Code**:

```bash
mkdir -p ~/.claude/skills/physical-bottleneck-analyst
curl -fsSL https://raw.githubusercontent.com/CyberK13/cyberagent/main/SKILL.md \
  -o ~/.claude/skills/physical-bottleneck-analyst/SKILL.md
```

Then just ask: *"analyze NVDA"* — Claude picks the skill up automatically. (Any
other agent that loads skills works the same way: give it `SKILL.md`.) The Python
package adds live data, real-time grounding, and the CLI / web UI on top.

## Methodology & prompts — fully open

There is no paywall. *How* to hunt a physical bottleneck is framework knowledge,
not alpha. The complete system prompts live in
[`src/cyberagent/prompts/departments.py`](src/cyberagent/prompts/departments.py),
and the *Situational Awareness* anchor (the physical-bottleneck ladder + the OOM
development arc) is distilled in [`references/sa-canon.md`](references/sa-canon.md).

---

## Roadmap

- [ ] LangChain / LangGraph tool wrapper
- [ ] MCP server (Claude / Cursor)
- [ ] EDGAR (US filings) + Tushare (A-share) adapters
- [ ] Segment-level chains for conglomerates
- [ ] Structured per-department gate verdicts (machine-enforced "stop")

---

## Disclaimer

`final_decision`, `confidence`, and the department reports are **AI-generated
educational outputs**, not financial advice. LLMs make mistakes; markets are
unpredictable. Do your own research. The authors and contributors are not liable
for any decision made based on this software. See [`docs/disclaimer.md`](docs/disclaimer.md).

## License

MIT. See [LICENSE](LICENSE).

## Contact

Questions, ideas, or feedback? Reach out on X: [**@CyberK013**](https://x.com/CyberK013).
