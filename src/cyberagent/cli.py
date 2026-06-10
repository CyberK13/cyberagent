"""cyberagent CLI — a terminal-style entry to the physical-bottleneck analyst chain.

Interactive (pick language + model, then enter a symbol):

    cyberagent

Non-interactive:

    cyberagent analyze MRVL --llm gemini --lang zh
    cyberagent analyze BTC  --depts physical,economics,leaders
"""

from __future__ import annotations

import argparse
import asyncio
import os
import sys

from .chain import AnalystChain
from .llm_adapter import PROVIDER_CATALOG
from .models import AnalystReport
from .prompts import DEPT_ORDER

BANNER = r"""
   _      _                                 _
  | |    | |                               | |
  ___ _   _| |__   ___ _ __ __ _  __ _  ___ _ __ | |_
 / __| | | | '_ \ / _ \ '__/ _` |/ _` |/ _ \ '_ \| __|
| (__| |_| | |_) |  __/ | | (_| | (_| |  __/ | | | |_
 \___|\__, |_.__/ \___|_|  \__,_|\__, |\___|_| |_|\__|
       __/ |                      __/ |
      |___/                      |___/
  physical-bottleneck reverse-consensus analyst chain
"""


def _load_dotenv(path: str = ".env") -> bool:
    """Lightweight .env loader (no dependency): load KEY=VALUE lines from ./.env
    into the environment without overwriting existing vars. Lets `cyberagent`
    pick up local keys automatically."""
    if not os.path.exists(path):
        return False
    try:
        with open(path, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue
                key, _, val = line.partition("=")
                key, val = key.strip(), val.strip().strip('"').strip("'")
                if key and key not in os.environ:
                    os.environ[key] = val
    except Exception:
        return False
    return True


def _has_key(env_key: str) -> bool:
    return bool(os.getenv(env_key))


def _choose_model(default: str = "gemini") -> str:
    """Print the model menu (with ✓/✗ for matched API keys) and return a provider."""
    print("选择模型 / Select model  (✓ = API key found in env, auto-matched):\n")
    for i, p in enumerate(PROVIDER_CATALOG, 1):
        mark = "✓" if _has_key(p["env_key"]) else "✗ missing"
        star = "  (default)" if p["provider"] == default else ""
        print(f"  {i}) {p['label']:<42} [{p['env_key']}: {mark}]{star}")
    print("  m) mock  (offline, no key — for trying the flow)\n")
    try:
        raw = input(f"> 选择 [1-{len(PROVIDER_CATALOG)} / m, 回车默认 {default}]: ").strip().lower()
    except (EOFError, KeyboardInterrupt):
        return default
    if not raw:
        return default
    if raw == "m":
        return "mock"
    if raw.isdigit() and 1 <= int(raw) <= len(PROVIDER_CATALOG):
        return PROVIDER_CATALOG[int(raw) - 1]["provider"]
    # allow typing a provider name directly
    return raw


def _choose_lang(default: str = "en") -> str:
    try:
        raw = input(f"> 语言 / Language [zh/en, 回车默认 {default}]: ").strip().lower()
    except (EOFError, KeyboardInterrupt):
        return default
    return raw if raw in ("zh", "en") else default


def _progress(stage: str, label: str, status: str) -> None:
    if status == "start":
        print(f"  … {label}", end="", flush=True)
    else:
        print(f"\r  ✓ {label}            ")


def _render(report: AnalystReport, lang: str) -> str:
    out = []
    out.append("=" * 70)
    out.append(f"  {report.company_name}  ({report.asset.code})   market={report.market}")
    out.append(f"  decision: {report.final_decision}   confidence: {report.confidence}   {report.elapsed_seconds}s")
    if report.headline:
        out.append(f"  » {report.headline}")
    out.append("=" * 70)
    if report.positioning:
        out.append("\n## Phase 0 — 资产定位 / Positioning\n")
        out.append(report.positioning.strip())
    for key, dept in report.departments.items():
        out.append(f"\n{'-' * 70}\n## {dept.display_name}  [{key}]\n")
        out.append(dept.markdown.strip())
    return "\n".join(out)


async def _run(symbol: str, *, llm, lang: str, departments=None, grounding: bool) -> int:
    if llm == "gemini" and not grounding:
        from .llm_adapter import GeminiAdapter
        llm = GeminiAdapter(grounding=False)
    chain = AnalystChain(llm=llm, lang=lang, departments=departments)
    print(f"\n分析 {symbol} … (model={getattr(chain.llm, 'name', llm)}, lang={lang})\n")
    report = await chain.analyze(symbol, on_event=_progress)
    if not report.success:
        print(f"\n✗ {report.error}", file=sys.stderr)
        return 1
    print("\n" + _render(report, lang))
    return 0


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(prog="cyberagent", description="Physical-bottleneck analyst chain.")
    sub = parser.add_subparsers(dest="cmd")

    a = sub.add_parser("analyze", help="analyze a symbol")
    a.add_argument("symbol")
    a.add_argument("--llm", default="gemini", help="provider: gemini/openai/claude/deepseek/mock")
    a.add_argument("--lang", default="en", choices=["zh", "en"])
    a.add_argument("--depts", default="", help="comma list, e.g. physical,economics,leaders")
    a.add_argument("--no-grounding", action="store_true", help="disable Gemini real-time search")

    s = sub.add_parser("serve", help="start the local web page")
    s.add_argument("--host", default="127.0.0.1")
    s.add_argument("--port", type=int, default=8000)

    args = parser.parse_args(argv)
    _load_dotenv()  # pick up local .env keys automatically

    if args.cmd == "serve":
        from .web import serve
        serve(host=args.host, port=args.port)
        return 0

    if args.cmd == "analyze":
        depts = [d.strip() for d in args.depts.split(",") if d.strip()] or None
        return asyncio.run(_run(args.symbol, llm=args.llm, lang=args.lang,
                                departments=depts, grounding=not args.no_grounding))

    # interactive "homepage"
    print(BANNER)
    lang = _choose_lang()
    provider = _choose_model()
    if provider != "mock" and provider in {p["provider"] for p in PROVIDER_CATALOG}:
        env_key = next(p["env_key"] for p in PROVIDER_CATALOG if p["provider"] == provider)
        if not _has_key(env_key):
            print(f"\n⚠️  没找到 {env_key}。请在 .env 填入，或选其它模型 / mock。", file=sys.stderr)
    try:
        symbol = input("\n> 输入代码 / Enter symbol (NVDA / 600519 / 0700): ").strip()
    except (EOFError, KeyboardInterrupt):
        return 0
    if not symbol:
        print("没有输入代码。", file=sys.stderr)
        return 1
    return asyncio.run(_run(symbol, llm=provider, lang=lang, departments=None, grounding=True))


if __name__ == "__main__":
    raise SystemExit(main())
