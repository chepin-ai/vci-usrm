#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
refract.py · HOLO-IFACE-01 水晶球折射引擎 v0.1
输入: holo/ask/QQ-*.md (root 提问原件)
处理: 五重折重构 (R1 直译照录 / R2 重整=行动词+对象 / R3 重定位语境=关键词锚定
      注册表/链/板面 / R4 重构元问题 / R5 重梳角度)
路由: L0 机械即时答(定义类/状态类) / L1 联邦线答(跨线协同类→dm-queue) / L2 会话深答(OTP)
输出: holo/answer/QQ-*-answer.md (重构全文+锚定上下文+答架+路由去向)
      并更新 holo/holo-state.json 的 crystal 面板
纪律: 零编数; 锚定只命中 holo-ctx 真数据; 时间戳一律取数据基线(确定性, 不取墙钟)
"""
import json
import re
import sys
from pathlib import Path

HOLO = Path(__file__).resolve().parent
WAVE = HOLO.parent
CTX = WAVE / "holo-ctx"
ASK_DIR = HOLO / "ask"
ANS_DIR = HOLO / "answer"
STATE_PATH = HOLO / "holo-state.json"

# ---------- 确定性时间基线: 取 holo-ctx 各源最大 ts(不取墙钟) ----------
TS_RE = re.compile(r"(\d{4}-\d{2}-\d{2})T(\d{2}):(\d{2})(?::(\d{2}))?Z")

def parse_ts(s):
    if not isinstance(s, str):
        return None
    m = TS_RE.search(s)
    if not m:
        return None
    d, hh, mm, ss = m.groups()
    return f"{d}T{hh}:{mm}:{ss or '00'}Z"

EVENT_KEYS = {"ts", "updated", "closed_ts", "solved_ts", "prev_ts"}  # 不含 deadline(未来值)

def ctx_baseline(ctx):
    """遍历 ctx 全部 JSON 的事件时间字段(EVENT_KEYS), 取最大可解析时间戳;
    deadline 属未来约定, 不入基线"""
    best = None
    def walk(o, key=None):
        nonlocal best
        if isinstance(o, dict):
            for k, v in o.items():
                walk(v, k)
        elif isinstance(o, list):
            for v in o:
                walk(v, key)
        elif isinstance(o, str) and key in EVENT_KEYS:
            t = parse_ts(o)
            if t and (best is None or t > best):
                best = t
    for d in ctx.values():
        walk(d)
    return best

def load_ctx():
    ctx = {}
    for p in sorted(CTX.glob("*.json")):
        ctx[p.name] = json.loads(p.read_text(encoding="utf-8"))
    return ctx

# ---------- 五重折 ----------
ACTION_WORDS = ["重理解", "重定位语境", "重构元问题", "重梳理角度", "重新翻译",
                "翻译", "重整", "重构", "重定位", "重梳理", "建立", "实现", "给出",
                "提供", "协同", "调整", "指挥", "创建", "设立", "回答", "展示",
                "提问", "提出", "适应", "交互", "完善", "需要"]

def fold_r1(text):
    """R1 直译照录: 原文一字不改"""
    return text.strip()

def fold_r2(text):
    """R2 重整: 抽取行动词+对象(按标点切段, 段内含行动词即取)"""
    segs = [s.strip() for s in re.split(r"[。；;，,！!？?\n]", text) if s.strip()]
    acts = []
    for seg in segs:
        for w in ACTION_WORDS:
            if w in seg:
                acts.append({"action": w, "object": seg})
                break
    seen, uniq = set(), []
    for a in acts:
        k = a["object"]
        if k not in seen:
            seen.add(k)
            uniq.append(a)
    return uniq

def build_anchor_lexicon(ctx):
    """R3 锚定词表: 全部来自 holo-ctx 真数据 + 面板/机制面词"""
    lex = []  # (keyword, kind, ref, source_path)
    inst = ctx.get("INST-REG.json", {})
    for it in inst.get("instances", []):
        iid = it["inst_id"]
        lex.append((iid, "实例", iid, "holo-ctx/INST-REG.json"))
        for tok in re.split(r"[-_]", iid):
            if len(tok) >= 4 and tok not in ("GENESIS",):
                lex.append((tok, "实例", iid, "holo-ctx/INST-REG.json"))
    base = ctx.get("BASE-REG.json", {})
    for b in base.get("bases", []):
        lex.append((b["base_id"], "基座", b["base_id"], "holo-ctx/BASE-REG.json"))
        for tok in b["base_id"].split("-"):
            if len(tok) >= 4:
                lex.append((tok, "基座", b["base_id"], "holo-ctx/BASE-REG.json"))
    exp = ctx.get("EXPECT-REG-01.json", {})
    for it in exp.get("items", []):
        lex.append((it["id"], "欠账", it["id"], "holo-ctx/EXPECT-REG-01.json"))
    board = ctx.get("board-index.json", {})
    for fn in board.get("公告板", []) + board.get("threads", []):
        stem = fn.rsplit(".md", 1)[0]
        lex.append((stem, "板面", fn, "holo-ctx/board-index.json"))
        if stem.startswith("TH-"):
            lex.append((stem, "话题", fn, "holo-ctx/board-index.json"))
    # 机制面词 → 面板/数据源(本界面自身词汇, 照录 root 令语言)
    face_words = [
        ("公告板", "板面", "board-index:公告板", "holo-ctx/board-index.json"),
        ("讨论室", "话题", "board-index:threads", "holo-ctx/board-index.json"),
        ("话题", "话题", "board-index:threads", "holo-ctx/board-index.json"),
        ("提案", "提案", "kernel-proposals", "holo-ctx/kernel-proposals.json"),
        ("义务", "欠账", "EXPECT-REG-01", "holo-ctx/EXPECT-REG-01.json"),
        ("死线", "欠账", "EXPECT-REG-01", "holo-ctx/EXPECT-REG-01.json"),
        ("态势", "面板", "sitrep", "holo-ctx/FLEET-STATE.json+KERNEL-STATE.json"),
        ("内核", "引擎", "S-KERNEL-LOOP", "holo-ctx/KERNEL-STATE.json"),
        ("kernel", "引擎", "S-KERNEL-LOOP", "holo-ctx/KERNEL-STATE.json"),
        ("链", "链", "chains", "holo-ctx/usrm-narrative-tip.json+beacon-mirror.json"),
        ("基座", "基座", "BASE-REG", "holo-ctx/BASE-REG.json"),
        ("知识", "基座", "QKSA/BASE-REG", "holo-ctx/BASE-REG.json"),
        ("界面", "本件", "HOLO-IFACE-01", "ctx-wave11-holo.md§0"),
        ("全息", "本件", "HOLO-IFACE-01", "ctx-wave11-holo.md§0"),
        ("水晶球", "本件", "HOLO-IFACE-01:crystal", "ctx-wave11-holo.md§3"),
        ("指挥", "面板", "command", "ctx-wave11-holo.md§3"),
        ("指令", "面板", "command", "ctx-wave11-holo.md§3"),
        ("QF-OS", "体", "QF-OS 五机+内核", "ctx-wave11-holo.md§1"),
        (" dashboard", "本件", "HOLO-IFACE-01", "ctx-wave11-holo.md§0"),
        ("Dashboard", "本件", "HOLO-IFACE-01", "ctx-wave11-holo.md§0"),
    ]
    lex.extend(face_words)
    # 长词优先, 避免短词抢命中
    lex.sort(key=lambda x: -len(x[0]))
    return lex

def fold_r3(text, lex, ctx):
    """R3 重定位语境: 关键词命中注册表/链/板面, 装配上下文锚"""
    hits, seen = [], set()
    low = text.lower()
    for kw, kind, ref, src in lex:
        key = (kind, ref)
        if key in seen:
            continue
        if kw.strip().lower() in low:
            seen.add(key)
            hits.append({"keyword": kw.strip(), "kind": kind, "ref": ref, "source": src})
    # 命中实例补状态(真数据回填)
    inst_by_id = {i["inst_id"]: i for i in ctx.get("INST-REG.json", {}).get("instances", [])}
    for h in hits:
        if h["kind"] == "实例" and h["ref"] in inst_by_id:
            it = inst_by_id[h["ref"]]
            h["detail"] = f"status={it['status']} heartbeat={it['heartbeat']}"
        if h["kind"] == "欠账":
            for it in ctx.get("EXPECT-REG-01.json", {}).get("items", []):
                if it["id"] == h["ref"]:
                    h["detail"] = f"state={it.get('state') or it.get('status')} deadline={it.get('deadline','—')}"
    return hits

def fold_r4(r2, r3):
    """R4 重构元问题: 升维一句(模板机械生成, 不冒充理解)"""
    objs = [a["object"] for a in r2[:3]]
    core = "；".join(objs) if objs else "(原文未析出行动段)"
    kinds = sorted({h["kind"] for h in r3})
    ctx_str = "、".join(kinds) if kinds else "无命中"
    return (f"root 真正之问≈: 如何把「{core}」落成不依赖会话端的系统件, "
            f"并使其被体的在册语境({ctx_str})接住、锚定、路由、留痕。")

def fold_r5(text, r3):
    """R5 重梳角度: 按命中面给出 2-3 个可选视角"""
    cands = []
    kinds = {h["kind"] for h in r3}
    if kinds & {"本件", "面板"}:
        cands.append(("边界全息视角", "界面=体的商结构截面: 不追问单件细节, 先看八面板投影能否接住此问"))
    if kinds & {"实例", "引擎", "基座", "欠账"}:
        cands.append(("在册义务视角", "此问落入哪个在册实例/欠账的责任面: 查 INST-REG 责任实例与 EXPECT-REG 死线"))
    if kinds & {"板面", "话题", "提案"}:
        cands.append(("联邦协同视角", "此问是否跨线: 命中板面/话题者走公告板+dm-queue 联邦路由, 不独占作答"))
    if not cands:
        cands.append(("字面应答视角", "无在册语境命中: 按 L0 字面机械答, 并建议 root 补充语境关键词"))
    cands.append(("元层视角", "把此问本身登记入 EXPECT-REG 候裁: 让义务机跟踪回答闭环, 而非依赖会话记忆"))
    return [{"angle": a, "note": n} for a, n in cands[:3]]

# ---------- 路由三档 ----------
L2_WORDS = ["证明", "深研", "研究", "为什么", "原理", "推导", "论证"]
L1_WORDS = ["协同", "共建", "共同", "全员", "所有其他方", "跨线", "@", "大家", "联邦"]
L0_DEF_WORDS = ["是什么", "何谓", "定义", "什么意思"]
L0_STATE_WORDS = ["状态", "多少", "列表", "哪些", "态势", "几件", "几个", "进展"]

def route(text):
    l2 = [w for w in L2_WORDS if w in text]
    l1 = [w for w in L1_WORDS if w in text]
    l0d = [w for w in L0_DEF_WORDS if w in text]
    l0s = [w for w in L0_STATE_WORDS if w in text]
    mentions = re.findall(r"@([A-Za-z0-9_-]+)", text)
    if l2:
        return {"level": "L2", "why": f"命中深研词: {'、'.join(l2)}",
                "target": "OTP 会话深答(异步)", "mentions": mentions}
    if l1:
        tgt = "、".join(mentions) if mentions else "联邦各线"
        return {"level": "L1", "why": f"命中跨线协同词: {'、'.join(l1)}",
                "target": f"dm-queue → {tgt}", "mentions": mentions}
    if l0d:
        return {"level": "L0", "why": f"定义类: {'、'.join(l0d)}", "target": "本机机械即时答",
                "mentions": mentions}
    return {"level": "L0", "why": ("状态类: " + "、".join(l0s)) if l0s else "默认 L0(无协同/深研词命中)",
            "target": "本机机械即时答", "mentions": mentions}

# ---------- 答件装配 ----------
def extract_body(text):
    """问体抽取: 有「」引块则以引块为问体(R2-R5/路由对象), 否则全文; R1 永远照录全文"""
    m = re.search(r"「(.+?)」", text, re.S)
    return m.group(1).strip() if m else text

def refract(qid, text, ctx, baseline):
    lex = build_anchor_lexicon(ctx)
    body = extract_body(text)
    r1 = fold_r1(text)
    r2 = fold_r2(body)
    r3 = fold_r3(body, lex, ctx)
    r4 = fold_r4(r2, r3)
    r5 = fold_r5(body, r3)
    rt = route(body)
    return {"qid": qid, "asked_baseline": baseline, "R1": r1, "R2": r2, "R3": r3,
            "R4": r4, "R5": r5, "route": rt, "answer_level_delivered": "L0"}

def render_answer(fr):
    L = []
    A = L.append
    A(f"# {fr['qid']} · 水晶球折射答件")
    A("")
    A(f"- 折射引擎: refract.py v0.1 (HOLO-IFACE-01)")
    A(f"- 投影基线 ts: {fr['asked_baseline']} (取 holo-ctx 数据最大 ts, 非墙钟, 确定性)")
    A(f"- 本件答深: **{fr['answer_level_delivered']} 机械答**(重构+锚定+答架+路由; 不冒充深答)")
    A(f"- 路由判定: **{fr['route']['level']}** — {fr['route']['why']} → {fr['route']['target']}")
    A("")
    A("## 五重折重构")
    A("")
    A("### R1 直译照录")
    A("")
    A("> " + fr["R1"].replace("\n", "\n> "))
    A("")
    A("### R2 重整(行动词+对象)")
    A("")
    if fr["R2"]:
        for a_ in fr["R2"]:
            A(f"- [{a_['action']}] {a_['object']}")
    else:
        A("- (未析出行动段)")
    A("")
    A("### R3 重定位语境(关键词锚定, 仅命中 holo-ctx 真数据)")
    A("")
    if fr["R3"]:
        A("| 命中词 | 类别 | 锚 | 数据源 | 回填 |")
        A("|---|---|---|---|---|")
        for h in fr["R3"]:
            A(f"| {h['keyword']} | {h['kind']} | {h['ref']} | {h['source']} | {h.get('detail','—')} |")
    else:
        A("- (无命中)")
    A("")
    A("### R4 重构元问题(升维一句)")
    A("")
    A(fr["R4"])
    A("")
    A("### R5 重梳角度(可选视角)")
    A("")
    for c in fr["R5"]:
        A(f"- **{c['angle']}**: {c['note']}")
    A("")
    A("## L0 机械答(答架)")
    A("")
    A("1. **界面本体已立**: 本答件即由 HOLO-IFACE-01 v0.1 水晶球三拍(ask→refract→display)产出; "
      "八面板态势见 dist/index.html(水晶球/态势总览/链面/注册面/欠账面/知识面/指挥面/元面)。")
    A("2. **设计基调照 ctx §1 五重折定案**: R1 要 dashboard → R2 会话端无关 → R3 界面=边界全息图"
      "(体的商结构截面) → R4 提问被接住/重构/路由/回答/留痕 → R5 三角合一(态势+水晶球+指挥协同)。")
    A("3. **架构约束照 ctx §3 钉死**: 零客户端凭证/单文件烘焙 HTML/双轨发布(私仓明文+公仓密封候)/"
      "L0·L1·L2 三档诚实分级/快照哈希链。")
    A("4. **深答去向**: 本问含跨线共建诉求, L0 不冒充终答; 按路由判定交联邦线接续(见下)。")
    A("")
    A("## 路由去向")
    A("")
    A(f"- 档位: **{fr['route']['level']}**({fr['route']['why']})")
    A(f"- 目标: {fr['route']['target']}")
    if fr["route"]["level"] == "L1":
        ms = fr["route"]["mentions"] or ["cisvr", "T5Q3"]
        A(f"- 建议共建线: {' + '.join(ms)}(照 root 令原文 @ 提及); "
          "投递面=dm-queue 目标线, 答深件异步回填水晶球面板")
    elif fr["route"]["level"] == "L2":
        A("- 投递面: OTP 会话深答, 答深件异步回填")
    else:
        A("- 本档即终答(机械即时答)")
    A("")
    A("## 诚实边界声明")
    A("")
    A("- 本答件五重折为机械模板重构, 不代表系统已'理解'root 意图; 深答以 L1/L2 回填件为准。")
    A("- R3 锚定仅做关键词匹配, 命中≠因果相关; 全部锚可回溯至 source 列真数据, 零编数。")
    A("- 一切声称停工程层: 本答件只声明已交付件(dist/answer/snapshot), 未交付件入灰标。")
    A("")
    return "\n".join(L)

# ---------- crystal 面板投影(ask/answer 扫描, 供 holo-gen 复用) ----------
def project_crystal():
    asks = sorted(ASK_DIR.glob("QQ-*.md"))
    answers = {p.name for p in ANS_DIR.glob("QQ-*-answer.md")}
    questions = []
    for p in asks:
        qid = p.stem
        ans = ANS_DIR / f"{qid}-answer.md"
        questions.append({
            "qid": qid,
            "ask_path": f"ask/{p.name}",
            "ask_bytes": p.stat().st_size,
            "status": "已折射" if ans.name in answers else "待折射",
            "answer_path": f"answer/{ans.name}" if ans.exists() else None,
            "answer_bytes": ans.stat().st_size if ans.exists() else 0,
        })
    return {
        "source_path": "ask/ + answer/",
        "projected_ts": None,  # 由调用方回填基线
        "questions": questions,
        "guide": {
            "howto": "root 投问: 在 holo/ask/ 落 QQ-YYYYMMDD-NNN.md(web/mobile 可写), "
                     "折射引擎五重折重构+锚定+路由, L0 即时机械答入 answer/, "
                     "L1 走 dm-queue 联邦线(h级), L2 走 OTP 会话深答(异步回填)。",
            "levels": [
                {"level": "L0", "name": "机械即时答", "scope": "定义类/状态类, 关键词锚定在册真数据"},
                {"level": "L1", "name": "联邦线答", "scope": "跨线协同类, 路由 dm-queue 目标线, h级回填"},
                {"level": "L2", "name": "会话深答", "scope": "深研类, OTP 异步, 答深件回填面板"},
            ],
        },
    }

def update_state_crystal(baseline):
    panel = project_crystal()
    panel["projected_ts"] = baseline
    state = {}
    if STATE_PATH.exists():
        state = json.loads(STATE_PATH.read_text(encoding="utf-8"))
    state.setdefault("panels", {})["crystal"] = panel
    STATE_PATH.write_text(json.dumps(state, ensure_ascii=False, indent=1, sort_keys=True) + "\n",
                          encoding="utf-8")
    return panel

def main():
    ctx = load_ctx()
    baseline = ctx_baseline(ctx)
    asks = sorted(ASK_DIR.glob("QQ-*.md"))
    if len(sys.argv) > 1:
        asks = [Path(a) for a in sys.argv[1:]]
    if not asks:
        print("refract: ask/ 下无 QQ-*.md", file=sys.stderr)
        return 1
    rc = 0
    for p in asks:
        qid = p.stem
        text = p.read_text(encoding="utf-8")
        fr = refract(qid, text, ctx, baseline)
        out = ANS_DIR / f"{qid}-answer.md"
        out.write_text(render_answer(fr), encoding="utf-8")
        print(f"refract: {qid} → {out.name} ({out.stat().st_size}B) "
              f"route={fr['route']['level']} hits={len(fr['R3'])}")
    update_state_crystal(baseline)
    print(f"refract: crystal 面板已更新 (baseline={baseline})")
    return rc

if __name__ == "__main__":
    sys.exit(main())
