"""Pydantic models for cyberagent's structured output.

The public, stable data contract of the package:

    AssetInfo      — what the classifier resolved the input to
    DeptReport     — one department's analysis
    AnalystReport  — the full 5-department result
"""

from __future__ import annotations

from typing import Any, Literal, Optional

from pydantic import BaseModel, Field

Market = Literal["CN", "US", "HK", "CRYPTO", "UNKNOWN"]
AssetType = Literal[
    "stock_cn",
    "stock_us",
    "stock_hk",
    "token",
    "evm_contract",
    "solana_contract",
    "unknown",
]
DeptName = Literal["physical", "human_dev", "economics", "financials", "leaders"]
FinalDecision = Literal["ACCUMULATE", "HOLD", "REDUCE", "AVOID"]


class AssetInfo(BaseModel):
    """Result of classifying a raw user input into a routable asset."""

    type: AssetType
    code: str                                  # normalized code
    raw_input: str = ""
    market: Market = "UNKNOWN"
    coingecko_id: Optional[str] = None         # when type == 'token'
    chain: Optional[str] = None                # when type endswith '_contract'
    confidence: float = 1.0                    # 0-1
    hints: dict[str, Any] = Field(default_factory=dict)


class DeptReport(BaseModel):
    """One department's analysis output."""

    name: DeptName
    display_name: str
    markdown: str
    success: bool = True
    structured_summary: dict[str, Any] = Field(default_factory=dict)
    error: Optional[str] = None


class AnalystReport(BaseModel):
    """The full result of running the 5-department analyst chain."""

    asset: AssetInfo
    company_name: str
    market: Market
    positioning: Optional[str] = None          # Phase 0: core business + physical-world position
    departments: dict[str, DeptReport] = Field(default_factory=dict)

    final_decision: Optional[FinalDecision] = None
    confidence: float = 0.0                    # 0-1
    headline: Optional[str] = None

    elapsed_seconds: float = 0.0
    success: bool = True
    error: Optional[str] = None

    def department(self, name: DeptName) -> Optional[DeptReport]:
        """Convenience lookup by department name."""
        return self.departments.get(name)
