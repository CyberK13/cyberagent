"""AssetClassifier — identify whether an input is a stock / token / contract
and route it to the right data adapter.

    classify("NVDA")        -> stock_us   code=NVDA
    classify("600519")      -> stock_cn   code=600519.SH
    classify("0700")        -> stock_hk   code=0700.HK
    classify("BTC")         -> token      code=btc   coingecko_id=bitcoin
    classify("0x6B17...")   -> evm_contract  chain=ethereum
    classify("crypto:JUP")  -> token      code=jup   coingecko_id=jupiter-exchange-solana

Explicit prefixes force routing: cn: / us: / hk: / crypto: / evm: / sol:
"""

from __future__ import annotations

import re

from .models import AssetInfo

# ──────────────────────────────────────────────────────────────────────────
# Token whitelist (symbol -> coingecko_id). Unknown symbols fall back to the
# CoinGecko search API at fetch time.
# ──────────────────────────────────────────────────────────────────────────
TOKEN_WHITELIST: dict[str, str] = {
    # Top market cap
    "BTC": "bitcoin", "ETH": "ethereum", "USDT": "tether", "BNB": "binancecoin",
    "SOL": "solana", "USDC": "usd-coin", "XRP": "ripple", "DOGE": "dogecoin",
    "ADA": "cardano", "TRX": "tron", "AVAX": "avalanche-2", "TON": "the-open-network",
    "DOT": "polkadot", "MATIC": "matic-network", "LINK": "chainlink",
    "WBTC": "wrapped-bitcoin", "LTC": "litecoin", "BCH": "bitcoin-cash",
    "NEAR": "near", "UNI": "uniswap", "XLM": "stellar", "ETC": "ethereum-classic",
    "ATOM": "cosmos", "XMR": "monero", "FIL": "filecoin", "APT": "aptos",
    "ARB": "arbitrum", "VET": "vechain", "OP": "optimism", "HBAR": "hedera-hashgraph",
    "IMX": "immutable-x", "INJ": "injective-protocol", "SUI": "sui",
    "RNDR": "render-token", "RENDER": "render-token", "GRT": "the-graph", "STX": "blockstack",
    # DeFi blue chips
    "AAVE": "aave", "MKR": "maker", "CRV": "curve-dao-token", "LDO": "lido-dao",
    "COMP": "compound-governance-token", "SNX": "havven", "FXS": "frax-share",
    "PENDLE": "pendle", "BAL": "balancer", "1INCH": "1inch", "RPL": "rocket-pool",
    # L2 / Modular / Restaking
    "TIA": "celestia", "EIGEN": "eigenlayer", "STRK": "starknet", "METIS": "metis-token",
    "MNT": "mantle", "ZK": "zksync", "MANTA": "manta-network", "BLAST": "blast",
    # Solana ecosystem
    "JUP": "jupiter-exchange-solana", "JTO": "jito-governance-token", "PYTH": "pyth-network",
    "WIF": "dogwifcoin", "BONK": "bonk", "POPCAT": "popcat", "W": "wormhole",
    # AI / DePIN narratives
    "TAO": "bittensor", "FET": "fetch-ai", "AGIX": "singularitynet", "OCEAN": "ocean-protocol",
    "AKT": "akash-network", "NMR": "numeraire", "WLD": "worldcoin-wld",
    # Meme
    "PEPE": "pepe", "SHIB": "shiba-inu", "FLOKI": "floki", "BOME": "book-of-meme",
    # RWA / stablecoin
    "ONDO": "ondo-finance", "FRAX": "frax", "DAI": "dai", "TUSD": "true-usd",
    # Others
    "HYPE": "hyperliquid", "KAS": "kaspa", "GMX": "gmx", "DYDX": "dydx-chain",
    "CFX": "conflux-token",
}

_SYMBOL_LOOKUP = {sym.lower(): cgid for sym, cgid in TOKEN_WHITELIST.items()}

RE_EVM_CONTRACT = re.compile(r"^0x[a-fA-F0-9]{40}$")
RE_CN_STOCK = re.compile(r"^(\d{6})(?:\.(SH|SZ|BJ))?$", re.IGNORECASE)
RE_HK_STOCK = re.compile(r"^(\d{1,5})(?:\.HK)?$", re.IGNORECASE)
RE_US_STOCK = re.compile(r"^[A-Z]{1,5}(\.[A-Z])?$")
RE_SOL_ADDR = re.compile(r"^[1-9A-HJ-NP-Za-km-z]{32,44}$")


def classify(raw: str, default_evm_chain: str = "ethereum") -> AssetInfo:
    """Identify the asset type of a raw input. Always returns an AssetInfo
    (type='unknown' rather than raising)."""
    if not raw:
        return AssetInfo(type="unknown", code="", raw_input="", confidence=0.0)

    s = raw.strip()

    # 0. Explicit prefix
    if ":" in s:
        prefix, _, rest = s.partition(":")
        prefix = prefix.strip().lower()
        rest = rest.strip()
        if prefix == "cn":
            return _cn_stock(rest, raw, forced=True)
        if prefix == "us":
            return _us_stock(rest, raw, forced=True)
        if prefix == "hk":
            return _hk_stock(rest, raw, forced=True)
        if prefix in ("crypto", "token"):
            return _token(rest, raw, forced=True)
        if prefix == "evm":
            return _evm_contract(rest, raw, default_evm_chain, forced=True)
        if prefix in ("sol", "solana"):
            return _solana(rest, raw, forced=True)

    # 1. EVM contract (strictest)
    if RE_EVM_CONTRACT.match(s):
        return _evm_contract(s, raw, default_evm_chain, forced=False)

    # 2. A-share (exactly 6 digits)
    if RE_CN_STOCK.match(s):
        return _cn_stock(s, raw, forced=False)

    # 3. Token whitelist (before US stock so BTC/ETH/SOL resolve to token)
    if s.lower() in _SYMBOL_LOOKUP:
        return _token(s, raw, forced=False)

    # 4. US stock (1-5 letters)
    if RE_US_STOCK.match(s.upper()):
        return _us_stock(s.upper(), raw, forced=False)

    # 5. HK stock (1-5 digits, not 6)
    if RE_HK_STOCK.match(s):
        return _hk_stock(s, raw, forced=False)

    # 6. Solana address (base58)
    if RE_SOL_ADDR.match(s) and len(s) >= 32:
        return _solana(s, raw, forced=False)

    return AssetInfo(
        type="unknown", code=s, raw_input=raw, confidence=0.0,
        hints={"reason": "no matching pattern; try cn:/us:/hk:/crypto:/evm: prefix"},
    )


def _cn_stock(s: str, raw: str, forced: bool) -> AssetInfo:
    s = s.strip().upper()
    m = RE_CN_STOCK.match(s)
    if not m:
        digits = "".join(c for c in s if c.isdigit())
        if len(digits) == 6:
            s = digits
            m = RE_CN_STOCK.match(s)
    if m:
        code_6, suffix = m.group(1), m.group(2)
        if not suffix:
            first = code_6[0]
            suffix = "SH" if first in ("6", "9") else ("BJ" if first in ("8", "4") else "SZ")
        return AssetInfo(
            type="stock_cn", code=f"{code_6}.{suffix.upper()}", raw_input=raw,
            market="CN", confidence=1.0 if not forced else 0.95,
            hints={"exchange": suffix.upper()},
        )
    return AssetInfo(type="unknown", code=s, raw_input=raw, confidence=0.0,
                     hints={"reason": "forced cn: but not 6-digit A-share format"})


def _hk_stock(s: str, raw: str, forced: bool) -> AssetInfo:
    digits = "".join(c for c in s.upper().replace(".HK", "") if c.isdigit())
    if not digits or len(digits) > 5:
        return AssetInfo(type="unknown", code=s, raw_input=raw, confidence=0.0,
                         hints={"reason": "not a 1-5 digit HK code"})
    code = f"{int(digits):04d}.HK"          # zero-pad to 4, e.g. 700 -> 0700.HK
    return AssetInfo(type="stock_hk", code=code, raw_input=raw, market="HK",
                     confidence=0.9 if forced else 0.7,
                     hints={"note": "HK stock (numeric code)"})


def _us_stock(s: str, raw: str, forced: bool) -> AssetInfo:
    return AssetInfo(type="stock_us", code=s.strip().upper(), raw_input=raw, market="US",
                     confidence=0.85 if not forced else 0.95,
                     hints={"note": "US stock or unknown small-cap ticker"})


def _token(s: str, raw: str, forced: bool) -> AssetInfo:
    sym = s.strip().lower()
    cgid = _SYMBOL_LOOKUP.get(sym)
    if cgid:
        return AssetInfo(type="token", code=sym, raw_input=raw, market="CRYPTO",
                         coingecko_id=cgid, confidence=1.0, hints={"source": "whitelist"})
    return AssetInfo(type="token", code=sym, raw_input=raw, market="CRYPTO",
                     coingecko_id=None, confidence=0.5 if forced else 0.3,
                     hints={"source": "unknown_symbol",
                            "note": "not in whitelist; will search CoinGecko at fetch time"})


def _evm_contract(s: str, raw: str, default_chain: str, forced: bool) -> AssetInfo:
    addr = s.strip()
    if not addr.startswith("0x"):
        addr = "0x" + addr
    addr = addr.lower()
    if not RE_EVM_CONTRACT.match(addr):
        return AssetInfo(type="unknown", code=addr, raw_input=raw, confidence=0.0,
                         hints={"reason": "not a valid EVM address"})
    return AssetInfo(type="evm_contract", code=addr, raw_input=raw, market="CRYPTO",
                     chain=default_chain, confidence=1.0,
                     hints={"note": "EVM address; chain defaulted"})


def _solana(s: str, raw: str, forced: bool) -> AssetInfo:
    addr = s.strip()
    if not RE_SOL_ADDR.match(addr):
        return AssetInfo(type="unknown", code=addr, raw_input=raw, confidence=0.0,
                         hints={"reason": "not a valid Solana base58 address"})
    return AssetInfo(type="solana_contract", code=addr, raw_input=raw, market="CRYPTO",
                     chain="solana", confidence=0.95 if forced else 0.85,
                     hints={"note": "Solana base58 address"})


class AssetClassifier:
    """Thin OO wrapper so `from cyberagent import AssetClassifier` works."""

    @staticmethod
    def classify(raw: str, default_evm_chain: str = "ethereum") -> AssetInfo:
        return classify(raw, default_evm_chain=default_evm_chain)
