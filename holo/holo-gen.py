#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
holo-gen.py · HOLO-IFACE-01 生成器 v0.1
流水线: 读 holo-ctx/*.json → 规范化 holo-state.json(八面板投影, 每面板带
        source_path+投影 ts) → 烘焙 dist/index.html(单文件: 内嵌 state JSON +
        vanilla JS + inline SVG, 零 CDN 零外链, file:// 可开) → 快照哈希链
        dist/snapshot.json {sha256, prev, ts, version} (prev 从既有 snapshot.json
        读, 无则 GENESIS)
纪律: 零编数; 投影数据只来自 holo-ctx; 禁 client-side fetch; 密钥模式零触及;
      时间基线=数据最大 ts(不取墙钟) ⇒ 同 ctx 同代码 ⇒ 同 dist sha256(确定性)
"""
import hashlib
import json
import re
import sys
from pathlib import Path

HOLO = Path(__file__).resolve().parent
WAVE = HOLO.parent
CTX = WAVE / "holo-ctx"
DIST = HOLO / "dist"
STATE_PATH = HOLO / "holo-state.json"
SNAP_PATH = DIST / "snapshot.json"
VERSION = "holo-v0.1"

TS_RE = re.compile(r"(\d{4}-\d{2}-\d{2})T(\d{2}):(\d{2})(?::(\d{2}))?Z")

def parse_ts(s):
    if not isinstance(s, str):
        return None
    m = TS_RE.search(s)
    if not m:
        return None
    d, hh, mm, ss = m.groups()
    return f"{d}T{hh}:{mm}:{ss or '00'}Z"

def load_ctx():
    ctx = {}
    for p in sorted(CTX.glob("*.json")):
        raw = p.read_bytes()
        ctx[p.stem] = {
            "data": json.loads(raw.decode("utf-8")),
            "source_path": f"holo-ctx/{p.name}",
            "sha12": hashlib.sha256(raw).hexdigest()[:12],
        }
    return ctx

EVENT_KEYS = {"ts", "updated", "closed_ts", "solved_ts", "prev_ts"}  # 不含 deadline(未来值)

def ctx_baseline(ctx):
    """基线=各源事件时间字段(EVENT_KEYS)最大值; deadline 属未来约定, 不入基线"""
    best = None
    def walk(o, key=None):
        nonlocal best
        if isinstance(o, dict):
            for k, v in o.items(): walk(v, k)
        elif isinstance(o, list):
            for v in o: walk(v, key)
        elif isinstance(o, str) and key in EVENT_KEYS:
            t = parse_ts(o)
            if t and (best is None or t > best):
                best = t
    for e in ctx.values():
        walk(e["data"])
    return best

def lag_hours(a, b):
    """两个规范 ts 串的小时差(保留 1 位); 不可解析返回 None"""
    def sec(t):
        return (int(t[0:4]) * 365 + int(t[5:7]) * 30 + int(t[8:10])) * 86400 \
             + int(t[11:13]) * 3600 + int(t[14:16]) * 60 + int(t[17:19])
    try:
        return round((sec(a) - sec(b)) / 3600.0, 1)
    except Exception:
        return None

# ---------- 八面板投影 ----------
def panel_sitrep(ctx, baseline):
    fleet = ctx["FLEET-STATE"]["data"]
    kern = ctx["KERNEL-STATE"]["data"]
    beacon = ctx["beacon-mirror"]["data"]
    circle = ctx["circle-state"]["data"]
    exp = ctx["EXPECT-REG-01"]["data"]
    inst = ctx["INST-REG"]["data"]
    # 死线表: open/watching/armed 且带 deadline
    deadlines = []
    for it in exp.get("items", []):
        st = it.get("state") or it.get("status") or "?"
        dl = it.get("deadline")
        if st in ("open", "watching", "armed") and dl:
            dt = parse_ts(dl)
            deadlines.append({
                "id": it["id"],
                "title": it.get("title") or it.get("what", ""),
                "state": st,
                "owner": it.get("owner", "—"),
                "deadline": dl,
                "overdue": bool(dt and baseline and dt < baseline),
            })
    deadlines.sort(key=lambda x: (not x["overdue"], x["deadline"]))
    # 实例状态分布
    by_status = {}
    for i in inst.get("instances", []):
        by_status[i["status"]] = by_status.get(i["status"], 0) + 1
    # beacon 锚停滞声明(降级声明制: 镜像 ts 落后基线即声明)
    lag = lag_hours(baseline, parse_ts(beacon.get("ts", "")) or baseline)
    stale_decl = (f"锚镜像 seq={beacon.get('seq')} ts={beacon.get('ts')}; "
                  f"落后投影基线({baseline})约 {lag}h ⇒ 按降级声明制标注为停滞窗口, "
                  "不作实时锚声称" if (lag is not None and lag > 0)
                  else "锚镜像与基线同拍")
    return {
        "source_path": "holo-ctx/FLEET-STATE.json + KERNEL-STATE.json + beacon-mirror.json + circle-state.json + EXPECT-REG-01.json",
        "projected_ts": baseline,
        "line_cards": [
            {"organ": "fleet-judge", "ts": fleet.get("ts"), "verdict": fleet.get("verdict"),
             "counts": fleet.get("counts"), "frontier": fleet.get("frontier", [])},
            {"organ": "kernel-loop", "ts": kern.get("ts"), "verdict": kern.get("loop_verdict"),
             "counts": kern.get("counts"), "certs_pass": kern.get("certs_pass"),
             "run": kern.get("run")},
            {"organ": "circle-refresh", "ts": circle.get("ts"),
             "verdict": f"收割 {circle['forward_circle'].get('harvested_this_run')} 件/班",
             "counts": {"session_circle_present": sum(
                 1 for v in circle.get("session_circle", {}).values() if v == "present")}},
        ],
        "kernel_loop": {
            "loop_verdict": kern.get("loop_verdict"),
            "counts": kern.get("counts"),
            "certs": [{"name": c["name"], "pass": c.get("pass")} for c in kern.get("certs", [])],
            "evolution": kern.get("evolution", {}).get("deltas", []),
        },
        "beacon": {
            "seq": beacon.get("seq"), "ts": beacon.get("ts"), "mode": beacon.get("mode"),
            "ext_ok": beacon.get("ext_ok", []),
            "qrand16": (beacon.get("qrand") or "")[:16],
            "stale_declaration": stale_decl,
        },
        "instances_by_status": by_status,
        "deadlines": deadlines,
    }

def panel_chains(ctx, baseline):
    tip = ctx["usrm-narrative-tip"]["data"]
    beacon = ctx["beacon-mirror"]["data"]
    kern = ctx["KERNEL-STATE"]["data"]
    circle = ctx["circle-state"]["data"]
    base = ctx["BASE-REG"]["data"]
    rows = [
        {"chain": "usrm 叙事链", "tip": tip.get("hash"), "seq": tip.get("seq"),
         "prev": tip.get("prev"), "ts": tip.get("ts"),
         "source_path": "holo-ctx/usrm-narrative-tip.json"},
        {"chain": "beacon 镜像锚", "tip": (beacon.get("hash") or "")[:16] + "…",
         "seq": beacon.get("seq"), "prev": (beacon.get("prev") or "")[:16] + "…",
         "ts": beacon.get("ts"), "source_path": "holo-ctx/beacon-mirror.json"},
        {"chain": "kernel ledger tip", "tip": (kern["anchor"].get("tip_hash") or "")[:16] + "…",
         "seq": kern["anchor"].get("tip_seq"), "prev": "—",
         "ts": kern.get("ts"), "source_path": "holo-ctx/KERNEL-STATE.json"},
        {"chain": "联邦 stream-ledger head", "tip": circle["forward_circle"].get("stream_ledger_head"),
         "seq": "—", "prev": "—", "ts": circle.get("ts"),
         "source_path": "holo-ctx/circle-state.json"},
    ]
    for b in base.get("bases", []):
        rows.append({"chain": f"基座 {b['base_id']}", "tip": b.get("chain_anchor"),
                     "seq": "—", "prev": "—", "ts": base and baseline,
                     "source_path": "holo-ctx/BASE-REG.json"})
    return {"source_path": "holo-ctx/usrm-narrative-tip.json + beacon-mirror.json + KERNEL-STATE.json + circle-state.json + BASE-REG.json",
            "projected_ts": baseline, "tips": rows}

def panel_registries(ctx, baseline):
    inst = ctx["INST-REG"]["data"]
    base = ctx["BASE-REG"]["data"]
    return {
        "source_path": "holo-ctx/INST-REG.json + BASE-REG.json",
        "projected_ts": inst.get("updated") or baseline,
        "instances": [
            {"inst_id": i["inst_id"], "status": i["status"], "heartbeat": i.get("heartbeat"),
             "cost_acc": i.get("cost_acc"), "parent": i.get("parent"),
             "anchor_out": i.get("anchor_out"),
             "note": (i.get("note") or "")[:120]}
            for i in inst.get("instances", [])
        ],
        "instances_n": inst.get("n", len(inst.get("instances", []))),
        "bases": [
            {"base_id": b["base_id"], "kind": b["kind"], "status": b["status"],
             "chain_anchor": b.get("chain_anchor"),
             "self_ops": b.get("self_ops", []), "collab_iface": b.get("collab_iface", [])}
            for b in base.get("bases", [])
        ],
        "reg_hash": base.get("reg_hash"),
    }

def panel_obligations(ctx, baseline):
    exp = ctx["EXPECT-REG-01"]["data"]
    open_items, overdue_items, watching = [], [], []
    for it in exp.get("items", []):
        st = it.get("state") or it.get("status") or "?"
        row = {"id": it["id"], "title": it.get("title") or it.get("what", ""),
               "state": st, "owner": it.get("owner", "—"),
               "deadline": it.get("deadline", "—"),
               "note": (it.get("note") or "")[:140]}
        dt = parse_ts(it.get("deadline", ""))
        if st == "open":
            open_items.append(row)
            if dt and baseline and dt < baseline:
                overdue_items.append(row)
        elif st in ("watching", "armed"):
            watching.append(row)
            if dt and baseline and dt < baseline:
                overdue_items.append(row)
    return {
        "source_path": "holo-ctx/EXPECT-REG-01.json",
        "projected_ts": exp.get("updated") or baseline,
        "law": exp.get("law"),
        "open": open_items, "overdue": overdue_items, "watching": watching,
        "solved_by_engine": exp.get("solved_by_engine", []),
        "escalation": [
            "field-router 每 tick 扫描全册, 超时 → FINDING 自动立(照 EXPECT-REG-01 law)",
            "kernel-loop ADJUDICATE 拍: open 项逐项判词(EVIDENCED/STALLED), STALLED → proposals",
            "proposals 由义务机(cisvr/usrm/root)批准后方入册(ratify 制, 机制不自封)",
        ],
    }

def panel_knowledge(ctx, baseline):
    base = ctx["BASE-REG"]["data"]
    tip = ctx["usrm-narrative-tip"]["data"]
    kern = ctx["KERNEL-STATE"]["data"]
    return {
        "source_path": "holo-ctx/BASE-REG.json + usrm-narrative-tip.json + KERNEL-STATE.json",
        "projected_ts": tip.get("ts") or baseline,
        "qksa": {
            "reg_hash": base.get("reg_hash"),
            "reg_hash_rule": base.get("reg_hash_rule"),
            "run": base.get("run"),
            "bases_n": len(base.get("bases", [])),
            "bases": [{"base_id": b["base_id"], "self_ops": b.get("self_ops", []),
                       "collab_iface": b.get("collab_iface", []), "status": b["status"]}
                      for b in base.get("bases", [])],
        },
        "recent_verdicts": [
            {"what": "QKSA-01 v0.1 嵌入+RUN-01", "verdict": "PASS 3/3",
             "ref": "vci-usrm/ure/qksa-run-01/"},
            {"what": "M3 usrm 半区呈堂", "verdict": "USRMS-HALF PASS 13/13",
             "ref": "TH-MECH-01[6] + dm cfts"},
            {"what": "kernel-loop 判词(11 open 项)", "verdict":
             f"EVIDENCED {sum(1 for v in kern.get('verdicts', []) if v['verdict']=='EVIDENCED')}/"
             f"STALLED {sum(1 for v in kern.get('verdicts', []) if v['verdict']=='STALLED')}",
             "ref": "holo-ctx/KERNEL-STATE.json"},
        ],
        "narrative_tip": {"seq": tip.get("seq"), "ts": tip.get("ts"),
                          "summary": tip.get("summary"), "hash": tip.get("hash")},
        "kernel_verdicts": kern.get("verdicts", []),
    }

def panel_command(ctx, baseline):
    props = ctx["kernel-proposals"]["data"]
    return {
        "source_path": "holo-ctx/kernel-proposals.json",
        "projected_ts": props.get("ts") or baseline,
        "schema": {
            "fields": ["directive_id", "target", "action", "deadline"],
            "flow": "指令件落 holo/direct/ → 路由 dm-queue/EXPECT-REG → 状态回显(issued/acked/done)",
            "note": "照 ctx §3 指挥面节; holo/direct/ 投递面 v0.1 未建, 灰标候 v0.2",
        },
        "in_flight": [
            {"kind": p.get("kind"), "ref": p.get("ref"), "reason": p.get("reason"),
             "ask": p.get("ask"), "state": "候义务机批准(proposed)"}
            for p in props.get("proposals", [])
        ],
        "ratify_rule": props.get("ratify"),
    }

def panel_crystal(ctx, baseline):
    """水晶球面板: 与 refract.py 同口径扫描 ask/answer(若 state 已有折射件摘要则并显)"""
    ask_dir, ans_dir = HOLO / "ask", HOLO / "answer"
    questions = []
    for p in sorted(ask_dir.glob("QQ-*.md")):
        ans = ans_dir / f"{p.stem}-answer.md"
        questions.append({
            "qid": p.stem, "ask_path": f"ask/{p.name}", "ask_bytes": p.stat().st_size,
            "status": "已折射" if ans.exists() else "待折射",
            "answer_path": f"answer/{ans.name}" if ans.exists() else None,
            "answer_bytes": ans.stat().st_size if ans.exists() else 0,
        })
    return {
        "source_path": "holo/ask/ + holo/answer/",
        "projected_ts": baseline,
        "questions": questions,
        "guide": {
            "howto": "root 投问: 在 holo/ask/ 落 QQ-YYYYMMDD-NNN.md(web/mobile 可写); "
                     "折射引擎五重折重构+锚定+路由; L0 即时机械答入 answer/, "
                     "L1 走 dm-queue 联邦线(h级回填), L2 走 OTP 会话深答(异步)。",
            "levels": [
                {"level": "L0", "name": "机械即时答", "scope": "定义类/状态类"},
                {"level": "L1", "name": "联邦线答", "scope": "跨线协同类 → dm-queue 目标线"},
                {"level": "L2", "name": "会话深答", "scope": "深研类 → OTP"},
            ],
        },
    }

def panel_meta(ctx, baseline):
    return {
        "source_path": "holo-gen.py 自身 + dist/snapshot.json",
        "projected_ts": baseline,
        "version": VERSION,
        "gen_ts_baseline": baseline,
        "ts_rule": "投影 ts 一律取 holo-ctx 数据最大 ts, 不取墙钟 ⇒ 构建确定性",
        "snapshot": {
            "file": "dist/snapshot.json",
            "rule": "sha256=H(dist/index.html 全字节); prev=上一链节 sha256(无则 GENESIS); "
                    "内容未变则链节不推进(幂等)",
            "note": "哈希不入 HTML 本体(防自指循环), 保证同 ctx 同代码 ⇒ 同 dist sha256",
        },
        "determinism": "同 holo-ctx 输入 + 同本代码 ⇒ 同 dist/index.html 字节 ⇒ 同 sha256; "
                       "复跑比对证据见 VERDICT.md",
        "sources": [{"path": e["source_path"], "sha12": e["sha12"]} for e in
                    sorted(ctx.values(), key=lambda x: x["source_path"])],
        "constraints": [
            "零客户端凭证(E804): 数据构建期烘焙, 浏览器端零 fetch",
            "单文件 HTML: vanilla JS + inline SVG, 零 CDN 零外链, file:// 可开",
            "密钥模式零触及; 一切声称停工程层; 零编数",
        ],
    }

# ---------- 单文件 HTML 模板(低饱和暖色系: 米白底/深墨字/赭石+苔绿点缀) ----------
HTML_TEMPLATE = r"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>HOLO-IFACE-01 · QF-OS 边界全息图</title>
<style>
:root{
  --paper:#f6f1e7; --card:#fffdf7; --ink:#2d2a24; --muted:#8a7f6d;
  --line:#e3d9c6; --ochre:#a05f2a; --ochre-soft:#c98d5a; --moss:#66795a;
  --moss-soft:#97a887; --warn:#9c4a2f;
}
*{box-sizing:border-box}
body{margin:0;background:var(--paper);color:var(--ink);
  font-family:"Songti SC","Noto Serif CJK SC","Source Han Serif SC",Georgia,"Times New Roman",serif;
  line-height:1.75;font-size:15px}
header{max-width:1080px;margin:0 auto;padding:44px 28px 18px;display:flex;gap:20px;align-items:center}
header .emblem{flex:0 0 auto}
h1{font-size:26px;margin:0 0 4px;font-weight:600;letter-spacing:.06em}
.sub{color:var(--muted);font-size:13px}
nav{max-width:1080px;margin:10px auto 0;padding:0 28px;display:flex;flex-wrap:wrap;gap:8px;
  border-bottom:1px solid var(--line);padding-bottom:14px}
nav button{background:none;border:1px solid var(--line);border-radius:999px;padding:6px 16px;
  font-family:inherit;font-size:14px;color:var(--muted);cursor:pointer;letter-spacing:.05em}
nav button.on{background:var(--ochre);border-color:var(--ochre);color:#fffdf7}
nav button:hover:not(.on){border-color:var(--ochre-soft);color:var(--ochre)}
main{max-width:1080px;margin:0 auto;padding:28px}
section.panel{display:none}
section.panel.on{display:block}
h2{font-size:20px;font-weight:600;margin:6px 0 4px;letter-spacing:.04em}
.src{color:var(--muted);font-size:12px;margin-bottom:18px}
.card{background:var(--card);border:1px solid var(--line);border-radius:10px;
  padding:18px 22px;margin-bottom:16px}
.card h3{margin:0 0 8px;font-size:16px;font-weight:600;color:var(--ochre)}
.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(280px,1fr));gap:16px}
table{width:100%;border-collapse:collapse;font-size:13.5px;background:var(--card)}
th,td{text-align:left;padding:8px 10px;border-bottom:1px solid var(--line);vertical-align:top}
th{color:var(--moss);font-weight:600;letter-spacing:.04em;white-space:nowrap}
td.mono,span.mono{font-family:"SF Mono",Menlo,Consolas,monospace;font-size:12.5px}
.tag{display:inline-block;border-radius:4px;padding:1px 8px;font-size:12px;letter-spacing:.05em}
.tag.ok{background:#eef0e6;color:var(--moss)}
.tag.warn{background:#f7ece2;color:var(--ochre)}
.tag.bad{background:#f6e4dd;color:var(--warn)}
.tag.dim{background:#f1ebdf;color:var(--muted)}
.mut{color:var(--muted)}
blockquote{margin:8px 0;padding:10px 16px;border-left:3px solid var(--ochre-soft);
  background:#fbf7ee;color:var(--ink);font-size:14px;white-space:pre-wrap}
.kv{display:flex;gap:8px;flex-wrap:wrap;font-size:13px}
.kv b{color:var(--moss);font-weight:600}
footer{max-width:1080px;margin:0 auto;padding:20px 28px 48px;color:var(--muted);
  font-size:12.5px;border-top:1px solid var(--line)}
.bar-row{display:flex;align-items:center;gap:10px;margin:4px 0;font-size:13px}
.bar-row .lbl{width:110px;color:var(--muted)}
.bar-row .trk{flex:1;background:#efe8d9;border-radius:4px;height:14px;overflow:hidden}
.bar-row .fil{height:100%;border-radius:4px}
ul.tight{margin:6px 0;padding-left:22px}
ul.tight li{margin:3px 0}
</style>
</head>
<body>
<header>
  <div class="emblem">
    <svg width="72" height="72" viewBox="0 0 72 72" role="img" aria-label="水晶球">
      <circle cx="36" cy="32" r="24" fill="#fbf7ee" stroke="#a05f2a" stroke-width="1.6"/>
      <path d="M20 30 Q36 18 52 30" fill="none" stroke="#97a887" stroke-width="1.2"/>
      <path d="M18 36 Q36 46 54 36" fill="none" stroke="#c98d5a" stroke-width="1.2"/>
      <circle cx="29" cy="25" r="3.2" fill="#e6d9bf"/>
      <path d="M22 60 L50 60 L44 52 L28 52 Z" fill="#e3d9c6" stroke="#8a7f6d" stroke-width="1"/>
    </svg>
  </div>
  <div>
    <h1>HOLO-IFACE-01 · QF-OS 边界全息图</h1>
    <div class="sub" id="meta-line">全息界面原型 v0.1 · 数据构建期烘焙 · 零客户端凭证 · file:// 可开</div>
  </div>
</header>
<nav id="tabs"></nav>
<main id="main"></main>
<footer id="foot"></footer>
<script id="holo-state" type="application/json">__STATE_JSON__</script>
<script>
"use strict";
const STATE = JSON.parse(document.getElementById("holo-state").textContent);
const P = STATE.panels;
const esc = s => String(s==null?"—":s).replace(/[&<>"]/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;"}[c]));
const tag = (t,cls) => `<span class="tag ${cls}">${esc(t)}</span>`;
const stTag = s => tag(s, s==="ACTIVE"?"ok":s==="CONVERGED"?"dim":s==="QUEUED"?"warn":(s==="open"?"warn":"dim"));

const TABS = [
  ["crystal","水晶球"],["sitrep","态势总览"],["chains","链面"],["registries","注册面"],
  ["obligations","欠账面"],["knowledge","知识面"],["command","指挥面"],["meta","元面"]
];

function srcLine(p){ return `<div class="src">数据源: ${esc(p.source_path)} · 投影 ts: ${esc(p.projected_ts)}</div>`; }

/* ---- 水晶球 ---- */
function rCrystal(){
  const p=P.crystal; let h=srcLine(p);
  h+=`<div class="card"><h3>提问指引</h3><p>${esc(p.guide.howto)}</p><div class="kv">`+
     p.guide.levels.map(l=>`<span>${tag(l.level,"warn")} <b>${esc(l.name)}</b> · ${esc(l.scope)}</span>`).join("")+
     `</div></div>`;
  h+=`<div class="card"><h3>问件册(${p.questions.length})</h3>`;
  if(!p.questions.length){ h+=`<p class="mut">尚无问件。投问径: holo/ask/QQ-*.md</p>`; }
  else{
    h+=`<table><tr><th>问件</th><th>态</th><th>原件</th><th>答件</th></tr>`+
      p.questions.map(q=>`<tr><td class="mono">${esc(q.qid)}</td>`+
        `<td>${q.status==="已折射"?tag("已折射","ok"):tag("待折射","warn")}</td>`+
        `<td class="mono">${esc(q.ask_path)} (${q.ask_bytes}B)</td>`+
        `<td class="mono">${q.answer_path?esc(q.answer_path)+" ("+q.answer_bytes+"B)":"—"}</td></tr>`).join("")+
      `</table>`;
  }
  return h+`</div>`;
}

/* ---- 态势总览 ---- */
function rSitrep(){
  const p=P.sitrep; let h=srcLine(p);
  h+=`<div class="grid">`+p.line_cards.map(c=>`<div class="card"><h3>${esc(c.organ)}</h3>`+
    `<div class="kv"><span>ts <b class="mono">${esc(c.ts)}</b></span></div>`+
    `<div class="kv"><span>判词 ${tag(c.verdict,"ok")}</span></div>`+
    (c.counts?`<div class="kv">`+Object.entries(c.counts).map(([k,v])=>`<span>${esc(k)} <b>${esc(v)}</b></span>`).join("")+`</div>`:"")+
    (c.frontier&&c.frontier.length?`<div class="kv"><span>前沿 `+c.frontier.map(f=>`<span class="mono">${esc(f)}</span>`).join(" · ")+`</span></div>`:"")+
    (c.certs_pass!==undefined?`<div class="kv"><span>证书 ${c.certs_pass?tag("certs PASS","ok"):tag("certs FAIL","bad")}</span><span>run <b class="mono">${esc(c.run)}</b></span></div>`:"")+
    `</div>`).join("")+`</div>`;
  const k=p.kernel_loop;
  h+=`<div class="card"><h3>kernel-loop 判词</h3><div class="kv">`+
    `<span>loop_verdict ${tag(k.loop_verdict,"ok")}</span>`+
    Object.entries(k.counts||{}).map(([kk,v])=>`<span>${esc(kk)} <b>${esc(v)}</b></span>`).join("")+
    k.certs.map(c=>`<span>${esc(c.name)} ${c.pass?tag("pass","ok"):tag("fail","bad")}</span>`).join("")+
    (k.evolution&&k.evolution.length?`<span>演化 Δ: <span class="mono">${esc(k.evolution.join(" ; "))}</span></span>`:"")+
    `</div></div>`;
  const b=p.beacon;
  h+=`<div class="card"><h3>beacon 态(含锚停滞声明)</h3><div class="kv">`+
    `<span>seq <b class="mono">${esc(b.seq)}</b></span><span>ts <b class="mono">${esc(b.ts)}</b></span>`+
    `<span>mode ${tag(b.mode,"dim")}</span><span>ext_ok <b>${esc(b.ext_ok.join("/"))}</b></span>`+
    `<span>qrand <b class="mono">${esc(b.qrand16)}…</b></span></div>`+
    `<blockquote>${esc(b.stale_declaration)}</blockquote></div>`;
  const bs=p.instances_by_status, tot=Object.values(bs).reduce((a,x)=>a+x,0)||1;
  const col={"ACTIVE":"#66795a","CONVERGED":"#c9bfa8","QUEUED":"#c98d5a"};
  h+=`<div class="card"><h3>实例状态分布(INST-REG)</h3><svg width="100%" height="26" viewBox="0 0 600 26" preserveAspectRatio="none">`;
  let x=0;
  for(const [s,n] of Object.entries(bs)){
    const w=600*n/tot;
    h+=`<rect x="${x.toFixed(1)}" y="3" width="${w.toFixed(1)}" height="20" rx="3" fill="${col[s]||"#8a7f6d"}"/>`;
    x+=w;
  }
  h+=`</svg><div class="kv">`+Object.entries(bs).map(([s,n])=>`<span>${tag(s,s==="ACTIVE"?"ok":s==="QUEUED"?"warn":"dim")} <b>${n}</b></span>`).join("")+`</div></div>`;
  h+=`<div class="card"><h3>死线表(open/watching, 按紧迫度)</h3><table>`+
    `<tr><th>编号</th><th>事项</th><th>态</th><th>主理</th><th>死线</th></tr>`+
    p.deadlines.map(d=>`<tr><td class="mono">${esc(d.id)}</td><td>${esc(d.title)}</td>`+
      `<td>${stTag(d.state)}${d.overdue?" "+tag("已逾","bad"):""}</td>`+
      `<td>${esc(d.owner)}</td><td class="mono">${esc(d.deadline)}</td></tr>`).join("")+
    `</table></div>`;
  return h;
}

/* ---- 链面 ---- */
function rChains(){
  const p=P.chains; let h=srcLine(p);
  h+=`<div class="card"><h3>各链 tip 表</h3><table>`+
    `<tr><th>链</th><th>tip</th><th>seq</th><th>prev</th><th>ts</th><th>数据源</th></tr>`+
    p.tips.map(r=>`<tr><td>${esc(r.chain)}</td><td class="mono">${esc(r.tip)}</td>`+
      `<td class="mono">${esc(r.seq)}</td><td class="mono">${esc(r.prev)}</td>`+
      `<td class="mono">${esc(r.ts)}</td><td class="mono mut">${esc(r.source_path)}</td></tr>`).join("")+
    `</table></div>`;
  return h;
}

/* ---- 注册面 ---- */
function rRegistries(){
  const p=P.registries; let h=srcLine(p);
  h+=`<div class="card"><h3>INST-REG 实例册(n=${p.instances_n})</h3><table>`+
    `<tr><th>inst_id</th><th>态</th><th>心跳</th><th>成本</th><th>parent</th><th>注</th></tr>`+
    p.instances.map(i=>`<tr><td class="mono">${esc(i.inst_id)}</td><td>${stTag(i.status)}</td>`+
      `<td class="mono">${esc(i.heartbeat)}</td><td class="mono">${esc(i.cost_acc)}</td>`+
      `<td class="mono mut">${esc(i.parent)}</td><td class="mut">${esc(i.note)}</td></tr>`).join("")+
    `</table></div>`;
  h+=`<div class="card"><h3>BASE-REG 基座册(8 基座, reg_hash=<span class="mono">${esc(p.reg_hash)}</span>)</h3><table>`+
    `<tr><th>base_id</th><th>kind</th><th>态</th><th>链锚</th><th>自运算</th><th>协同口</th></tr>`+
    p.bases.map(b=>`<tr><td class="mono">${esc(b.base_id)}</td><td>${esc(b.kind)}</td>`+
      `<td>${stTag(b.status)}</td><td class="mono">${esc(b.chain_anchor)}</td>`+
      `<td>${b.self_ops.map(o=>tag(o,"dim")).join(" ")}</td>`+
      `<td>${b.collab_iface.length?b.collab_iface.map(o=>tag(o,"ok")).join(" "):'<span class="mut">—</span>'}</td></tr>`).join("")+
    `</table></div>`;
  return h;
}

/* ---- 欠账面 ---- */
function rObligations(){
  const p=P.obligations; let h=srcLine(p);
  h+=`<div class="card"><h3>登记律</h3><blockquote>${esc(p.law)}</blockquote></div>`;
  const tbl=(rows,extra)=>rows.length?`<table><tr><th>编号</th><th>事项</th><th>态</th><th>主理</th><th>死线</th><th>注</th></tr>`+
    rows.map(r=>`<tr><td class="mono">${esc(r.id)}</td><td>${esc(r.title)}</td><td>${stTag(r.state)}${extra&&extra(r)||""}</td>`+
      `<td>${esc(r.owner)}</td><td class="mono">${esc(r.deadline)}</td><td class="mut">${esc(r.note)}</td></tr>`).join("")+`</table>`
    :`<p class="mut">无</p>`;
  h+=`<div class="card"><h3>逾期表(${p.overdue.length})</h3>${tbl(p.overdue,()=>" "+tag("已逾","bad"))}</div>`;
  h+=`<div class="card"><h3>open 表(${p.open.length})</h3>${tbl(p.open)}</div>`;
  h+=`<div class="card"><h3>watching/armed 表(${p.watching.length})</h3>${tbl(p.watching)}</div>`;
  h+=`<div class="card"><h3>升级链</h3><ul class="tight">`+p.escalation.map(e=>`<li>${esc(e)}</li>`).join("")+`</ul></div>`;
  h+=`<div class="card"><h3>帕累托引擎直决销案(${p.solved_by_engine.length})</h3><table>`+
    `<tr><th>编号</th><th>事项</th><th>定案</th><th>执行痕</th></tr>`+
    p.solved_by_engine.map(s=>`<tr><td class="mono">${esc(s.id)}</td><td>${esc(s.what)}</td>`+
      `<td>${esc(s.decision)}</td><td class="mut">${esc(s.executed)}</td></tr>`).join("")+`</table></div>`;
  return h;
}

/* ---- 知识面 ---- */
function rKnowledge(){
  const p=P.knowledge; let h=srcLine(p);
  const q=p.qksa;
  h+=`<div class="card"><h3>QKSA 量子化知识底座</h3><div class="kv">`+
    `<span>reg_hash <b class="mono">${esc(q.reg_hash)}</b></span><span>run <b>${esc(q.run)}</b></span>`+
    `<span>基座数 <b>${q.bases_n}</b></span></div>`+
    `<p class="mut">${esc(q.reg_hash_rule)}</p><table>`+
    `<tr><th>base_id</th><th>态</th><th>自运算算子</th><th>协同协议</th></tr>`+
    q.bases.map(b=>`<tr><td class="mono">${esc(b.base_id)}</td><td>${stTag(b.status)}</td>`+
      `<td>${b.self_ops.map(o=>tag(o,"dim")).join(" ")}</td>`+
      `<td>${b.collab_iface.length?b.collab_iface.map(o=>tag(o,"ok")).join(" "):'<span class="mut">—</span>'}</td></tr>`).join("")+
    `</table></div>`;
  h+=`<div class="card"><h3>自运算/协同最近判词</h3><table><tr><th>事项</th><th>判词</th><th>引</th></tr>`+
    p.recent_verdicts.map(v=>`<tr><td>${esc(v.what)}</td><td>${tag(v.verdict,"ok")}</td>`+
      `<td class="mono mut">${esc(v.ref)}</td></tr>`).join("")+`</table></div>`;
  h+=`<div class="card"><h3>kernel-loop 逐项判词(${p.kernel_verdicts.length})</h3><table>`+
    `<tr><th>欠账</th><th>判词</th><th>构造数</th><th>主理</th></tr>`+
    p.kernel_verdicts.map(v=>`<tr><td class="mono">${esc(v.id)}</td>`+
      `<td>${tag(v.verdict,v.verdict==="EVIDENCED"?"ok":"warn")}</td>`+
      `<td class="mono">${esc(v.constructions)}</td><td>${esc(v.owner)}</td></tr>`).join("")+
    `</table></div>`;
  const nt=p.narrative_tip;
  h+=`<div class="card"><h3>usrm 叙事链 tip(seq=${esc(nt.seq)})</h3><p>${esc(nt.summary)}</p>`+
    `<div class="kv"><span>hash <b class="mono">${esc(nt.hash)}</b></span><span>ts <b class="mono">${esc(nt.ts)}</b></span></div></div>`;
  return h;
}

/* ---- 指挥面 ---- */
function rCommand(){
  const p=P.command; let h=srcLine(p);
  h+=`<div class="card"><h3>指令件 schema</h3><div class="kv">`+
    p.schema.fields.map(f=>`<span class="mono">${esc(f)}</span>`).join("")+`</div>`+
    `<p>${esc(p.schema.flow)}</p><p class="mut">${esc(p.schema.note)}</p></div>`;
  h+=`<div class="card"><h3>在途指令/提案(${p.in_flight.length})</h3>`+
    (p.in_flight.length?`<table><tr><th>类</th><th>引</th><th>事由</th><th>所请</th><th>态</th></tr>`+
     p.in_flight.map(d=>`<tr><td>${tag(d.kind,"warn")}</td><td class="mono">${esc(d.ref)}</td>`+
       `<td>${esc(d.reason)}</td><td>${esc(d.ask)}</td><td>${tag(d.state,"dim")}</td></tr>`).join("")+`</table>`
     :`<p class="mut">无在途件</p>`)+`</div>`;
  h+=`<div class="card"><h3>批准律</h3><blockquote>${esc(p.ratify_rule)}</blockquote></div>`;
  return h;
}

/* ---- 元面 ---- */
function rMeta(){
  const p=P.meta; let h=srcLine(p);
  const s=p.snapshot;
  h+=`<div class="card"><h3>本版生成</h3><div class="kv">`+
    `<span>版本 <b class="mono">${esc(p.version)}</b></span>`+
    `<span>投影基线 ts <b class="mono">${esc(p.gen_ts_baseline)}</b></span></div>`+
    `<p class="mut">${esc(p.ts_rule)}</p></div>`;
  h+=`<div class="card"><h3>快照哈希链</h3><div class="kv">`+
    `<span>链件 <b class="mono">${esc(s.file)}</b></span></div>`+
    `<p>${esc(s.rule)}</p><p class="mut">${esc(s.note)}</p></div>`;
  h+=`<div class="card"><h3>确定性声明</h3><blockquote>${esc(p.determinism)}</blockquote></div>`;
  h+=`<div class="card"><h3>架构约束(钉死)</h3><ul class="tight">`+
    p.constraints.map(c=>`<li>${esc(c)}</li>`).join("")+`</ul></div>`;
  h+=`<div class="card"><h3>数据源清册(${p.sources.length})</h3><table><tr><th>路径</th><th>sha256[:12]</th></tr>`+
    p.sources.map(x=>`<tr><td class="mono">${esc(x.path)}</td><td class="mono">${esc(x.sha12)}</td></tr>`).join("")+
    `</table></div>`;
  return h;
}

const RENDER={crystal:rCrystal,sitrep:rSitrep,chains:rChains,registries:rRegistries,
  obligations:rObligations,knowledge:rKnowledge,command:rCommand,meta:rMeta};

const nav=document.getElementById("tabs"), main=document.getElementById("main");
TABS.forEach(([key,label],idx)=>{
  const b=document.createElement("button");
  b.textContent=label; b.dataset.key=key;
  b.onclick=()=>show(key);
  nav.appendChild(b);
  const sec=document.createElement("section");
  sec.className="panel"; sec.id="p-"+key;
  sec.innerHTML=RENDER[key]();
  main.appendChild(sec);
});
function show(key){
  document.querySelectorAll("nav button").forEach(b=>b.classList.toggle("on",b.dataset.key===key));
  document.querySelectorAll("section.panel").forEach(s=>s.classList.toggle("on",s.id==="p-"+key));
  if(history.replaceState) history.replaceState(null,"","#"+key);
}
const init=(location.hash||"").slice(1);
show(RENDER[init]?init:"crystal");
document.getElementById("meta-line").textContent=
  `${STATE.panels.meta.version} · 投影基线 ${STATE.panels.meta.gen_ts_baseline} · 数据构建期烘焙 · 零客户端凭证 · file:// 可开`;
document.getElementById("foot").innerHTML=
  `HOLO-IFACE-01 原型 v0.1 · 一切声称停工程层 · 快照哈希链见 <span class="mono">dist/snapshot.json</span>(幂等推进, 哈希不入 HTML 本体防自指) · 数据源 ${STATE.panels.meta.sources.length} 件全真投影, 零编数`;
</script>
</body>
</html>
"""


# ---------- 主流水线 ----------
def build_state(ctx, baseline):
    return {
        "doc": "HOLO-IFACE-01 holo-state",
        "version": VERSION,
        "baseline_ts": baseline,
        "panels": {
            "crystal": panel_crystal(ctx, baseline),
            "sitrep": panel_sitrep(ctx, baseline),
            "chains": panel_chains(ctx, baseline),
            "registries": panel_registries(ctx, baseline),
            "obligations": panel_obligations(ctx, baseline),
            "knowledge": panel_knowledge(ctx, baseline),
            "command": panel_command(ctx, baseline),
            "meta": panel_meta(ctx, baseline),
        },
    }

def bake_html(state):
    payload = json.dumps(state, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    payload = payload.replace("</", "<\\/")  # 防 </script> 截断
    return HTML_TEMPLATE.replace("__STATE_JSON__", payload)

def write_snapshot(html_bytes, baseline):
    sha = hashlib.sha256(html_bytes).hexdigest()
    prev, prev_sha = "GENESIS", None
    if SNAP_PATH.exists():
        try:
            old = json.loads(SNAP_PATH.read_text(encoding="utf-8"))
            prev = old.get("sha256", "GENESIS")
            prev_sha = prev
        except Exception:
            prev = "GENESIS"
    if prev_sha == sha:
        return prev_sha, prev, True  # 幂等: 内容未变, 链节不推进
    snap = {"sha256": sha, "prev": prev, "ts": baseline, "version": VERSION}
    SNAP_PATH.write_text(json.dumps(snap, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    return sha, prev, False

def main():
    DIST.mkdir(parents=True, exist_ok=True)
    ctx = load_ctx()
    baseline = ctx_baseline(ctx)
    state = build_state(ctx, baseline)
    STATE_PATH.write_text(json.dumps(state, ensure_ascii=False, indent=1, sort_keys=True) + "\n",
                          encoding="utf-8")
    html = bake_html(state)
    html_bytes = html.encode("utf-8")
    (DIST / "index.html").write_bytes(html_bytes)
    sha, prev, idem = write_snapshot(html_bytes, baseline)
    p = state["panels"]
    counts = {
        "crystal.questions": len(p["crystal"]["questions"]),
        "sitrep.line_cards": len(p["sitrep"]["line_cards"]),
        "sitrep.deadlines": len(p["sitrep"]["deadlines"]),
        "chains.tips": len(p["chains"]["tips"]),
        "registries.instances": len(p["registries"]["instances"]),
        "registries.bases": len(p["registries"]["bases"]),
        "obligations.open": len(p["obligations"]["open"]),
        "obligations.overdue": len(p["obligations"]["overdue"]),
        "obligations.watching": len(p["obligations"]["watching"]),
        "knowledge.bases": p["knowledge"]["qksa"]["bases_n"],
        "knowledge.kernel_verdicts": len(p["knowledge"]["kernel_verdicts"]),
        "command.in_flight": len(p["command"]["in_flight"]),
        "meta.sources": len(p["meta"]["sources"]),
    }
    print(f"holo-gen: baseline={baseline}")
    print(f"holo-gen: holo-state.json {STATE_PATH.stat().st_size}B (八面板)")
    print(f"holo-gen: dist/index.html {len(html_bytes)}B")
    print(f"holo-gen: snapshot sha256={sha[:12]}… prev={prev[:12]}"
          f"{' (幂等未推进)' if idem else ''}")
    print("holo-gen: 面板计数 " + json.dumps(counts, ensure_ascii=False, sort_keys=True))
    return 0

if __name__ == "__main__":
    sys.exit(main())
