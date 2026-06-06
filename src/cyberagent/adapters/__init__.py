"""Data adapters — route an AssetInfo to the right source and return a markdown
data block the departments can read.

    fetch(asset_info) -> (data_md, meta)

All adapters degrade gracefully: on missing libs / no network / errors they
return ("", {"company_name": code}) so the analyst chain still runs on LLM
reasoning alone.
"""

from __future__ import annotations

from typing import Tuple

from ..models import AssetInfo
from . import crypto, stock

__all__ = ["fetch", "crypto", "stock"]


async def fetch(asset_info: AssetInfo, *, timeout: float = 10.0) -> Tuple[str, dict]:
    """Return (data_md, meta) for an asset. meta always has 'company_name'."""
    t = asset_info.type
    try:
        if t in ("token", "evm_contract", "solana_contract"):
            return await crypto.fetch(asset_info, timeout=timeout)
        if t in ("stock_cn", "stock_us", "stock_hk"):
            return await stock.fetch(asset_info, timeout=timeout)
    except Exception:
        pass
    return "", {"company_name": asset_info.code}
