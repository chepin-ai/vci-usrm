#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""FORMAL-STACK-RUN-01 器一：工具链统一清单构造器（自指规约·清单层）
扫描内置工具表（≥12 件）→ toolchain-manifest.json：
  每件字段 {name, layer(search|prove|verify), scope(L0|L1|L2|L3), status(GREEN|GRAY),
            anchor, D_f(证伪条件一句), version}
  manifest_hash = sha256(canon(tools))[:16]（ts 不入哈希，可复算）
  版本谱系链：v0.1 创世（prev=null）
  gap_ledger：GRAY 件逐条列缺口与验法
诚实档：status 语义在本文件明确定义——GREEN=本沙箱可实跑或有既有 run 全绿工件在案可复算；
GRAY=仅注册/引用，本端无实测工件（缺口在案）。kernel-loop/audit-ring 为联邦器官引用，无本地锚。
"""
import json, hashlib, os, sys

BASE = os.path.dirname(os.path.abspath(__file__))
ANCHOR_LOCAL = {"qrand_seq": 61, "stale": True,
                "note": "锚停滞在案：沿用 genealogy-run-01 last-good qrand@seq61，降级声明随锚"}
ANCHOR_REF = {"ref": "联邦器官引用", "local_anchor": None,
              "note": "外部引用件，本端无本地锚，仅登记谱系"}

def sha(s): return hashlib.sha256(s.encode("utf-8")).hexdigest()
def canon(o): return json.dumps(o, ensure_ascii=False, sort_keys=True)

# ---------------- 内置工具表（13 件 ≥12） ----------------
TOOLS = [
 {"name": "z3", "version": "5.1.0", "layer": "prove", "scope": "L1", "status": "GREEN",
  "anchor": dict(ANCHOR_LOCAL),
  "D_f": "若对已知 UNSAT 小模型（如五机链 I1/I2）报 SAT，或对已知 SAT 含疵变体报 UNSAT，即证伪"},
 {"name": "cvc5", "version": "1.3.4", "layer": "prove", "scope": "L1", "status": "GRAY",
  "anchor": dict(ANCHOR_LOCAL),
  "D_f": "若同一 SMT-LIB 基准与 z3 判定系统性冲突且无法归因编码差异，即证伪"},
 {"name": "lean", "version": "场端径（未装本端）", "layer": "prove", "scope": "L2", "status": "GRAY",
  "anchor": dict(ANCHOR_LOCAL),
  "D_f": "若内核接受含 sorry/公理注入之定理为已证，即证伪"},
 {"name": "qfk-v0.2", "version": "0.2", "layer": "search", "scope": "L1", "status": "GRAY",
  "anchor": dict(ANCHOR_LOCAL),
  "D_f": "若同一查询两次返回不可复算之不一致结果且无降级声明，即证伪"},
 {"name": "ipmp", "version": "registered", "layer": "search", "scope": "L1", "status": "GRAY",
  "anchor": dict(ANCHOR_LOCAL),
  "D_f": "若声称命中之模式在目标语料中复算不存在，即证伪"},
 {"name": "pareto-verify", "version": "registered", "layer": "verify", "scope": "L2", "status": "GRAY",
  "anchor": dict(ANCHOR_LOCAL),
  "D_f": "若所报 Pareto 前沿中存在被同集另一点严格支配之解，即证伪"},
 {"name": "entangle-v2", "version": "2", "layer": "verify", "scope": "L2", "status": "GRAY",
  "anchor": dict(ANCHOR_LOCAL),
  "D_f": "若声明纠缠一致之两工件独立复算哈希不等，即证伪"},
 {"name": "t54-zkp", "version": "registered", "layer": "prove", "scope": "L3", "status": "GRAY",
  "anchor": dict(ANCHOR_LOCAL),
  "D_f": "若所出零知识证明对公开输入验证算法拒绝，即证伪"},
 {"name": "genealogy-harness", "version": "run-01-E1", "layer": "verify", "scope": "L1",
  "status": "GREEN", "anchor": dict(ANCHOR_LOCAL),
  "D_f": "若 GENEALOGY-RUN-01-E1 transcript 哈希链重放断裂或 verdict_hash 复算不符，即证伪"},
 {"name": "presync", "version": "registered", "layer": "verify", "scope": "L0", "status": "GRAY",
  "anchor": dict(ANCHOR_LOCAL),
  "D_f": "若预同步声明一致之两端上下文指纹实测不等，即证伪"},
 {"name": "otp-swm", "version": "registered", "layer": "search", "scope": "L2", "status": "GRAY",
  "anchor": dict(ANCHOR_LOCAL),
  "D_f": "若一次性 pad 被复用而检测器未报警，即证伪"},
 {"name": "kernel-loop", "version": "联邦器官引用", "layer": "verify", "scope": "L3",
  "status": "GRAY", "anchor": dict(ANCHOR_REF),
  "D_f": "若联邦器官回执与本地复算系统性冲突且无法归因版本差，即证伪"},
 {"name": "audit-ring", "version": "联邦器官引用", "layer": "verify", "scope": "L3",
  "status": "GRAY", "anchor": dict(ANCHOR_REF),
  "D_f": "若审计环签名链在公开复算下出现断环而未在案声明，即证伪"},
]

# GRAY 件缺口台账：逐条列缺口与验法
GAP_LEDGER = {
 "cvc5":   {"gap": "本沙箱未安装，无双求解器交叉判定实测", "how_to_verify": "pip/场端安装 cvc5 后对同一 SMT-LIB 基准与 z3 对拍"},
 "lean":   {"gap": "场端径：本端无 lean 工具链，五机链不变量未做交互式定理证明", "how_to_verify": "场端 lean4 工程化编码 I1/I2 并 #check 内核放行"},
 "qfk-v0.2": {"gap": "仅版本号注册，本端无可执行件与基准查询集", "how_to_verify": "取固定查询集双跑比对复算性"},
 "ipmp":   {"gap": "仅注册，无命中复算实测", "how_to_verify": "对声称命中做目标语料独立 grep/AST 复算"},
 "pareto-verify": {"gap": "仅注册，无前沿支配性机检实测", "how_to_verify": "对所报前沿逐点做 O(n²) 支配性复算"},
 "entangle-v2": {"gap": "仅注册，无纠缠工件独立哈希复算实测", "how_to_verify": "取纠缠声明工件对，独立 sha256 复算比对"},
 "t54-zkp": {"gap": "仅注册，本端无证明验证器", "how_to_verify": "以公开输入跑验证算法，核验接受/拒绝"},
 "presync": {"gap": "仅注册，无上下文指纹对拍实测", "how_to_verify": "对两端上下文各算指纹并比对"},
 "otp-swm": {"gap": "仅注册，无 pad 复用检测实测", "how_to_verify": "构造复用样本喂检测器，核验必报警"},
 "kernel-loop": {"gap": "联邦器官引用，本端无回执工件", "how_to_verify": "取联邦回执与本地复算对拍"},
 "audit-ring": {"gap": "联邦器官引用，本端无环签名工件", "how_to_verify": "公开复算环签名链连续性"},
}

def main():
    layers = sorted({t["layer"] for t in TOOLS})
    assert layers == ["prove", "search", "verify"], f"layer 取值越界: {layers}"
    assert all(t["scope"] in ("L0", "L1", "L2", "L3") for t in TOOLS)
    assert all(t["status"] in ("GREEN", "GRAY") for t in TOOLS)
    assert len(TOOLS) >= 12

    mhash = sha(canon(TOOLS))[:16]
    gray = [t["name"] for t in TOOLS if t["status"] == "GRAY"]
    gap_ledger = [{"name": n, "version": next(t["version"] for t in TOOLS if t["name"] == n),
                   **GAP_LEDGER[n]} for n in gray]

    manifest = {
     "run_id": "FORMAL-STACK-RUN-01-E1",
     "schema": "toolchain-manifest v0.1",
     "status_semantics": {
      "GREEN": "本沙箱可实跑（z3 5.1.0 已 pip 装机检）或有既有 run 全绿工件在案可复算（genealogy-harness）",
      "GRAY": "仅注册/引用，本端无实测工件；缺口逐条见 gap_ledger"},
     "layer_enum": ["search", "prove", "verify"],
     "scope_enum": ["L0", "L1", "L2", "L3"],
     "n_tools": len(TOOLS),
     "tools": TOOLS,
     "manifest_hash": mhash,
     "hash_rule": "manifest_hash=sha256(canon(tools))[:16]；canon=json.dumps(ensure_ascii=False,sort_keys=True)；无 ts，全量可复算",
     "version_lineage": [
      {"version": "v0.1", "prev": None, "manifest_hash": mhash,
       "note": "创世版：13 件登记（GREEN=2 / GRAY=11）；后续版本 prev 指向前版 manifest_hash"}],
     "gap_ledger": gap_ledger,
     "honesty": ["toy/原型档：工具表为内置登记表，GRAY 件无实测背书，缺口与验法在案",
                "锚停滞在案：沿用 last-good qrand@seq61，降级声明随锚"]}

    out = os.path.join(BASE, "toolchain-manifest.json")
    with open(out, "w", encoding="utf-8") as f:
        json.dump(manifest, f, ensure_ascii=False, indent=1)
    print(f"[manifest] tools={len(TOOLS)} GREEN={len(TOOLS)-len(gray)} GRAY={len(gray)} "
          f"manifest_hash={mhash} 谱系=v0.1(prev=null) gap_ledger={len(gap_ledger)} 条")
    return manifest

if __name__ == "__main__":
    main()
