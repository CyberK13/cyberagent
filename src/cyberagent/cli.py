"""cyberagent CLI — a terminal-style entry to the physical-bottleneck analyst chain.

Interactive wizard (step by step: language → model → API key → symbol):

    cyberagent

Non-interactive:

    cyberagent analyze MRVL --llm gemini --lang zh
    cyberagent analyze BTC  --depts physical,economics,leaders
"""

from __future__ import annotations

import argparse
import asyncio
import getpass
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


# Localized wizard strings (zh/en). Step 1 (language) is bilingual since the
# language isn't chosen yet; every later step speaks the chosen language.
_TEXTS = {
    "en": {
        "step_model":  "\nStep 2/4 — Select a model  (✓ = API key already in env):\n",
        "mock_line":   "  m) mock  (offline, no key — just to try the flow)\n",
        "choose":      "> Choose [1-{n} / m, Enter = default {default}]: ",
        "step_key":    "\nStep 3/4 — API key",
        "key_found":   "  ✓ {env_key} found in environment — using it.",
        "key_needed":  "  {label} needs {env_key}. Get a key from the provider, then paste it below.",
        "key_prompt":  "> Paste {env_key} (input hidden): ",
        "key_empty":   "No key entered. Pick another model or set the key in .env.",
        "key_save":    "> Save it to .env so you won't re-enter next time? [Y/n]: ",
        "key_saved":   "  ✓ saved to .env",
        "step_symbol": "\nStep 4/4 — Enter symbol (NVDA / 600519 / 0700): ",
        "no_symbol":   "No symbol entered.",
    },
    "zh": {
        "step_model":  "\n第 2/4 步 —— 选择模型（✓ = 环境里已有该 key）：\n",
        "mock_line":   "  m) mock（离线、无需 key，只为体验流程）\n",
        "choose":      "> 选择 [1-{n} / m，回车默认 {default}]: ",
        "step_key":    "\n第 3/4 步 —— API key",
        "key_found":   "  ✓ 环境里已找到 {env_key}，直接使用。",
        "key_needed":  "  {label} 需要 {env_key}。先去对应平台申请 key，然后粘贴到下面。",
        "key_prompt":  "> 粘贴 {env_key}（输入不回显）: ",
        "key_empty":   "没有输入 key。请换个模型，或在 .env 里填好。",
        "key_save":    "> 保存到 .env，下次免输？[Y/n]: ",
        "key_saved":   "  ✓ 已保存到 .env",
        "step_symbol": "\n第 4/4 步 —— 输入代码 (NVDA / 600519 / 0700): ",
        "no_symbol":   "没有输入代码。",
    },
}


def _t(lang: str, key: str, **kw) -> str:
    s = _TEXTS.get(lang, _TEXTS["en"]).get(key) or _TEXTS["en"][key]
    return s.format(**kw) if kw else s


def _choose_lang(default: str = "en") -> str:
    print("Step 1/4 — Language / 第 1/4 步 —— 语言")
    try:
        raw = input(f"> [zh / en, Enter = {default}]: ").strip().lower()
    except (EOFError, KeyboardInterrupt):
        return default
    return raw if raw in ("zh", "en") else default


def _choose_model(lang: str, default: str = "gemini") -> str:
    """Print the model menu (with ✓/✗ for matched API keys) and return a provider."""
    print(_t(lang, "step_model"))
    for i, p in enumerate(PROVIDER_CATALOG, 1):
        mark = "✓" if _has_key(p["env_key"]) else "—"
        star = "  (default)" if p["provider"] == default else ""
        print(f"  {i}) {p['label']:<42} [{mark}]{star}")
    print(_t(lang, "mock_line"))
    try:
        raw = input(_t(lang, "choose", n=len(PROVIDER_CATALOG), default=default)).strip().lower()
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


def _save_key_to_dotenv(env_key: str, value: str, path: str = ".env") -> None:
    """Append or update a single KEY=value line in ./.env (creating it if needed)."""
    lines: list[str] = []
    found = False
    if os.path.exists(path):
        with open(path, encoding="utf-8") as f:
            lines = f.read().splitlines()
        for i, ln in enumerate(lines):
            if ln.strip().startswith(env_key + "="):
                lines[i] = f"{env_key}={value}"
                found = True
                break
    if not found:
        lines.append(f"{env_key}={value}")
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")


def _ensure_key(provider: str, lang: str) -> bool:
    """Step 3: make sure the chosen provider has an API key, prompting for it if
    missing (and offering to save it to .env). Returns False to abort."""
    cat = next((p for p in PROVIDER_CATALOG if p["provider"] == provider), None)
    if cat is None:
        return True  # custom/typed provider name — let the adapter handle it
    env_key = cat["env_key"]
    print(_t(lang, "step_key"))
    if _has_key(env_key):
        print(_t(lang, "key_found", env_key=env_key))
        return True
    print(_t(lang, "key_needed", label=cat["label"], env_key=env_key))
    try:
        entered = getpass.getpass(_t(lang, "key_prompt", env_key=env_key)).strip()
    except (EOFError, KeyboardInterrupt):
        return False
    if not entered:
        print(_t(lang, "key_empty"), file=sys.stderr)
        return False
    os.environ[env_key] = entered  # adapters read this as a fallback
    try:
        save = input(_t(lang, "key_save")).strip().lower()
    except (EOFError, KeyboardInterrupt):
        save = ""
    if save in ("", "y", "yes"):
        try:
            _save_key_to_dotenv(env_key, entered)
            print(_t(lang, "key_saved"))
        except Exception:
            pass
    return True


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

    # interactive wizard: language → model → API key → symbol
    print(BANNER)
    lang = _choose_lang()                 # Step 1
    provider = _choose_model(lang)        # Step 2
    if provider != "mock":                # Step 3
        if not _ensure_key(provider, lang):
            return 1
    try:
        symbol = input(_t(lang, "step_symbol")).strip()   # Step 4
    except (EOFError, KeyboardInterrupt):
        return 0
    if not symbol:
        print(_t(lang, "no_symbol"), file=sys.stderr)
        return 1
    return asyncio.run(_run(symbol, llm=provider, lang=lang, departments=None, grounding=True))


if __name__ == "__main__":
    raise SystemExit(main())
