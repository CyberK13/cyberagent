"""Run the 5-department physical-bottleneck chain end-to-end.

Offline by default (MockLLM, no API key needed). Swap in a real provider:

    chain = AnalystChain(llm="gemini", api_key="...", lang="zh")

Run:  python examples/basic.py
"""

import asyncio

from cyberagent import AnalystChain, MockLLM


async def main() -> None:
    chain = AnalystChain(llm=MockLLM(), lang="zh")   # -> AnalystChain(llm="gemini", api_key=...)

    report = await chain.analyze("NVDA")             # or "600519" / "0700"

    print(f"asset        : {report.asset.type} ({report.market})")
    print(f"company      : {report.company_name}")
    print(f"final_decision: {report.final_decision}  (confidence {report.confidence})")
    print(f"elapsed      : {report.elapsed_seconds}s\n")

    for key, dept in report.departments.items():
        print(f"## {dept.display_name}")
        print(dept.markdown[:300], "...\n")


if __name__ == "__main__":
    asyncio.run(main())
