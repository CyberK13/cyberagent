"""cyberagent local web page — a CLI-styled homepage to drive the analyst chain.

    python -m cyberagent.web            # then open http://127.0.0.1:8000
    cyberagent serve --port 8000

Pick language + model (the matching API key is auto-detected from .env), enter a
symbol, and the 5-department physical-bottleneck chain runs and renders.
"""

from __future__ import annotations

import asyncio
import os

from .chain import AnalystChain
from .llm_adapter import PROVIDER_CATALOG

_INDEX = r"""<!doctype html>
<html lang="en"><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>cyberagent // bottleneck terminal</title>
<script src="https://cdn.jsdelivr.net/npm/marked/marked.min.js"></script>
<style>
:root{
  --bg:#04070a; --panel:#070c12; --fg:#d7e6e3; --mut:#5f7682; --faint:#33424c;
  --grn:#5dff9f; --cyan:#3df0ff; --red:#ff5f7a; --yel:#ffe45f; --blu:#5fafff;
  --bd:#13242b; --bd2:#1d3a44;
  --mono:ui-monospace,'SF Mono','JetBrains Mono','Fira Code',Menlo,Consolas,'PingFang SC',monospace;
}
*{box-sizing:border-box;border-radius:0!important}
html,body{margin:0;background:var(--bg);color:var(--fg);font-family:var(--mono);font-size:13.5px;line-height:1.55}
/* grid + scanline atmosphere */
body::before{content:"";position:fixed;inset:0;pointer-events:none;z-index:0;
  background:
    linear-gradient(transparent 95%, rgba(61,240,255,.035) 100%) 0 0/100% 26px,
    linear-gradient(90deg, transparent 95%, rgba(61,240,255,.025) 100%) 0 0/26px 100%,
    radial-gradient(ellipse at 50% -10%, rgba(61,240,255,.10), transparent 60%);}
body::after{content:"";position:fixed;inset:0;pointer-events:none;z-index:2;opacity:.5;
  background:repeating-linear-gradient(0deg, rgba(0,0,0,.18) 0, rgba(0,0,0,.18) 1px, transparent 1px, transparent 3px);
  animation:scan 7s linear infinite;}
@keyframes scan{from{background-position:0 0}to{background-position:0 120px}}
.wrap{position:relative;z-index:3;max-width:1020px;margin:0 auto;padding:26px 20px 60px}
.glow{text-shadow:0 0 7px currentColor}
/* header */
.head{border:1px solid var(--bd2);padding:14px 18px;position:relative;margin-bottom:14px;
  background:linear-gradient(180deg,rgba(61,240,255,.05),transparent)}
.brand{font-size:20px;font-weight:700;color:var(--cyan);letter-spacing:1px}
.brand b{color:var(--grn)}
.cur{display:inline-block;width:9px;height:16px;background:var(--grn);margin-left:4px;vertical-align:-2px;
  box-shadow:0 0 8px var(--grn);animation:blink 1.1s steps(1) infinite}
@keyframes blink{50%{opacity:0}}
.tag{color:var(--mut);margin-top:4px;font-size:12.5px}
.statusbar{margin-top:10px;display:flex;gap:18px;flex-wrap:wrap;font-size:12px;color:var(--mut);border-top:1px dashed var(--bd2);padding-top:8px}
.statusbar .dot{color:var(--grn)} .statusbar b{color:var(--fg)}
/* corner-bracket panels */
.panel{position:relative;border:1px solid var(--bd);background:var(--panel);padding:16px 18px;margin:14px 0}
.panel::before,.panel::after{content:"";position:absolute;width:11px;height:11px;border:1.5px solid var(--cyan);
  filter:drop-shadow(0 0 4px var(--cyan))}
.panel::before{top:-1px;left:-1px;border-right:0;border-bottom:0}
.panel::after{bottom:-1px;right:-1px;border-left:0;border-top:0}
.plabel{position:absolute;top:-9px;left:14px;background:var(--bg);padding:0 8px;color:var(--cyan);font-size:11px;letter-spacing:1.5px}
/* control rows */
.row{display:flex;flex-wrap:wrap;gap:9px;align-items:center;margin:9px 0}
.lbl{color:var(--mut);width:58px}
.lbl::before{content:"> ";color:var(--grn)}
button{background:transparent;color:var(--mut);border:1px solid var(--bd2);padding:6px 13px;cursor:pointer;
  font:inherit;transition:.12s;letter-spacing:.5px}
button:hover{color:var(--fg);border-color:var(--cyan);box-shadow:0 0 9px rgba(61,240,255,.35)}
button.on{color:var(--grn);border-color:var(--grn);box-shadow:0 0 11px rgba(93,255,159,.4)}
button:disabled{opacity:.4;cursor:wait}
.k{color:var(--grn)} .x{color:var(--red)}
input{background:#03070b;color:var(--grn);border:1px solid var(--bd2);padding:8px 11px;font:inherit;min-width:260px;
  letter-spacing:1px;text-shadow:0 0 6px rgba(93,255,159,.45)}
input:focus{outline:0;border-color:var(--cyan);box-shadow:0 0 11px rgba(61,240,255,.35)}
#go{color:var(--grn);border-color:var(--grn);font-weight:700}
#go:hover{background:rgba(93,255,159,.08);box-shadow:0 0 16px rgba(93,255,159,.5)}
/* status / progress log */
#status{color:var(--yel);margin:14px 2px;min-height:18px;white-space:pre-wrap}
#log{margin:6px 0;color:var(--mut)} #log .l{opacity:0;animation:fadein .25s forwards}
#log .ok{color:var(--grn)} @keyframes fadein{to{opacity:1}}
/* cyber processing animation */
#proc{display:none;margin:14px 0}
.procline{display:flex;align-items:center;gap:16px;flex-wrap:wrap;color:var(--cyan)}
.spin{display:inline-block;width:16px;height:16px;border:2px solid var(--bd2);
  border-top-color:var(--cyan);border-right-color:var(--grn);border-radius:50%!important;
  animation:spin .8s linear infinite;filter:drop-shadow(0 0 6px var(--cyan))}
@keyframes spin{to{transform:rotate(360deg)}}
.tmono{color:var(--grn);text-shadow:0 0 7px var(--grn);font-weight:700}
.dots::after{content:"";animation:dots 1.3s steps(4,end) infinite}
@keyframes dots{0%{content:""}25%{content:"."}50%{content:".."}75%{content:"..."}100%{content:"..."}}
.bar{position:relative;height:16px;border:1px solid var(--bd2);margin-top:13px;overflow:hidden;
  background:repeating-linear-gradient(90deg,#03070b 0,#03070b 9px,#061018 9px,#061018 10px)}
.fill{height:100%;width:0;background:linear-gradient(90deg,var(--grn),var(--cyan));
  box-shadow:0 0 14px var(--cyan);transition:width .3s linear;position:relative}
.fill::after{content:"";position:absolute;inset:0;
  background:linear-gradient(90deg,transparent,rgba(255,255,255,.55),transparent);
  animation:sweep 1.4s linear infinite}
@keyframes sweep{from{transform:translateX(-100%)}to{transform:translateX(100%)}}
/* result */
.verdict{display:flex;align-items:center;gap:14px;flex-wrap:wrap}
.badge{border:1px solid var(--grn);color:var(--grn);padding:3px 14px;font-weight:700;letter-spacing:2px;
  box-shadow:0 0 14px rgba(93,255,159,.45)}
.meta{color:var(--mut)} .meta b{color:var(--fg)}
h2{font-size:14px;color:var(--cyan);letter-spacing:1px;margin:2px 0 10px;border-bottom:1px solid var(--bd);padding-bottom:6px}
h2::before{content:"▸ ";color:var(--grn)}
.panel :is(h3,h4){color:var(--blu)} .panel strong{color:var(--grn)} .panel code{color:var(--yel)}
.panel pre{white-space:pre-wrap;overflow-x:auto} a{color:var(--cyan)}
.foot{color:var(--faint);text-align:center;margin-top:30px;font-size:11px;letter-spacing:1px}
</style></head>
<body><div class="wrap">

  <div class="head">
    <div class="brand glow">$ <b>cyber</b>agent<span class="cur"></span></div>
    <div class="tag">PHYSICAL-BOTTLENECK · REVERSE-CONSENSUS · ANALYST CHAIN</div>
    <div class="statusbar">
      <span><span class="dot glow">●</span> SYSTEM ONLINE</span>
      <span>LANG <b id="sLang">zh</b></span>
      <span>MODEL <b id="sModel">gemini</b></span>
      <span>CHAIN <b>physical→human→econ→fin→leaders</b></span>
    </div>
  </div>

  <div class="panel">
    <span class="plabel">CONFIG</span>
    <div class="row"><span class="lbl" id="lLang"></span>
      <button class="lang" data-l="zh">中文 ZH</button>
      <button class="lang on" data-l="en">English</button>
    </div>
    <div class="row"><span class="lbl" id="lModel"></span><span id="models"></span></div>
    <div class="row"><span class="lbl" id="lSym"></span>
      <input id="sym" value="MRVL" autocomplete="off">
      <button id="go"></button>
    </div>
  </div>

  <div id="status"></div>
  <div id="proc" class="panel"><span class="plabel">PROCESSING</span>
    <div class="procline">
      <span class="spin"></span>
      <span id="procLabel" class="dots"></span>
      <span>· <span id="lElapsed"></span> <b id="elapsed" class="tmono">00:00</b></span>
      <span>· <span id="lEta"></span> <b id="eta" class="tmono"></b></span>
    </div>
    <div class="bar"><div class="fill" id="fill"></div></div>
  </div>
  <div id="log"></div>
  <div id="out"></div>
  <div class="foot" id="foot"></div>
</div>
<script>
let LANG="en", LLM="gemini";
const I18N={
  en:{lang:"Language",model:"Model",sym:"Symbol",analyze:"▸ ANALYZE",
      ph:"NVDA / 600519 / 0700",conf:"confidence",
      run:s=>`▸ analyzing ${s} · model=${LLM} · full 5-dept ~1-3 min, bottleneck-chain reasoning…`,
      stageRun:"… running",done:s=>`✓ COMPLETE · ${s}s`,
      foot:"cyberagent // local terminal · not financial advice",
      stages:["Positioning","Physical World","Human Development","Economics","Company Financials","Leaders & Verdict"],
      pos:"Positioning",proc:"analyzing",elapsed:"ELAPSED",eta:"ETA",etaFull:"~2-3 min (full 5-dept)",etaMock:"~1s (mock)"},
  zh:{lang:"语言",model:"模型",sym:"标的",analyze:"▸ 分析",
      ph:"NVDA / 600519 / 0700",conf:"置信度",
      run:s=>`▸ 分析 ${s} · model=${LLM} · 完整 5 部门约 1-3 分钟，物理瓶颈链推理中…`,
      stageRun:"… 运行中",done:s=>`✓ 完成 · ${s}s`,
      foot:"cyberagent // 本地终端 · 非投资建议",
      stages:["资产定位","物理世界分析","人类发展分析","经济学分析","公司当前财务","行业龙头与建议"],
      pos:"资产定位",proc:"分析中",elapsed:"已用时",eta:"预计",etaFull:"约 2-3 分钟（完整 5 部门）",etaMock:"约 1 秒（mock）"}
};
const $=s=>document.querySelector(s);
function setStatus(t,c){const s=$("#status");s.textContent=t;s.style.color=c||"var(--yel)"}
function applyLang(){
  const t=I18N[LANG];
  $("#lLang").textContent=t.lang;$("#lModel").textContent=t.model;$("#lSym").textContent=t.sym;
  $("#go").textContent=t.analyze;$("#sym").placeholder=t.ph;$("#foot").textContent=t.foot;
  $("#sLang").textContent=LANG;
  document.querySelectorAll(".lang").forEach(x=>x.classList.toggle("on",x.dataset.l===LANG));
}
async function loadModels(){
  const ms=await (await fetch("/api/models")).json();
  const box=$("#models");box.innerHTML="";
  const add=(p,label,ok)=>{const b=document.createElement("button");
    b.innerHTML=label+" "+(ok===null?"":(ok?'<span class="k">✓</span>':'<span class="x">✗</span>'));
    b.className="mdl"+(p===LLM?" on":"");b.dataset.p=p;
    b.onclick=()=>{LLM=p;$("#sModel").textContent=p;document.querySelectorAll(".mdl").forEach(x=>x.classList.remove("on"));b.classList.add("on")};
    box.appendChild(b)};
  ms.forEach(m=>add(m.provider,m.label,m.available));
  add("mock","MOCK·offline",null);
}
document.querySelectorAll(".lang").forEach(b=>b.onclick=()=>{LANG=b.dataset.l;applyLang()});
function startLog(){
  const log=$("#log");log.innerHTML="";let i=0;const stages=I18N[LANG].stages,run=I18N[LANG].stageRun;
  const id=setInterval(()=>{ if(i>=stages.length){return}
    const d=document.createElement("div");d.className="l";
    d.innerHTML="  ["+String(i+1).padStart(2,"0")+"] "+stages[i]+" <span style='color:var(--mut)'>"+run+"</span>";
    log.appendChild(d);i++;
  },1400);
  return ()=>clearInterval(id);
}
let _t0=0,_timer=0;
function startProc(){
  const t=I18N[LANG], eta=(LLM==="mock")?2:160;
  $("#procLabel").textContent=t.proc;$("#lElapsed").textContent=t.elapsed;$("#lEta").textContent=t.eta;
  $("#eta").textContent=(LLM==="mock")?t.etaMock:t.etaFull;
  $("#proc").style.display="block";$("#fill").style.width="0%";_t0=Date.now();
  _timer=setInterval(()=>{
    const el=(Date.now()-_t0)/1000;
    $("#elapsed").textContent=String(Math.floor(el/60)).padStart(2,"0")+":"+String(Math.floor(el%60)).padStart(2,"0");
    $("#fill").style.width=Math.min(96,el/eta*100).toFixed(1)+"%";
  },250);
}
function stopProc(){clearInterval(_timer);$("#fill").style.width="100%";setTimeout(()=>$("#proc").style.display="none",450)}
$("#go").onclick=async()=>{
  const sym=$("#sym").value.trim();if(!sym)return;const t=I18N[LANG];
  $("#out").innerHTML="";const stop=startLog();startProc();
  setStatus(t.run(sym));$("#go").disabled=true;
  try{
    const d=await (await fetch("/api/analyze",{method:"POST",headers:{"Content-Type":"application/json"},
      body:JSON.stringify({symbol:sym,llm:LLM,lang:LANG})})).json();
    stop();
    if(!d.ok){setStatus("✗ "+(d.error||"failed"),"var(--red)");return}
    document.querySelectorAll("#log .l").forEach(e=>{e.classList.add("ok");
      e.innerHTML=e.innerHTML.replace(I18N[LANG].stageRun,"✓").replace(/<span[^>]*>(.*?)<\/span>/,"$1")});
    setStatus(t.done(d.elapsed),"var(--grn)");
    let h=`<div class="panel verdict"><span class="plabel">VERDICT</span>
      <span class="badge glow">${d.decision||"-"}</span>
      <span class="meta">${t.conf} <b>${d.confidence}</b> · <b>${d.company_name}</b> (${d.market})</span></div>`;
    if(d.headline)h+=`<div class="panel"><span class="plabel">HEADLINE</span>${marked.parse(d.headline)}</div>`;
    if(d.positioning)h+=`<div class="panel"><span class="plabel">PHASE-0</span><h2>${t.pos}</h2>${marked.parse(d.positioning)}</div>`;
    d.departments.forEach((x,i)=>h+=`<div class="panel"><span class="plabel">D${i+1}</span><h2>${x.display}</h2>${marked.parse(x.markdown)}</div>`);
    $("#out").innerHTML=h;
  }catch(e){stop();setStatus("✗ "+e,"var(--red)")}
  finally{stopProc();$("#go").disabled=false}
};
applyLang();loadModels();
</script>
</body></html>"""


def _make_app():
    try:
        from flask import Flask, jsonify, request
    except ImportError as e:  # pragma: no cover
        raise ImportError("web UI needs `pip install 'cyberagent[web]'`") from e

    app = Flask(__name__)

    @app.get("/")
    def index():
        return _INDEX

    @app.get("/api/models")
    def models():
        return jsonify([
            {"provider": p["provider"], "label": p["label"].split(" (")[0],
             "available": bool(os.getenv(p["env_key"])), "env_key": p["env_key"]}
            for p in PROVIDER_CATALOG
        ])

    @app.post("/api/analyze")
    def analyze():
        from flask import jsonify, request
        body = request.get_json(force=True) or {}
        symbol = (body.get("symbol") or "").strip()
        llm = body.get("llm") or "gemini"
        lang = body.get("lang") or "zh"
        if not symbol:
            return jsonify({"ok": False, "error": "no symbol"})
        try:
            chain = AnalystChain(llm=llm, lang=lang)
            report = asyncio.run(chain.analyze(symbol))
        except Exception as e:  # noqa: BLE001
            return jsonify({"ok": False, "error": str(e)})
        if not report.success:
            return jsonify({"ok": False, "error": report.error})
        return jsonify({
            "ok": True, "company_name": report.company_name, "market": report.market,
            "decision": report.final_decision, "confidence": report.confidence,
            "headline": report.headline, "positioning": report.positioning,
            "elapsed": report.elapsed_seconds,
            "departments": [
                {"key": k, "display": d.display_name, "markdown": d.markdown}
                for k, d in report.departments.items()
            ],
        })

    return app


def serve(host: str = "127.0.0.1", port: int = 8000) -> None:
    # load local .env so model keys are auto-detected
    try:
        from .cli import _load_dotenv
        _load_dotenv()
    except Exception:
        pass
    app = _make_app()
    print(f"cyberagent web -> http://{host}:{port}  (Ctrl+C to stop)")
    app.run(host=host, port=port, debug=False)


if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser(prog="cyberagent.web")
    ap.add_argument("--host", default="127.0.0.1")
    ap.add_argument("--port", type=int, default=8000)
    serve(**vars(ap.parse_args()))
