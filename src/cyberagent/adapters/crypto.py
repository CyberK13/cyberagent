"""Crypto data adapter — CoinGecko (no key, free tier).

Returns a markdown data block for a token. Network/errors degrade gracefully to
("", {"company_name": code}) so the chain can still run on LLM reasoning alone.
"""

from __future__ import annotations

from typing import Tuple

from ..models import AssetInfo

_CG = "https://api.coingecko.com/api/v3"


async def fetch(asset_info: AssetInfo, *, timeout: float = 10.0) -> Tuple[str, dict]:
    code = asset_info.code
    cgid = asset_info.coingecko_id
    meta = {"company_name": code}

    if asset_info.type in ("evm_contract", "solana_contract"):
        md = (
            f"### On-chain asset\n- Address: {code}\n- Chain: {asset_info.chain}\n"
            "- No token summary available without an indexer; rely on reasoning + search.\n"
        )
        return md, meta

    try:
        import httpx
    except ImportError:
        return "", meta

    try:
        async with httpx.AsyncClient(timeout=timeout) as client:
            if not cgid:
                r = await client.get(f"{_CG}/search", params={"query": code})
                coins = (r.json() or {}).get("coins", [])
                if coins:
                    cgid = coins[0]["id"]
            if not cgid:
                return "", meta
            r = await client.get(
                f"{_CG}/coins/{cgid}",
                params={"localization": "false", "tickers": "false", "market_data": "true",
                        "community_data": "false", "developer_data": "false", "sparkline": "false"},
            )
            d = r.json() or {}
    except Exception:
        return "", meta

    name = d.get("name") or code
    meta["company_name"] = name
    m = d.get("market_data") or {}

    def usd(block):
        return (m.get(block) or {}).get("usd")

    desc = ((d.get("description") or {}).get("en") or "").strip().replace("\n", " ")[:400]
    cats = ", ".join([c for c in (d.get("categories") or []) if c][:6])

    chg24 = m.get("price_change_percentage_24h")
    chg7 = m.get("price_change_percentage_7d")
    chg30 = m.get("price_change_percentage_30d")
    ath_chg = (m.get("ath_change_percentage") or {}).get("usd")
    flags = []
    try:
        if chg24 is not None and chg24 >= 20: flags.append(f"24h {chg24:+.0f}%")
        if chg7 is not None and chg7 >= 40: flags.append(f"7d {chg7:+.0f}%")
        if chg30 is not None and chg30 >= 80: flags.append(f"30d {chg30:+.0f}%")
        if ath_chg is not None and ath_chg >= -8: flags.append("near all-time high")
    except Exception:
        pass
    flag_md = ""
    if flags:
        flag_md = ("- ⚠ **PARABOLIC / NARRATIVE-MOVE FLAG**: " + "; ".join(flags) +
                   ". You MUST search WHY (catalyst / listing / KOL / unlock) and treat a "
                   "headline-driven spike as an AVOID/observe form, not a buy form.\n")
    meta["price_flags"] = flags

    md = (
        f"### Token: {name} ({(d.get('symbol') or '').upper()})\n"
        f"- Narrative / categories: {cats or 'N/A'}\n"
        f"- Price (USD): {usd('current_price')}\n"
        f"- Market cap (USD): {usd('market_cap')}\n"
        f"- Fully diluted valuation (USD): {usd('fully_diluted_valuation')}\n"
        f"- 24h volume (USD): {usd('total_volume')}\n"
        f"\n#### Price action (CHECK BEFORE THESIS)\n"
        f"- 24h / 7d / 30d change %: {chg24} / {chg7} / {chg30}\n"
        f"- ATH (USD): {usd('ath')} | from ATH %: {ath_chg}\n"
        f"{flag_md}"
        f"\n#### Supply\n"
        f"- Circulating: {m.get('circulating_supply')} | Total: {m.get('total_supply')} | Max: {m.get('max_supply')}\n"
        f"\n#### Description\n{desc or 'N/A'}\n"
        f"\n*(source: CoinGecko)*\n"
    )
    return md, meta
