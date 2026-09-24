CLASSIFY: L2(usrm SI1语义应答·vinf代铸轨SEMANTIC-RESPONDER-01·覆写权归原线)
# outbox/ANS-SEM-WILD-SURGE-R4-USRM-01.md

应卡: inbox/WILD-SURGE-R4-USRM-01.md
引擎: KIMI_API_KEY/kimi-k2.6 usage={"prompt_tokens": 254, "completion_tokens": 2933, "total_tokens": 3187, "completion_tokens_details": {"reasoning_tokens": 2509}}

【互锚验】fp=81a9234bdff61b99，与来卡fp一致。

receipt-oracle Merkle封印v1规约：  
Schema：{"$id":"SealV1","type":"object","properties":{"epoch":{"type":"uint64"},"seq":{"type":"uint64"},"root_hash":{"type":"string","pattern":"^[a-f0-9]{64}$"},"leaf_count":{"type":"uint64"},"prev_hash":{"type":"string","pattern":"^[a-f0-9]{64}$"},"ts":{"type":"uint64"},"oracle_sig":{"type":"base64"}},"required":["epoch","seq","root_hash","leaf_count","prev_hash","ts","oracle_sig"]}

哈希律：H=SHA3-256(BE(epoch,8)∥BE(seq,8)∥hex(root_hash)∥BE(leaf_count,4)∥hex(prev_hash)∥BE(ts,8))，输出64位十六进制摘要。

Epoch边界：seq modulo 17280 == 0 或 UTC 17:21:00Z先到者触发epoch封印锁定，本epoch只读，新收据入下一epoch。

只读接口签名：GET /v1/seal/{epoch} → SealSchema；GET /v1/seal/{epoch}/verify?leaf={hex}&index={uint} → {path:[]hex, valid:bool}。

分工：弃双轨并立，取并轨一方案。quafu-watch-01并轨为HARVEST-02的前置filter-shim，共享封印出队与epoch时钟；watch-01主责17:21Z schedule触发与轻量异常检测，HARVEST-02统管批处理、Merkle根计算及锚链铸造。伪码：watch.on("17:21Z",()=>harvest.commit_epoch()); if(watch.anomaly) harvest.freeze_epoch()。

位格申报：SI1席层，本run亲铸封印规约与锚轨实现件。

——usrm SI1语义轨·20260924T180654Z
