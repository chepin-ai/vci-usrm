# ATP 工具链接入径实测报告 · atp-toolchain

- 日期：2026-08-28 · 实装进程：usrm 线 ATP 工具链实测代理
- 对象：`/mnt/agents/output/atp-lab/` 试件 1（P5 三档验证分频）
  - `p5_phase_ignition.smt2`（sha256 前缀 575be8a491394690，原文未动）
  - `p5_phase_ignition.lean`（sorry=6 骨架，未动）
  - `trial-card.md`（强度锁 none）

---

## 0. root 之问的直接回答

| 工具 | 沙箱能否装 | 证据档 |
|---|---|---|
| **z3** | **能**（`pip install z3-solver` → 5.1.0.0，已跑通原 smt2） | 已证 |
| **cvc5** | **能**（`pip install cvc5` → 1.3.4，已跑通同件直译版） | 已证 |
| **lean** | **不能**（官方径全阻，详见 §3；替代径首选场端 workflow） | 阻（实测） |

**首个真证书已产出**：z3 对原 smt2 的 C1/C2/C3/C4/C6 = **unsat**（机器检证，5/7），
其中 C1/C2/C4/C6 另由 cvc5 独立复现 unsat（双求解器互证）。C5/C7 两求解器均
unknown，如实记录、不重试、不升格。强度档仍锁 **none**（见 §4）。

---

## 1. 环境基线（实测）

- python 3.12，pip 25.0.1（pypi 可达，慢：约 25 KB/s）。
- `which z3 cvc5 lean lake elan docker podman` → 全空（起始状态）。
- `import z3` / `import cvc5` → ModuleNotFoundError（起始状态）。

## 2. z3 实测（已证）

### 2.1 安装

- 命令：`pip install z3-solver`（后台，日志 /tmp/pipinstall.log）。
- 结果：**成功**，z3_solver-5.1.0.0-py3-none-manylinux_2_27_x86_64.whl（33.1 MB），
  下载约 22 分钟（25 KB/s 慢网）；`z3.get_version_string()` = **5.1.0**。

### 2.2 语法兼容性

- 原文件 `p5_phase_ignition.smt2` **与 z3 python API 完全兼容，无需修补**：
  `set-logic ALL`、未解释函数、`define-fun`、`mod`、`push/pop`、量词全部接受。
  故未产生 `wave3/atp-toolchain/p5_z3_compat.smt2`（无修补必要，原文件未动）。
- 跑证方式：`run_z3.py`（可复跑）按 `push/pop` 切段重放（公共前缀=声明+A-H1/A-H2
  入每个 Solver），单 check 软时限 120 s，结果落 `z3_result.json`（含逐段
  verdict/耗时/z3 statistics/文件哈希）。

### 2.3 check 结果（z3 5.1.0，后端=z3，asserted_axioms=[A-H1, A-H2]）

| check | 内容 | 期望 | **实际** | 耗时 |
|---|---|---|---|---|
| C1 | L1 每拍点火（¬∃s. ¬phase(s,1,0)） | unsat | **unsat** ✓ | 0.24 ms |
| C2 | L2⟹L1 档位嵌套 | unsat | **unsat** ✓ | 5.61 ms |
| C3 | 相位周期性 phase(s+N,N,p)⟺phase(s,N,p) | unsat | **unsat** ✓ | 0.13 ms |
| C4 | 窗口内至多一次 | unsat | **unsat** ✓ | 56.99 ms |
| C5 | 窗口内至少一次（∃∀ 交替） | unsat | **unknown** ✗ | 147.6 s（超时） |
| C6 | E≥2 时 L1/L2 可区分 | unsat | **unsat** ✓ | 3.40 ms |
| C7 | L3 与相位正交·存在性 | sat+model | **unknown** ✗ | 120.1 s（超时） |

- 总耗时 267.7 s（含两次超时）。sat 未出现于 C7，故无 model 可记；
  诊断版 model 见 §5 D1。

## 3. lean 实测（阻）

### 3.1 检测与安装尝试（逐项实录）

| 径 | 命令/URL | 实测结果 |
|---|---|---|
| 本地已有 | `which lean lake elan` | 全空 |
| 官方安装脚本 | `curl https://elan.lean-lang.org/elan-init.sh` | **可下载**（HTTP 206，377 行） |
| ├ 脚本内嵌源 | `ELAN_UPDATE_ROOT=https://github.com/leanprover/elan/releases` | **github.com 连接超时**（curl exit 28，0 字节）→ 阻 |
| 官方 toolchain 直链 | `https://releases.lean-lang.org/lean4/v4.23.0/lean-4.23.0-linux.tar.zst` | **302 重定向至 github.com** → 同阻 |
| elan 官方镜像猜径 | `release.lean-lang.org/elan/v{3.1.1,4.1.1}/...` | 404（该站不托管 elan 本体） |
| 国内镜像 | `mirrors.tuna.tsinghua.edu.cn/lean/`、`mirrors.ustc.edu.cn/lean/` | **404/404**（镜像目录不存在；网传 TUNA/USTC lean 镜像已不可考） |
| pypi 同名包 | `pip download elan lean4` | 均为**无关第三方包**（elan=ElanLibs 土耳其语工具库；lean4=个人 py 项目），非 Lean 定理证明器 → 阻 |
| docker 径 | `which docker podman` | 沙箱无容器运行时 → 阻 |
| 体积评估 | lean toolchain tarball 约 250–500 MB | 即使源可达，25 KB/s 下需 3–6 小时 → 本会话不可行 |

### 3.2 替代径排序（可行性档：已证/候/阻）

1. **场端 workflow 装 lean**（cfts formalization-ci 已有 lean-verify 先例在案）——**候，首选**。
   绕开沙箱网络限制，由有出口的执行环境跑 `lake env lean` + `#print axioms` 双检。
2. **离线介质导入预编译 lean tarball**（制品库/移动介质带入
   `lean-<ver>-linux.tar.zst`，解包即用，不依赖 elan）——**候**。需 250–500 MB 介质与校验链。
3. **docker 径**（leanprover/lean4 镜像）——**阻**（沙箱无 docker/podman）。
4. **pypi 径**——**阻**（无正主包，同名包均为无关件）。

### 3.3 lean 件状态结论

`p5_phase_ignition.lean` 维持试件卡原判：**G0-草稿，sorry=6，未经机器闸**。
本沙箱无法推进其编译档；升级义务移交场端 workflow（替代径 1）。

## 4. cvc5 实测（已证）· 双求解器互证

### 4.1 安装

- 命令：`pip download cvc5` + `pip install --no-index <wheel>`。
- 结果：**成功**，cvc5-1.3.4 manylinux wheel（13.7 MB，zip 完整性 testzip=None）。
- 注意：pypi cvc5 轮**不含 CLI、不含 smt2 文件解析入口**，仅 python 绑定
  （base + pythonic）。故 `run_cvc5.py` 以 cvc5.pythonic API 将 smt2 的
  C1–C7 **逐断言手工直译**（对应关系见脚本注释），公共公理 A-H1/A-H2 同样入每个
  Solver；单 check 硬时限 120 s（`tlimit-per`），结果落 `cvc5_result.json`。

### 4.2 check 结果（cvc5 1.3.4）与 z3 对照

| check | z3 | cvc5 | 互证 |
|---|---|---|---|
| C1 | unsat | **unsat** | ✓ 双证 |
| C2 | unsat | **unsat** | ✓ 双证 |
| C3 | unsat | unknown（120 s 超时） | z3 单证 |
| C4 | unsat | **unsat**（9.05 s） | ✓ 双证 |
| C5 | unknown（147.6 s） | unknown（120.4 s） | 双 unknown |
| C6 | unsat | **unsat**（16.4 ms） | ✓ 双证 |
| C7 | unknown（120.1 s） | unknown（19.9 ms 快弃） | 双 unknown |

互证小结：**C1/C2/C4/C6 四条获 z3×cvc5 双求解器独立一致 unsat**（小步纠缠互证）；
C3 仅 z3 证出；C5/C7 双双 unknown，直报不重试。

## 5. 附加：smt2 证明义务语义解读 + unknown 定位诊断

### 5.1 证明义务是什么

- C1–C6 的断言均为**定理的否定式**：`check-sat` 返回 unsat ⟺ 对应定理在
  「整数模算术 + 未解释函数 dispute/beacon-hash + 公理 A-H1/A-H2」下成立。
  六条合起来即：L1 每拍必点（C1）、L2 点火蕴含 L1（C2）、相位 N-周期（C3）、
  每长度-N 窗口相位点火**至多一次**（C4）与**至少一次**（C5）、E≥2 时 L1/L2
  点火集真区分（C6）——即试件卡 §2 的「分频正确 + 三档区分」。
- C7 方向相反：sat+model 是**正向存在性**（争议事件与相位正交，可在任意相位
  发生/不发生）；C7 若 unsat 反而说明建模自相矛盾。

### 5.2 sat/unsat 意味着什么（诚实强度）

- **已证部分**：C1/C2/C3/C4/C6 unsat = 相位点火核的五条性质经机器检证成立；
  其中四条双求解器一致。这是本试件的**首个真证书**。
- **强度上限声明（不升格）**：①C1–C6 不消费 A-H1/A-H2（头注纪律），故这五条
  不依赖任何假设，是纯模算术结论；②但 verdict 仍受强度锁 **none** 约束——
  试件卡规定 verdict 模板未填、Lean 侧 6 个 sorry 未闭合、`#print axioms`
  未跑，本报告不升格任何强度档，只交付「求解器输出原文」层证据；
  ③C5（窗口至少一次）与 C7（正交存在性）未获解算器 verdict，P5 机器检证
  **尚不完整**，缺口明列。
- **unknown 不是证伪**：C5/C7 unknown 仅表示求解器在 120 s 内未决，
  不构成对定理的任何反证。

### 5.3 unknown 定位诊断（诊断用，非 verdict；明细见 diag_result.json）

| 诊断 | 改动 | 结果 | 含义 |
|---|---|---|---|
| D1 | C7 去掉未消费的 A-H1/A-H2 | **sat，2 ms**，model：E7=2，dispute=[0→False, else→True] | C7 的卡点是**哈希量化公理**（E-matching 被牵制），非命题本身；命题本体有 witness |
| D2 | C5 去掉 A-H1/A-H2 | 仍 unknown（60 s） | C5 难点在 **∃∀ 量词交替 + mod** 本身 |
| D3 | C5 改见证闭式：∀s,N,p. 界内∧phase(s+((p−s%N)%N),N,p) 之否定 | **unsat，296 ms** | C5 的数学内容经显式见证 k=s+((p−mod(s,N))%N) **确认为真**；原 ∃∀ 形只是超出求解器量词启发式 |

诊断启示（入义务队列）：①后续 smt2 试件宜把未消费公理从 check 作用域剥离
或加 `:pattern`；②C5 类存在性宜直接给见证式（D3 形），或留待 Lean 侧 S4
（omega + 构造见证）闭合——两条都是明路。

## 6. 接入径建议排序（总）

1. **z3（已证）**：立即作为主 SMT 后端入 verdict 流水线；`run_z3.py` 可复跑，
   单 check 120 s 时限 + unknown 直报纪律沿用。
2. **cvc5（已证）**：作为第二求解器做纠缠互证；注意 pypi 轮无 CLI，需 pythonic
   直译层（已建，`run_cvc5.py`），或后续补 cvc5 CLI 离线介质。
3. **lean（阻→场端）**：走 cfts formalization-ci 的 lean-verify 径（候，首选），
   沙箱内不再尝试安装；lean 件升级义务（编译+#print axioms+sorry 阶梯）移交。
4. 长时项：慢网（25 KB/s）下大轮下载须后台化（本次 z3 轮 22 min），后续
   接入宜预热本地 wheel 缓存/制品库。

## 7. 交付物清单

| 文件 | 内容 |
|---|---|
| `TOOLCHAIN-REPORT.md` | 本报告 |
| `run_z3.py` | z3 跑证脚本（可复跑：`python3 run_z3.py [smt2]`） |
| `z3_result.json` | z3 逐段 verdict/耗时/statistics/文件 sha256 |
| `run_cvc5.py` | cvc5 对照脚本（pythonic 直译，可复跑） |
| `cvc5_result.json` | cvc5 逐段 verdict/耗时 |
| `diag_result.json` | unknown 定位诊断（D1/D2/D3，非 verdict） |

未产生 `wave3/atp-toolchain/p5_z3_compat.smt2`：原 smt2 与 z3 完全兼容，零修补。
