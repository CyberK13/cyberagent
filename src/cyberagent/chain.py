"""AnalystChain — the public entry point.

    chain = AnalystChain(llm="gemini", api_key="...", lang="zh")
    report = await chain.analyze("NVDA")

Outer shape: classify -> fetch data -> run the 5 departments in sequence (each
reads the upstream reports) -> parse the strategy dept's final decision ->
AnalystReport. The analytical soul is the physical-bottleneck 5-step chain
encoded in ``cyberagent.prompts``.
"""

from __future__ import annotations

import re
import time
from typing import Optional, Sequence, Union

from . import adapters
from .classifier import classify
from .depts import run_department, run_positioning
from .llm_adapter import LLMAdapter, resolve_llm
from .models import AnalystReport, FinalDecision
from .prompts import DEPT_ORDER, get_department

_DECISIONS = ("ACCUMULATE", "HOLD", "REDUCE", "AVOID")


def _parse_verdict(markdown: str) -> tuple[Optional[FinalDecision], float, Optional[str]]:
    """Best-effort extraction of final_decision / confidence / headline from the
    closing (leaders) department's markdown."""
    decision: Optional[FinalDecision] = None
    up = markdown.upper()
    # Prefer a decision near a "final decision" marker, else first occurrence.
    marker = re.search(r"(FINAL DECISION|最终决策)(.{0,80})", up, re.DOTALL)
    search_space = marker.group(2) if marker else up
    for d in _DECISIONS:
        if d in search_space:
            decision = d  # type: ignore[assignment]
            break
    if decision is None:
        for d in _DECISIONS:
            if d in up:
                decision = d  # type: ignore[assignment]
                break

    confidence = 0.0
    # Skip an optional "(0-100)" scale label after the keyword, then grab the real number.
    cm = re.search(
        r"(?:置信度|confidence)\s*(?:[（(][^）)]*[）)])?\s*[:：]?\s*\n?\s*(\d{1,3})",
        markdown, re.IGNORECASE,
    )
    if cm:
        try:
            confidence = min(100, int(cm.group(1))) / 100.0
        except ValueError:
            pass

    headline = None
    hm = re.search(r"(?:headline|反共识)[^\n]*\n+([^\n]{4,160})", markdown, re.IGNORECASE)
    if hm:
        headline = hm.group(1).strip().lstrip("#-* ").strip()

    return decision, confidence, headline


class AnalystChain:
    def __init__(
        self,
        llm: Union[str, LLMAdapter] = "gemini",
        *,
        api_key: Optional[str] = None,
        model: Optional[str] = None,
        lang: str = "en",
        departments: Optional[Sequence[str]] = None,
        timeout: float = 20.0,
    ):
        self.llm = resolve_llm(llm, api_key=api_key, model=model)
        self.lang = lang
        self.departments = list(departments) if departments else list(DEPT_ORDER)
        self.timeout = timeout

    async def analyze(
        self,
        symbol: str,
        *,
        lang: Optional[str] = None,
        departments: Optional[Sequence[str]] = None,
        on_event=None,
    ) -> AnalystReport:
        """on_event(stage_key, label, status) — optional progress callback
        (status in {'start','done'}); used by the CLI for live progress."""
        lang = lang or self.lang
        dept_keys = [k for k in DEPT_ORDER if k in (departments or self.departments)]
        t0 = time.perf_counter()

        def _emit(stage, label, status):
            if on_event:
                try:
                    on_event(stage, label, status)
                except Exception:
                    pass

        asset = classify(symbol)
        report = AnalystReport(asset=asset, company_name=asset.code, market=asset.market)

        if asset.type == "unknown":
            report.success = False
            report.error = f"Could not classify {symbol!r}. Try cn:/us:/hk:/crypto:/evm: prefix."
            report.elapsed_seconds = round(time.perf_counter() - t0, 3)
            return report

        data_md, meta = await adapters.fetch(asset, timeout=self.timeout)
        report.company_name = meta.get("company_name") or asset.code
        if not data_md:
            # Live fetch failed (offline / rate-limited / unsupported market) — say
            # so loudly instead of letting the LLM silently run on stale memory.
            data_md = (
                "⚠ **LIVE DATA UNAVAILABLE** — the real-time fetch (quote/news) failed for this run. "
                "No current price or news is provided. State your knowledge cutoff, tag every "
                "time-sensitive claim as [Needs verification · possibly stale], and cap confidence accordingly."
            )

        # Phase 0: core business + physical-world positioning (grounds the whole chain)
        _emit("positioning", "资产定位 / Positioning", "start")
        report.positioning = await run_positioning(
            llm=self.llm, company_name=report.company_name, code=asset.code,
            market=asset.market, data_md=data_md, lang=lang,
        )
        _emit("positioning", "资产定位 / Positioning", "done")
        pos_label = "资产定位 / Positioning"
        grounded_md = f"## {pos_label}\n{report.positioning}\n\n## 原始数据 / Raw data\n{data_md}".strip()

        prior: dict[str, str] = {}
        for key in dept_keys:
            spec = get_department(key)
            label = spec["display_zh"] if lang == "zh" else spec["display_en"]
            _emit(key, label, "start")
            dr = await run_department(
                key, llm=self.llm, company_name=report.company_name, code=asset.code,
                market=asset.market, data_md=grounded_md, prior_reports=prior, lang=lang,
            )
            report.departments[key] = dr
            prior[key] = dr.markdown
            _emit(key, label, "done")

        closer = report.departments.get("leaders")
        if closer and closer.success:
            report.final_decision, report.confidence, report.headline = _parse_verdict(closer.markdown)

        report.elapsed_seconds = round(time.perf_counter() - t0, 3)
        return report
