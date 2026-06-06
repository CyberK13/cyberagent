"""Analysis prompts — fully open-source, bilingual (zh / en).

Phase 0 positioning + 5 departments (physical / human_dev / economics /
financials / leaders), anchored to references/sa-canon.md. The user picks a
language and the whole report is generated in it. No paywall.
"""

from .departments import (
    DEPARTMENTS,
    DEPT_ORDER,
    build_positioning_prompt,
    build_user_prompt,
    get_department,
    positioning_system_prompt,
    system_prompt,
)

__all__ = [
    "DEPARTMENTS",
    "DEPT_ORDER",
    "build_user_prompt",
    "build_positioning_prompt",
    "positioning_system_prompt",
    "get_department",
    "system_prompt",
]
