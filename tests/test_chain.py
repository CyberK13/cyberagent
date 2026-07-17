"""End-to-end chain tests using the offline MockLLM (no network / no API key)."""

import asyncio

from cyberagent import AnalystChain, MockLLM, classify
from cyberagent.prompts import DEPT_ORDER, system_prompt


def test_classifier_routes_markets():
    assert classify("NVDA").type == "stock_us"
    assert classify("600519").type == "stock_cn"
    assert classify("0700").type == "stock_hk"
    assert classify("BTC").type == "token"
    assert classify("BTC").coingecko_id == "bitcoin"
    assert classify("0x6B175474E89094C44Da98b954EedeAC495271d0F").type == "evm_contract"
    assert classify("???bad").type == "unknown"


def test_chain_runs_all_five_departments_offline():
    chain = AnalystChain(llm=MockLLM(), lang="zh", timeout=1.0)
    report = asyncio.run(chain.analyze("BTC"))
    assert report.success
    assert report.market == "CRYPTO"
    assert list(report.departments.keys()) == list(DEPT_ORDER)
    assert list(DEPT_ORDER) == ["physical", "human_dev", "economics", "financials", "leaders"]
    assert all(d.success for d in report.departments.values())
    assert report.positioning  # Phase 0 ran
    assert report.final_decision in ("ACCUMULATE", "HOLD", "REDUCE", "AVOID")


def test_chain_subset_and_language():
    chain = AnalystChain(llm=MockLLM(), lang="en", departments=["physical", "leaders"], timeout=1.0)
    report = asyncio.run(chain.analyze("NVDA"))
    assert list(report.departments.keys()) == ["physical", "leaders"]


def test_unknown_symbol_is_graceful():
    chain = AnalystChain(llm=MockLLM(), timeout=1.0)
    report = asyncio.run(chain.analyze("@@@nonsense"))
    assert report.success is False
    assert report.error


def test_parse_verdict_ignores_template_enumeration():
    """A report that echoes the output template's 'ACCUMULATE / HOLD / REDUCE /
    AVOID' menu line must not be parsed as ACCUMULATE."""
    from cyberagent.chain import _parse_verdict

    md = (
        "### 最终决策：必须是 ACCUMULATE / HOLD / REDUCE / AVOID 之一\n"
        "**AVOID**（由定价位置(b)驱动）\n"
        "### 置信度（0-100）+ 扣分依据\n42（承重 Inferred -10）\n"
        "### 一句话反共识 headline\n共识已响亮，尖顶观察不追\n"
    )
    decision, confidence, headline = _parse_verdict(md)
    assert decision == "AVOID"
    assert confidence == 0.42
    assert headline and "共识" in headline


def test_parse_verdict_machine_line():
    from cyberagent.chain import _parse_verdict

    md = "...analysis...\nFINAL DECISION: HOLD | CONFIDENCE: 65/100\n"
    decision, confidence, _ = _parse_verdict(md)
    assert decision == "HOLD"
    assert confidence == 0.65


def test_parse_verdict_two_label_line_takes_first():
    from cyberagent.chain import _parse_verdict

    md = "### Final decision\nAVOID (or HOLD if you already own it)\n"
    decision, _, _ = _parse_verdict(md)
    assert decision == "AVOID"


def test_prompts_have_bottleneck_soul_not_mao():
    blob = "".join(system_prompt(k, "zh") + system_prompt(k, "en") for k in DEPT_ORDER)
    # bottleneck-chain soul present
    assert "物理瓶颈" in blob and "再多钱也买不到" in blob
    # Mao content removed
    for banned in ("毛泽东", "矛盾论", "实践论", "论持久战", "principal contradiction"):
        assert banned not in blob, f"Mao content leaked: {banned}"
