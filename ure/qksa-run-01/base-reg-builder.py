#!/usr/bin/env python3
"""QKSA-RUN-01 测1：首批 8 基座登记表构建器 → BASE-REG.json

纪律：零编数。anchor 三档来源如实标注：
  - derived     : 由给定字符串 sha256(...)[:12] 现算（占位，注明 derived）
  - recorded    : 在案实录（survey §3.1 narrative_outbox.json seq192 tip）
  - computed    : qfk.chain 实际建链取链头 hash（真算）
确定性：qfk.chain.append 显式传 ts，无时间戳漂移；本脚本重跑产物逐字节一致。
"""
import hashlib
import json
import sys

sys.path.insert(0, "/mnt/agents/output/wave5")

from qfk.chain import Chain, canon  # noqa: E402

OUT = "/mnt/agents/output/wave5/qksa-run-01/BASE-REG.json"


def sha256_12(s: str) -> str:
    return hashlib.sha256(s.encode("utf-8")).hexdigest()[:12]


def qfk_chain_anchor() -> dict:
    """qfk-chain-self：用 qfk.chain 实际建 3 entry，取链头 hash[:12] 作 anchor（真算）。
    ts 显式固定 → anchor 确定性可复跑。"""
    ch = Chain()
    for i, name in enumerate(("qksa-run-01:genesis", "qksa-run-01:base-reg",
                              "qksa-run-01:self-compute")):
        ch.append("qksa-run-01", canon({"i": i, "name": name}), ts=1700000000.0 + i)
    assert ch.verify(), "qfk chain replay verify failed"
    head = ch.head.hex()
    return {"chain_anchor": head[:12], "anchor_evidence": "computed",
            "anchor_note": f"qfk.chain 实际建 3 entry 取链头（真算）, head={head[:16]}…, verify()=True"}


def build_registry() -> list[dict]:
    bases = [
        {
            "base_id": "usrm-k-ledger",
            "kind": "hash-chain-ledger",
            "chain_anchor": sha256_12("T58"),
            "anchor_evidence": "derived",
            "anchor_note": '占位=sha256("T58")[:12] 现算（derived）；正本 T58 knowledge_ledger.py 在 usrm-repo，本机无仓，未读真链头',
            "self_ops": ["VERIFY", "RESIDUAL", "CLOSURE"],
            "collab_iface": ["P1"],
            "status": "active",
        },
        {
            "base_id": "usrm-narrative",
            "kind": "narrative-chain",
            "chain_anchor": "78f5464a04a0",
            "anchor_evidence": "recorded",
            "anchor_note": "在案 tip：survey §3.1 narrative_outbox.json(ure/) seq192 tip=78f5464a04a0",
            "self_ops": ["VERIFY", "RESIDUAL", "CLOSURE"],
            "collab_iface": ["P1", "P3"],
            "status": "active",
        },
        {
            "base_id": "qgl-genealogy",
            "kind": "multi-base-group",
            "chain_anchor": sha256_12("quantum-go-knowledge-genealogy"),
            "anchor_evidence": "derived",
            "anchor_note": 'sha256("quantum-go-knowledge-genealogy")[:12] 现算；五子基座名列表照录 survey §3.2 genealogy/v1.json',
            "sub_bases": ["knowledge_graph", "cell_complex", "hyperhypergraph",
                          "iso_network", "lean"],
            "self_ops": ["VERIFY", "CLOSURE"],
            "collab_iface": ["P2", "P3"],
            "status": "active",
        },
        {
            "base_id": "ucif2-kg-lean",
            "kind": "lean-formalized-kg",
            "chain_anchor": sha256_12("ucif2-kg-lean"),
            "anchor_evidence": "derived",
            "anchor_note": '占位=sha256("ucif2-kg-lean")[:12]（derived）；正本 KnowledgeGraph/*.lean 七件在 ucif2 仓，本机无仓',
            "self_ops": ["VERIFY", "CLOSURE"],
            "collab_iface": ["P3"],
            "status": "active",
        },
        {
            "base_id": "vinf-formal-tex",
            "kind": "latex-genealogy",
            "chain_anchor": sha256_12("vinf-formal-tex"),
            "anchor_evidence": "derived",
            "anchor_note": '占位=sha256("vinf-formal-tex")[:12]（derived）；正本 形式化谱系.tex 在 vinf 仓，本机无仓',
            "self_ops": ["CLOSURE"],
            "collab_iface": ["P2"],
            "status": "active",
        },
        {
            "base_id": "cfts-alms-daemon",
            "kind": "auto-acquisition+search-daemon",
            "chain_anchor": sha256_12("cfts-alms-daemon"),
            "anchor_evidence": "derived",
            "anchor_note": '占位=sha256("cfts-alms-daemon")[:12]（derived）；正本 alms/auto_knowledge_acquisition.py + tools/auto_search_daemon.py 在 cfts 仓，本机无仓',
            "self_ops": ["RESIDUAL", "FORECAST"],
            "collab_iface": ["P1", "P2"],
            "status": "active",
        },
        {
            "base_id": "qlv-temperament",
            "kind": "quantum-encoding-genealogy",
            "chain_anchor": sha256_12("qlv-temperament"),
            "anchor_evidence": "derived",
            "anchor_note": '占位=sha256("qlv-temperament")[:12]（derived）；qlv 档已 evac 至 ci-inbox/mailbox-vault/test-evac-20260821/qlv-lab/（survey §1）',
            "self_ops": ["CLOSURE"],
            "collab_iface": [],
            "status": "EVAC-候复活",
        },
        {
            "base_id": "qfk-chain-self",
            "kind": "qfk-native",
            "self_ops": ["VERIFY", "RESIDUAL", "CLOSURE", "FORECAST"],
            "collab_iface": ["P1", "P2", "P3"],
            "status": "active",
            **qfk_chain_anchor(),  # anchor/anchor_evidence/anchor_note 真算填入
        },
    ]
    return bases


def main():
    bases = build_registry()
    assert len(bases) == 8, "登记表须恰 8 基座"
    ids = [b["base_id"] for b in bases]
    assert len(set(ids)) == 8, "base_id 重复"
    reg_hash = hashlib.sha256(canon(bases)).hexdigest()[:12]
    doc = {
        "doc": "BASE-REG",
        "run": "QKSA-RUN-01",
        "test": "base-reg-builder",
        "bases": bases,
        "reg_hash": reg_hash,
        "reg_hash_rule": "sha256(canon(bases))[:12]，canon=json sort_keys/utf-8/紧凑分隔（qfk.chain.canon 同式）",
    }
    with open(OUT, "w", encoding="utf-8") as f:
        f.write(json.dumps(doc, ensure_ascii=False, indent=2, sort_keys=True) + "\n")
    print(f"bases={len(bases)} ids={ids}")
    print(f"reg_hash={reg_hash}")
    print(f"written={OUT}")


if __name__ == "__main__":
    main()
