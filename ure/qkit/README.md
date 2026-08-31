# fieldqkit v1 — QF-OS 通用/可复用量子接口共享库（canonical）
2026-08-31T16:15:51Z ｜ wave-56 立（root 问：为什么不使用 fieldqkit 及通用/可复用量子接口包@共享库 → 本波落地）

## 统一面
`run(ops, nq, engine, shots, creds, backend, wait)` / `bell()` / `chsh()` / `ghz3()` — 引擎='numpy'|'quafu'|'qr'。
电路=指令列表 `[('h',0),('cnot',0,1),('ry',q,θ),('rz',q,θ),('x',q)]`，引擎差异（参数序/鉴权/并发性）全部封装在适配器内，调用方零感知。

## 引擎适配要点（wave-46~55 实测沉淀）
- **numpy**：本地态矢（without 基座），返回 counts+exact 双轨。
- **quafu**（北量子院 Quafu 云）：`User(api_token=QUAFU_KEY)` 显式注入；`Task(user=u)`；`t.config(backend=,shots=)` 设后端；`t.send(qc,wait=False)` 异提交→`t.retrieve(taskid)` 轮询。同账户并发会话降级（返回空 counts 无异常）→ 顺序/异步轮询策。
- **qr**（QuantumRings scarlet_quantum_rings，64q）：`QuantumRingsProvider(token=QR_KEY_64, name=QR_USER)`（token-only 报 Invalid account name）；qiskit 参数序 `qc.ry(θ,q)`；`job_monitor(job)` 后 `job.result().get_counts()`；并发主引擎（4/4 实证全成质量不降）。

## 后端实况（wave-56 轮询）
ScQ-P5=5q 超导真机 Online（队 635）；ScQ-Sim10=模拟器 Online；Baihua=119q Online（队 477）；余 Offline/Obsolete。

## smoke 证据
smoke-01.json（numpy Bell/CHSH S=2.8174>2；QR Bell/GHZ3；quafu Bell Completed 8C67F8601510F98C）。
