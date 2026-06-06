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


def test_prompts_have_bottleneck_soul_not_mao():
    blob = "".join(system_prompt(k, "zh") + system_prompt(k, "en") for k in DEPT_ORDER)
    # bottleneck-chain soul present
    assert "物理瓶颈" in blob and "再多钱也买不到" in blob
    # Mao content removed
    for banned in ("毛泽东", "矛盾论", "实践论", "论持久战", "principal contradiction"):
        assert banned not in blob, f"Mao content leaked: {banned}"
