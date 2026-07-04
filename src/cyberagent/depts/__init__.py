"""Department runner.

The 5 departments (industry / financial / risk / valuation / strategy) share one
runner: each is a single LLM call with its department system prompt + a user
message assembled from the data context and upstream reports. The 5-step
physical-bottleneck logic lives in the prompts (see ``cyberagent.prompts``).
"""

from __future__ import annotations

from typing import Optional

from ..llm_adapter import LLMAdapter
from ..models import DeptReport
from ..prompts import (
    build_positioning_prompt,
    build_user_prompt,
    get_department,
    positioning_system_prompt,
    system_prompt,
)


async def run_positioning(
    *,
    llm: LLMAdapter,
    company_name: str,
    code: str,
    market: str,
    data_md: str,
    lang: str = "zh",
) -> str:
    """Phase 0 — core business + physical-world positioning (a short statement)."""
    try:
        return await llm.complete(
            positioning_system_prompt(lang, search=getattr(llm, "supports_search", False)),
            build_positioning_prompt(
                company_name=company_name, code=code, market=market,
                data_md=data_md, lang=lang,
            ),
        )
    except Exception as e:  # noqa: BLE001
        return f"(positioning failed: {e})"


async def run_department(
    key: str,
    *,
    llm: LLMAdapter,
    company_name: str,
    code: str,
    market: str,
    data_md: str,
    prior_reports: Optional[dict[str, str]] = None,
    lang: str = "zh",
) -> DeptReport:
    """Run one department and return its DeptReport."""
    spec = get_department(key)
    display = spec["display_zh"] if lang == "zh" else spec["display_en"]
    system = system_prompt(key, lang, search=getattr(llm, "supports_search", False))
    user = build_user_prompt(
        key, company_name=company_name, code=code, market=market,
        data_md=data_md, prior_reports=prior_reports, lang=lang,
    )
    try:
        markdown = await llm.complete(system, user)
        return DeptReport(name=key, display_name=display, markdown=markdown, success=True)
    except Exception as e:  # noqa: BLE001 — surface as a failed dept, don't crash the chain
        return DeptReport(
            name=key, display_name=display,
            markdown=f"(department failed: {e})", success=False, error=str(e),
        )
