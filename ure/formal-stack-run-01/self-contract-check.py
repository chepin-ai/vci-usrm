#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""FORMAL-STACK-RUN-01 器四：契约-实现对位器最小原型（自指规约·对位层；缺口#7 自指实锤）
以五机制式契约表（GENEALOGY-CLOSURE-01 §2 要义，内置，字段级）对
genealogy-run-01/run.py 源码做静态对位：
  步骤A（源码写入点提取）：正则提取 run.py 中五类工件的输出写入点
    （jdump(..., "<file>") 与 record_phase("<PHASE>", ...) 调用）。
  步骤B（字段存在性核验）：逐契约字段核验「该字段确在对应工件 JSON 中产出」
    （读 genealogy-run-01 工件 JSON 验字段路径存在性）。
diff=0 → CONTRACT-PASS；任一写入点缺位或字段缺位 → CONTRACT-FAIL 并定位。
诚实档：静态对位非全语义契约【候】——只验「写入点在源码存在 ∧ 字段在工件存在」，
不验字段值语义正确性（值级一致性由器二 replay-regression 覆盖）。
确定性：本报告无 ts，全量可复算。
"""
import json, os, re, sys

BASE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(os.path.dirname(BASE), "genealogy-run-01")

def load(name):
    with open(os.path.join(SRC, name), encoding="utf-8") as f:
        return json.load(f)

def get_path(obj, path):
    """按 'a.b[].c' 路径取值；'[]' 表示对列表逐元素展开（全须存在）。"""
    parts = path.split(".")
    cur = [obj]
    for p in parts:
        nxt = []
        if p.endswith("[]"):
            key = p[:-2]
            for o in cur:
                if not isinstance(o, dict) or key not in o or not isinstance(o[key], list):
                    return False, None
                nxt.extend(o[key])
        else:
            for o in cur:
                if not isinstance(o, dict) or p not in o:
                    return False, None
                nxt.append(o[p])
        cur = nxt
    return True, cur

# ---------------- 五机制式契约表（字段级，内置） ----------------
CONTRACT = [
 {"class": "命题件", "artifact": "obligations.json",
  "write_point": r'jdump\(obligations,\s*"obligations\.json"\)',
  "fields": ["run_id", "preregistration.prediction",
              "obligations[].prop_id", "obligations[].statement",
              "obligations[].check_spec", "obligations[].deadline",
              "obligations[].anchor.qrand_seq", "obligations[].anchor.stale",
              "obligations[].status", "obligations[].verdict_ref",
              "closure.verdict_hash"]},
 {"class": "构造件", "artifact": "evidence-obl1.json",
  "write_point": r'jdump\(construct_obl1\(narr\),\s*"evidence-obl1\.json"\)',
  "fields": ["prop_id", "construction", "entries[].seq", "entries[].stored",
              "entries[].recomputed", "entries[].match", "n_checked", "all_match",
              "anchor.qrand_seq"]},
 {"class": "构造件", "artifact": "evidence-obl2.json",
  "write_point": r'jdump\(construct_obl2\(inst\),\s*"evidence-obl2\.json"\)',
  "fields": ["prop_id", "construction", "n_instances", "dup_inst_ids",
              "unique_ok", "dim_rows[].inst_id", "dim_rows[].ok", "dim_ok",
              "anchor.qrand_seq"]},
 {"class": "构造件", "artifact": "evidence-obl3.json",
  "write_point": r'jdump\(construct_obl3\(beac\),\s*"evidence-obl3\.json"\)',
  "fields": ["prop_id", "construction", "stored_qrand", "expected_qrand",
              "qrand_match", "stored_seq", "seq_match", "stale_decl",
              "anchor.qrand_seq"]},
 {"class": "证书件", "artifact": "certificates.json",
  "write_point": r'jdump\(out,\s*"certificates\.json"\)',
  "fields": ["run_id", "challenge_seed", "certificates[].prop_id",
              "certificates[].evidence_file", "certificates[].result",
              "certificates[].checks", "certificates[].recalc",
              "anchor.qrand_seq"]},
 {"class": "判词件", "artifact": "verdict.json",
  "write_point": r'jdump\(verdict,\s*"verdict\.json"\)',
  "fields": ["run_id", "schema", "注册编号", "预测", "实验指针.evidence",
              "实验指针.certificates", "实验指针.anchor.qrand_seq",
              "结果", "状态", "诚实档", "verdict_hash",
              "signatures.threshold", "signatures.threshold_met"]},
 {"class": "锚件", "artifact": "transcript.json",
  "write_point": r'jdump\(doc,\s*"transcript\.json"\)',
  "fields": ["run_id", "schema", "hash_rule", "anchor.qrand_seq", "anchor.stale",
              "entries[].phase", "entries[].actor_machine", "entries[].prev",
              "entries[].hash", "entries[].anchor.qrand_seq",
              "total.phases", "total.cost_acc"]},
]

PHASES = ["PI", "C", "V", "J", "Z3", "A"]  # 五机链相位写入点（record_phase）

def main():
    with open(os.path.join(SRC, "run.py"), encoding="utf-8") as f:
        source = f.read()

    rows, n_diff = [], 0
    # 步骤A：源码写入点提取
    for spec in CONTRACT:
        wp_found = re.search(spec["write_point"], source) is not None
        rows.append({"kind": "write_point", "class": spec["class"],
                     "artifact": spec["artifact"], "pattern": spec["write_point"],
                     "result": "PASS" if wp_found else "FAIL"})
        if not wp_found:
            n_diff += 1
    for ph in PHASES:
        found = re.search(r'record_phase\("%s",' % ph, source) is not None
        rows.append({"kind": "phase_write_point", "class": "锚件",
                     "artifact": "transcript.json", "pattern": f'record_phase("{ph}", ...)',
                     "result": "PASS" if found else "FAIL"})
        if not found:
            n_diff += 1

    # 步骤B：字段存在性核验（读工件 JSON）
    n_fields = 0
    for spec in CONTRACT:
        obj = load(spec["artifact"])
        for fp in spec["fields"]:
            n_fields += 1
            ok, _ = get_path(obj, fp)
            rows.append({"kind": "field", "class": spec["class"],
                         "artifact": spec["artifact"], "field": fp,
                         "result": "PASS" if ok else "FAIL"})
            if not ok:
                n_diff += 1

    fails = [r for r in rows if r["result"] == "FAIL"]
    verdict = "CONTRACT-PASS" if n_diff == 0 else "CONTRACT-FAIL"
    report = {
     "run_id": "FORMAL-STACK-RUN-01-E1",
     "tool": "self-contract-check",
     "contract_ref": "GENEALOGY-CLOSURE-01 §2 五机制式契约（字段级内置表）",
     "target": "genealogy-run-01/run.py 源码 + 八件工件 JSON",
     "scope_decl": "静态对位非全语义契约【候】：验『源码写入点存在 ∧ 契约字段在工件 JSON 存在』；"
                   "字段值级一致性由 replay-regression 覆盖",
     "artifact_classes": len(CONTRACT),
     "write_points_checked": len(CONTRACT) + len(PHASES),
     "fields_checked": n_fields,
     "checks_total": len(rows),
     "diff": n_diff,
     "verdict": verdict,
     "fail_locations": [{"class": r["class"], "artifact": r["artifact"],
                         "item": r.get("field") or r["pattern"]} for r in fails],
     "contract_table_digest_fields_per_class": {s["class"] + "/" + s["artifact"]: len(s["fields"])
                                                for s in CONTRACT},
     "rows": rows,
     "determinism": "本报告无 ts 字段，全量可复算"}
    with open(os.path.join(BASE, "contract-report.json"), "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=1)
    print(f"[contract] {verdict}  写入点={len(CONTRACT)+len(PHASES)} 字段={n_fields} "
          f"checks={len(rows)-n_diff}/{len(rows)} PASS  diff={n_diff}"
          + (f"  FAIL@={report['fail_locations']}" if n_diff else ""))
    return 0 if n_diff == 0 else 1

if __name__ == "__main__":
    sys.exit(main())
