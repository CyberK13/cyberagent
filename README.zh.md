<div align="center">

# 🧠 cyberagent

### 物理瓶颈 · 反共识投资分析框架 —— 面向*所有市场*

一条 LLM 智能体链，把任意标的一层层拆到卡住它所在产业的**物理约束**，核对市场
**是否已经定价**，并**拒绝追逐叙事驱动的尖顶**。覆盖 A 股 / 港股 / 美股。
自带 LLM key 即可运行。

[![PyPI](https://img.shields.io/pypi/v/cyberagent.svg)](https://pypi.org/project/cyberagent/)
[![Python](https://img.shields.io/badge/python-3.9%2B-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![X](https://img.shields.io/badge/X-@CyberK013-black.svg)](https://x.com/CyberK013)

### 🌐 Language / 语言

[English](README.md) &nbsp;|&nbsp; **简体中文**

</div>

---

## 它和别的有什么不一样

市面多数开源「AI 分析师」框架问的是*「这家公司好不好」*，产出一份教科书式 SWOT。
cyberagent 问的是一个更锋利、**可证伪、反共识**的问题，且严格按顺序：

> **物理瓶颈 → 唯一性 → 商业化 → 财务弹性 → 共识修正**
>
> *这个标的的供应链被哪个物理量卡住？它唯一吗？能变现吗？有没有非线性财务弹性？
> 市场是不是已经把它定价了？*

它建立在 Aschenbrenner《[Situational Awareness](https://situational-awareness.ai/)》
的一个核心判断上：**AI 扩张是一个大规模*工业*进程**，被物理输入卡住——电力、变压器、
HBM、CoWoS 先进封装、特定材料。cyberagent 把这个 thesis 落地：沿供应链一直拆到
*「再多钱也买不到」*的环节，再施加强硬的反叙事纪律，避免把头条驱动的暴涨误当机会。

它**不预测价格**。它给的是事实、可证伪的逻辑链、可监控的物理信号——最终决策由你做出。

---

## 思想基础

cyberagent 站在两个想法之上，并把它们变成一条可复现、可证伪的智能体链。

### Leopold Aschenbrenner —《Situational Awareness》（**为什么**）

在《[Situational Awareness：未来十年](https://situational-awareness.ai/)》里，Aschenbrenner
论证：**AI 扩张是一个大规模*工业*进程**，不是软件进程——每一代前沿模型都需要更大的集群、
更大的电厂、更大的芯片厂。所以绑定约束是**物理的**——电力、变压器、HBM、CoWoS 封装、特定
材料——而有效算力以每年约一个数量级（OOM）复合增长（GPT‑2 → GPT‑4 → ~2027 AGI）。拥有
*situational awareness* 的人靠趋势线，**在主流共识定价它之前数年**就建立 conviction。
cyberagent 就把市场当成这个物理系统；thesis 提炼在 [`references/sa-canon.md`](references/sa-canon.md)。

### Serenity 与 Crux —— 瓶颈方法（**怎么做**）

实操纪律来自供应链瓶颈猎手，比如 **Serenity**（[@aleabitoreddit](https://x.com/aleabitoreddit)）
和 **Crux Capital**。他们不先问*「哪只股票会涨？」*，而是**先把机器拆开，找那个堵点**：

> *这台机器到底长什么样？它的 BOM 里最难替代的零件是什么？如果其中一家明天停产，
> 下游要等多久？*

- **Serenity** 窄而深 —— 找一个制胜的堵点，押死。
- **Crux** 宽而有纪律 —— 画一张约六层的栈，每层按执行确定性排仓位，把已验证的执行者和早期期权分开。

cyberagent 把这套纪律提炼成一条固定、可证伪、任何 LLM 都能在任意市场上跑的链。

> 我们借的是他们的**方法**——沿供应链拆到物理堵点、问*「链在哪断」*、把执行和期权分开。
> 我们**不**冒充他们、不引用他们、不把他们的持仓当事实。

---

## 它怎么工作

这条链是一台**望远镜**——从物理现实一路缩放到可操作的具体标的，每一步是一次带 grounding
的 LLM 调用（都读上游报告）：

> **资产定位 → 物理世界 → 人类发展 → 经济学 → 公司财务 → 行业龙头与判定**

这台望远镜，正是上面那条五步*方法*链（瓶颈 → 唯一性 → 商业化 → 弹性 → 共识）的实际执行方式。

![AnalystChain —— 物理瓶颈分析流水线](https://raw.githubusercontent.com/CyberK13/cyberagent/main/docs/assets/analystchain-zh.png)

**Phase 0 · 资产定位。** 先用基本面锁定这家公司到底卖什么，再把它钉到物理 / AI
供应链的具体一层（材料 → 衬底 → 设备 → 封装 → 器件 → 模组 → 系统 → 终端）和一台
具体机器（如 *GB300 NVL72 机架*、*1.6T 光链*）。

**五个部门**顺序运行，每个都读上游报告：

| 部门 | `key` | 职责 |
|---|---|---|
| 🪨 物理世界 | `physical` | 在 SA 瓶颈阶梯上定位绑定约束（电力 > CoWoS/HBM > 裸逻辑）；把标的分类为 **owner / adjacent / derivative / none**。非 owner ⇒ 降级，禁用稀缺租金逻辑。 |
| 🌍 人类发展 | `human_dev` | 把需求放到 AGI / OOM 弧线上——早期（还有跑道）还是成熟/见顶？ |
| 💱 经济学 | `economics` | ore-seller vs processor；**把涨幅拆成盈利增长 vs 倍数扩张**；识别估值框架切换；是否*已被定价*（Gray Rhino vs 响亮共识）？ |
| 📈 公司财务 | `financials` | 基本面 + 财务弹性（线性 vs 非线性）；盈利异常先归因再当红旗。 |
| 🎯 行业龙头 | `leaders` | 两轴判定——**瓶颈身份(a) vs 定价位置(b)**——steelman + Munger 反向、可监控退出信号、最终决策。 |

### 纪律（它为什么不追尖顶）

这正是教科书框架跳过的部分：

- **实时搜索** —— 用 Gemini 时会*搜索价格为什么动*（催化剂、谁说的），而不是信模型记忆。
- **价格行为护栏** —— 数据层标记抛物线 / 贴近高点的异动；几天内靠一句话翻倍的股票是**回避/观察**形态，不是买入形态。
- **证据分级** —— 每个关键论断打 `Confirmed / Inferred / Weak` 标签；承重的 `Inferred` 会封顶置信度。
- **两个独立维度** —— *「是不是瓶颈」*（分类）与*「该不该在这个价位买」*（定价）绝不混为一谈。非瓶颈在某价位也能是好交易；真瓶颈在尖顶也可能是坏交易。
- **诚实标「晚了」** —— 抛物线 + 估值极值 + 共识响亮 ⇒ 标签是*「晚了/尖顶」*，不是机会。

> 仅供教育与研究用途。输出质量受模型、数据及诸多非确定因素影响。**不构成任何
> 财务、投资或交易建议。**

---

## 快速开始 —— 30 秒

```bash
python3 -m venv .venv && source .venv/bin/activate   # 隔离环境（Windows：.venv\Scripts\activate）
python3 -m pip install 'cyberagent[all]'             # 全套：行情数据 + 全部 LLM provider + 本地网页
cyberagent                                           # 启动交互式向导
```

安装时不用选模型。`cyberagent` 会一步步带你走 —— **① 语言 → ② 模型 → ③ 粘贴 API key
→ ④ 输入代码**（`NVDA` / `600519` / `0700`）—— 然后打印报告。就这些。（想用浏览器？
`cyberagent serve` 打开本地网页。）

> 用 `python3 -m pip`（不要用裸 `pip`）配合上面的 venv —— macOS 上常常没有 `pip`
> 命令（`command not found`），新版 Python 也会拒绝装进系统环境。venv 一次性绕开这两个坑。

想装得更精简？不必装全部 provider —— 只装一个的 extra（`gemini` / `deepseek` /
`openai` / `claude`）即可，例如 `python3 -m pip install 'cyberagent[stocks,web,deepseek]'`。
向导会提供该 provider；非交互用法用 `--llm <provider>`（见下方）。

## 在 Python 里使用

```python
import asyncio
from cyberagent import AnalystChain

chain = AnalystChain(llm="gemini", api_key="...", lang="zh")
report = asyncio.run(chain.analyze("NVDA"))

print(report.final_decision)                   # ACCUMULATE / HOLD / REDUCE / AVOID
print(report.departments["leaders"].markdown)
```

（Jupyter / 异步程序里直接 `await chain.analyze("NVDA")`。用 `lang="zh"` / `"en"`
选报告语言，整份报告都按它生成。完整 API 见 [`docs/quickstart.md`](docs/quickstart.md)。）

<details>
<summary><b>更多 —— 其它 LLM provider · 自定义 adapter · 安装选项 · CLI 参数</b></summary>

<br>

**Provider。** Gemini 是默认、也是唯一带实时 grounding 的；以下都可用：

```python
from cyberagent import AnalystChain, LLMAdapter, MockLLM

AnalystChain(llm="openai",   api_key="sk-...")
AnalystChain(llm="claude",   api_key="...")
AnalystChain(llm="deepseek", api_key="...")
AnalystChain(llm=MockLLM())                    # 离线、无 key —— 体验流程

class MyLLM(LLMAdapter):
    async def complete(self, system: str, user: str) -> str: ...
AnalystChain(llm=MyLLM())
```

key 可以传参、走环境变量、或放本地 `.env`（全部变量见 [`.env.example`](.env.example)）。
申请入口：[Gemini（免费）](https://aistudio.google.com/app/apikey) ·
[OpenAI](https://platform.openai.com/api-keys) ·
[Anthropic](https://console.anthropic.com/) ·
[DeepSeek](https://platform.deepseek.com/)。

**安装选项。** 裸 `pip install cyberagent` 是零依赖核心。extras：`stocks`（yfinance）·
`gemini` / `openai` / `claude` / `deepseek`（provider）· `web`（本地网页）· `all`（全部）。
DeepSeek 是 OpenAI 兼容接口，`deepseek` extra 即 `openai` 的别名——
`python3 -m pip install 'cyberagent[deepseek]'`，设 `DEEPSEEK_API_KEY`，用 `--llm deepseek`。

**CLI。**

```bash
cyberagent analyze NVDA --llm gemini --lang zh
cyberagent analyze AAPL --depts physical,economics,leaders   # 子集，更快
cyberagent serve                              # 本地网页 http://127.0.0.1:8000
```

CLI 和网页会自动加载 `.env`，带模型选择器（找到的 key 旁显示 ✓）、逐部门实时进度、渲染报告。

</details>

---


## 作为 Claude Skill 使用 —— 无需安装

整套方法论还被打包成一个自包含的 **Claude Skill**，见 [`SKILL.md`](SKILL.md)——它用纯
prompt 形态跑同一条物理瓶颈链，不需要 Python。在 **Claude Code** 里安装：

```bash
mkdir -p ~/.claude/skills/physical-bottleneck-analyst
curl -fsSL https://raw.githubusercontent.com/CyberK13/cyberagent/main/SKILL.md \
  -o ~/.claude/skills/physical-bottleneck-analyst/SKILL.md
```

然后直接说：*「分析 NVDA」*——Claude 会自动调起这个 skill。（其它能加载 skill 的
agent 同理：把 `SKILL.md` 给它即可。）Python 包在此之上加了实时数据、grounding 和
CLI / 网页。

## 方法论与 prompts —— 完全开源

没有付费墙。*怎么*狩猎物理瓶颈是框架知识，不是 alpha。完整的 system prompts 在
[`src/cyberagent/prompts/departments.py`](src/cyberagent/prompts/departments.py)；
《Situational Awareness》的锚（物理瓶颈阶梯 + OOM 发展弧线）提炼在
[`references/sa-canon.md`](references/sa-canon.md)。

---

## 路线图

- [ ] LangChain / LangGraph tool 封装
- [ ] MCP server（Claude / Cursor）
- [ ] EDGAR（美股文件）+ Tushare（A 股）adapter
- [ ] 多分部公司的分部级链
- [ ] 结构化的部门级闸门裁决（机器强制「停」）

---

## 免责声明

`final_decision` / `confidence` 与各部门报告均为 **AI 生成的教育性输出**，不构成投资建议。
LLM 会犯错，市场不可预测，请自行研究。作者与贡献者不对基于本软件的任何决策负责。
详见 [`docs/disclaimer.md`](docs/disclaimer.md)。

## 协议

MIT，见 [LICENSE](LICENSE)。

## 联系

有任何问题、想法或反馈，欢迎在 X 上联系：[**@CyberK013**](https://x.com/CyberK013)。
