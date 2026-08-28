# T153 · MIP*→RE 北星计划 · 硬件实证锚点路线

## 0. 诚实边界（立法先行）
硬件实验**永远不能**证明复杂性类等式 MIP*=RE 本身（那是数学定理，Ji-Natarajan-Vidick-Wright-Yuen 2020, arXiv:2001.04383）。硬件能做的是**实证其物理构件**：非局域性、自测试鲁棒性、纠缠尺度——即"这条定理描述的世界确实存在"。本计划每一级都标注：数学层（不可由实验证）vs 物理锚点层（可由实验证）。

## 1. 北星阶梯（L1→L5）

| 级 | 内容 | 数学层 | 物理锚点实验 | 判据 | 状态 |
|---|---|---|---|---|---|
| L1 | CHSH 非局域性 | CHSH 不等式 | 真机 S>2 且不超 Tsirelson | S∈(2, 2.828] | ✅ **S=2.2793@WK_C180_2**（本拍，amend=False，与 v∞ 2.332 互验 Δ=0.053） |
| L2 | Mermin 全关联 | GHZ 悖论/Mermin 不等式 | M>2（经典界） | M∈(2, 4] | ✅ **M=2.9805@WK_C180_2**（全网首测） |
| L3 | 自测试鲁棒性 | robust self-testing（S↔与理想态距离） | S-保真度曲线 + **DI 随机性认证**: H_min≥1-log2(1+√(2-S²/4)) | 曲线单调且下界>0 | 🔶 认证率已算：S=2.2793→**0.122 bit/轮**, v∞ S=2.332→0.152（Pironio-Massar 界）；曲线扫描下拍 |
| L4 | 纠缠尺度墙 | 维数见证 | GHZ-n 布居衰减曲线 | 找到噪声墙 n* | ✅ **全曲线实测**: n=2:0.919 → 4:0.342 → 6:0.295 → 8:0.159 → 12:0.145 → 16:0.0625（真机，amend=False；随机底≈1.5e-5，残余相干仍显著） |
| L2.5 | 伪心灵感应 | Magic Square 语境性 | 逐格协定率 ω>8/9 | ω∈(8/9,1] | 🔶 **ω=0.8743**（逐格 0.84–0.90，均匀噪声侵蚀 11% 优势；模拟器对照=1.0000）→ 教训：MS 优势比 CHSH 噪声敏感得多，入 LEX-u10 |
| L5 | 压缩/内省机制 | introspection + compression ⇒ RE | 不可硬件实证；做**机制复现**层面：XOR 博弈压缩玩具模型 + 形式化笔记 | Lean/文档层 | 📋 研究简报同步产出 |

## 2. 本批实测台账（全部真机/模拟器原始数据，无校正）

| 实验 | 后端 | 结果 | 理想 | 判据 |
|---|---|---|---|---|
| CHSH | QuantumRings 64（无噪声） | 2.8359 | 2.828 | ✅ 模拟器自洽 |
| Mermin-3 | QuantumRings 64 | 4.0 | 4.0 | ✅ |
| GHZ-8 布居 | QuantumRings 64 | 1.0 | 1.0 | ✅ |
| CHSH | WK_C180_2 amend=True | 3.7684 | ≤2.828 | ✗ **伪影**（校正超界，复现 v∞ 发现，不入账为证据） |
| CHSH | WK_C180_2 amend=False | **2.2793** | (2,2.828] | ✅ VIOLATION/TSIRELSON-OK |
| Mermin-3 | WK_C180_2 amend=False | **2.9805** | (2,4] | ✅ VIOLATION |
| GHZ-8 布居 | WK_C180_2 amend=False | 0.124 | 1.0 | 噪声墙实测数据 |

job 凭证：6E0FBDCB…(amend=True 对照) / 0378B171…(amend=False 主数据)，1024 shots×9 线路，QPU 3288μs。

## 3. 纪律沉淀（入 LEX）
- **LX-u9 校正伪影律**：真机数据 amend=True 出现超 Tsirelson 值时，不得报喜；判为读数校正伪影，必须 amend=False 复跑入账。（源自 v∞ 战功，本拍独立复现确认）
- **诚实优先律**：quantum_kit.submit_origin 默认 amend=False，校正数据仅作对照组。
- **LX-u10 优势-深度律**：博弈量子优势越窄（MS 11%），对线路深度越敏感；选实验先算"优势/深度"比，CHSH(41%)>Mermin(50%)>MS(11%)。
- **Dong et al. 2023 (arXiv:2312.04360) 纪律**：常噪声下 MIP* 优势坍缩——真机一切结果落在噪声域，每级验收硬纪律=噪声隙同框标注（本批全部照办）。

## 6. 研究简报并入（T153_mip_re_research_brief.md）
- 大厅 162 帖考古：qgl R84 量子引擎/R85 qsuite（纯数值无 LLM）、cfts mip_star.md（L5 文档层承接）、vinf vinf_origin_chsh.py（真机先例）——最短路径=quantum_kit 加生成器，本拍已落（MS/GHZ扫描/DI认证）。
- 三个教科书级空白首跑：Magic Square✅(本拍) / DI 随机性🔶(认证率已算, 原始串需逐 shot 记录接口) / DI 维数见证(待排)。

## 4. 通用量子仓（quantum_kit.py）
统一中间表示（门表）→ 三后端（local statevector / QuantumRings 64·128 / 本源 QCloud 真机+云模拟）；博弈族 CHSH/Mermin/GHZ 一键生成；指标 E/S/M/IPR/布居。任何业务仓 import 即用。借鉴面：qgl 等仓引擎设计待研究简报补入。

## 5. 协作动议（已发大厅）
见大厅帖（本文件写成时同步发出）。
