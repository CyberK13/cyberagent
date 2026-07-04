"""Stock data adapter — yfinance (no key; needs network).

Covers US / HK / A-share via yfinance symbol mapping. Degrades gracefully to
("", {"company_name": code}) when yfinance is missing or offline.
"""

from __future__ import annotations

from typing import Tuple

from ..models import AssetInfo


def _cn_news(code6: str) -> list:
    """A-share news via akshare (Eastmoney, free, no key/signup) — yfinance has
    no news coverage for the CN market. Returns yfinance-shaped items so the
    downstream formatting is shared."""
    try:
        import akshare as ak
        df = ak.stock_news_em(symbol=code6)
        df = df.sort_values("发布时间", ascending=False)
        items = []
        for _, r in df.head(8).iterrows():
            items.append({"content": {
                "title": str(r.get("新闻标题") or "").strip(),
                "pubDate": str(r.get("发布时间") or ""),
                "provider": {"displayName": str(r.get("文章来源") or "").strip()},
                "summary": str(r.get("新闻内容") or "").strip(),
            }})
        return items
    except Exception:
        return []


def _yf_symbol(asset_info: AssetInfo) -> str:
    code = asset_info.code
    if asset_info.type == "stock_cn":
        # 600519.SH -> 600519.SS (Shanghai); .SZ / .BJ kept as yfinance expects
        return code.replace(".SH", ".SS")
    return code  # stock_us as-is; stock_hk already like 0700.HK


async def fetch(asset_info: AssetInfo, *, timeout: float = 10.0) -> Tuple[str, dict]:
    import asyncio
    from datetime import datetime, timezone

    code = asset_info.code
    meta = {"company_name": code}

    try:
        import yfinance as yf
    except ImportError:
        return "", meta
    # yfinance logs a raw "HTTP Error 404" for endpoints Yahoo lacks on some
    # markets (e.g. A-share rating history) — expected, keep it off the console
    import logging
    logging.getLogger("yfinance").setLevel(logging.CRITICAL)

    sym = _yf_symbol(asset_info)

    def _pull():
        try:
            t = yf.Ticker(sym)
            info = t.info or {}
            try:
                hist = t.history(period="6mo", interval="1d")
            except Exception:
                hist = None
            try:
                news = t.news or []
            except Exception:
                news = []
            if not news and asset_info.type == "stock_cn":
                news = _cn_news(code.split(".")[0])
            try:
                ratings = t.upgrades_downgrades
            except Exception:
                ratings = None
            return info, hist, news, ratings
        except Exception:
            return {}, None, [], None

    try:
        info, hist, news, ratings = await asyncio.wait_for(asyncio.to_thread(_pull), timeout=timeout)
    except Exception:
        return "", meta
    if not info:
        return "", meta

    name = info.get("longName") or info.get("shortName") or code
    meta["company_name"] = name
    price = info.get("currentPrice") or info.get("regularMarketPrice")
    currency = info.get("currency", "")

    fetched_at = datetime.now().astimezone().strftime("%Y-%m-%d %H:%M %Z")
    mkt_epoch = info.get("regularMarketTime")
    if isinstance(mkt_epoch, (int, float)):
        quote_as_of = datetime.fromtimestamp(mkt_epoch, tz=timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    else:
        quote_as_of = fetched_at
    meta["fetched_at"] = fetched_at
    meta["price"] = price

    # ── price action: recent returns + parabolic/spike flag (so the chain can
    #    SEE a narrative-driven run-up instead of treating a snapshot as stable) ──
    hi52 = info.get("fiftyTwoWeekHigh")
    lo52 = info.get("fiftyTwoWeekLow")
    pa_lines, flags = [], []
    try:
        if hist is not None and len(hist) > 3:
            close = hist["Close"].dropna()
            last = float(close.iloc[-1])
            for label, n in (("5D", 5), ("1M", 22), ("3M", 66)):
                if len(close) > n:
                    chg = (last / float(close.iloc[-n - 1]) - 1) * 100
                    pa_lines.append(f"  - {label} change: {chg:+.1f}%")
                    if label == "1M" and chg >= 40:
                        flags.append(f"1-month move {chg:+.0f}% (steep run-up)")
                    if label == "5D" and chg >= 25:
                        flags.append(f"5-day move {chg:+.0f}% (vertical spike)")
        if hi52 and price and float(price) / float(hi52) >= 0.95:
            flags.append("price within 5% of 52-week high")
        if hi52 and lo52 and float(lo52) > 0 and float(hi52) / float(lo52) >= 3:
            flags.append(f"52-week range is {float(hi52)/float(lo52):.1f}x (very wide)")
    except Exception:
        pass
    pa_block = ""
    if pa_lines or flags:
        pa_block = "\n#### Price action (CHECK BEFORE THESIS)\n" + "\n".join(pa_lines) + "\n"
        if flags:
            pa_block += ("- ⚠ **PARABOLIC / NARRATIVE-MOVE FLAG**: " + "; ".join(flags) +
                         ". You MUST search WHY the price moved (catalyst / who said what / news) "
                         "and treat a headline-driven spike as an AVOID/observe form, not a buy form.\n")
    meta["price_flags"] = flags

    # ── live news + analyst rating actions: fetched at runtime so EVERY provider
    #    (search-grounded or not) sees today's catalysts instead of its training
    #    memory. Empty for markets Yahoo doesn't cover (e.g. A-shares) — omitted. ──
    news_block = ""
    news_lines = []
    for item in (news or [])[:8]:
        c = item.get("content", item) if isinstance(item, dict) else {}
        title = c.get("title")
        if not title:
            continue
        pub = c.get("pubDate") or ""
        if not pub and isinstance(item.get("providerPublishTime"), (int, float)):
            pub = datetime.fromtimestamp(item["providerPublishTime"], tz=timezone.utc).strftime("%Y-%m-%d")
        prov = c.get("provider")
        src = prov.get("displayName") if isinstance(prov, dict) else item.get("publisher", "")
        summary = (c.get("summary") or "").strip().replace("\n", " ")
        line = f"  - [{str(pub)[:10]}] {title} ({src})"
        if summary:
            line += f" — {summary[:180]}"
        news_lines.append(line)
    if news_lines:
        news_block = (
            f"\n#### Recent news (LIVE, fetched {fetched_at} — use THESE as current catalysts, not memory)\n"
            + "\n".join(news_lines) + "\n"
        )

    ratings_block = ""
    try:
        if ratings is not None and len(ratings):
            rl = []
            for ts, row in ratings.head(8).iterrows():
                tgt = ""
                cur, prior = row.get("currentPriceTarget"), row.get("priorPriceTarget")
                if cur:
                    tgt = f", PT {prior:g}→{cur:g}" if prior else f", PT {cur:g}"
                rl.append(
                    f"  - [{str(ts)[:10]}] {row.get('Firm', '?')}: {row.get('priceTargetAction') or row.get('Action', '')}"
                    f" ({row.get('FromGrade') or '—'}→{row.get('ToGrade') or '—'}{tgt})"
                )
            if rl:
                ratings_block = (
                    "\n#### Recent analyst rating actions (LIVE — current revisions, cite these dates)\n"
                    + "\n".join(rl) + "\n"
                )
    except Exception:
        pass

    md = (
        f"### Company: {name} ({code})\n"
        f"- **Data fetched at: {fetched_at}**  (cite this date; do not use a remembered/older price)\n"
        f"- Sector / Industry: {info.get('sector', 'N/A')} / {info.get('industry', 'N/A')}\n"
        f"- Country: {info.get('country', 'N/A')}\n"
        f"- **Price ({currency}, as of {quote_as_of}): {price}**\n"
        f"- Market cap: {info.get('marketCap')}\n"
        f"- 52W high / low: {hi52} / {lo52}\n"
        f"{pa_block}"
        f"\n#### Valuation (note: market usually prices FORWARD)\n"
        f"- P/E (trailing / **forward**): {info.get('trailingPE')} / {info.get('forwardPE')}\n"
        f"- P/B: {info.get('priceToBook')} | P/S (trailing): {info.get('priceToSalesTrailing12Months')}\n"
        f"- EV/EBITDA: {info.get('enterpriseToEbitda')} | PEG: {info.get('pegRatio')}\n"
        f"\n#### Analyst consensus & ownership (cross-check 'is it already priced')\n"
        f"- Mean target / high / low: {info.get('targetMeanPrice')} / {info.get('targetHighPrice')} / {info.get('targetLowPrice')}"
        f"  (vs price {price}{' — ⚠ MEAN TARGET BELOW PRICE = overshoot signal' if (info.get('targetMeanPrice') and price and info.get('targetMeanPrice') < price) else ''})\n"
        f"- # analysts: {info.get('numberOfAnalystOpinions')} | recommendation: {info.get('recommendationKey')} (mean {info.get('recommendationMean')})\n"
        f"- Insider held %: {info.get('heldPercentInsiders')} | Institution held %: {info.get('heldPercentInstitutions')}\n"
        f"{ratings_block}"
        f"{news_block}"
        f"\n#### Fundamentals\n"
        f"- Total revenue: {info.get('totalRevenue')}\n"
        f"- Revenue growth: {info.get('revenueGrowth')}\n"
        f"- Earnings growth: {info.get('earningsGrowth')}\n"
        f"- Gross margin: {info.get('grossMargins')} | Operating margin: {info.get('operatingMargins')} | Profit margin: {info.get('profitMargins')}\n"
        f"- ROE: {info.get('returnOnEquity')} | ROA: {info.get('returnOnAssets')}\n"
        f"- Free cash flow: {info.get('freeCashflow')} | Operating cash flow: {info.get('operatingCashflow')}\n"
        f"- Total debt: {info.get('totalDebt')} | Debt/Equity: {info.get('debtToEquity')} | Current ratio: {info.get('currentRatio')}\n"
        f"\n#### Business\n{(info.get('longBusinessSummary') or 'N/A')[:600]}\n"
        f"\n*(source: yfinance, symbol {sym})*\n"
    )
    return md, meta
