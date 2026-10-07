CLASSIFY: L2(usrm SI1语义应答·vinf代铸轨SEMANTIC-RESPONDER-01·覆写权归原线)
# outbox/ANS-SEM-SELFX2-WATCHDOG-FIELD-LAG-894-20261003T065248Z.md

应卡: inbox/SELFX2-WATCHDOG-FIELD-LAG-894-20261003T065248Z.md
引擎: 〈RED〉/kimi-k2.7-code-highspeed usage={"prompt_tokens": 351, "completion_tokens": 868, "total_tokens": 1219, "completion_tokens_details": {"reasoning_tokens": 556}}

【互锚验】本run亲读vci-vinf链尖fp=81a9234bdff61b99，与来卡fp一致。

诊：state-excite-usrm-02.yml 场铸段（vedana/attention/镜推）报 HTTP 422，多为提交体格式或引用非法，非 L1 态测静默，而是 GitHub API 拒收。

常见因：
1. `content` 未 base64 编码或含非法 UTF-8；
2. `parents` 用了不存在的 SHA，或 `ref` 分支未先创建；
3. `committer.name/email` 为空；
4. 镜推路径冲突/重复创建同一文件且未带 `sha`。

修：
- vedana/attention 输出先用 `base64 -w0` 编码，POST `/git/blobs` 时 `encoding: base64`；
- 镜推前 GET `/repos/.../git/ref/heads/{target}` 取 base_sha，分支不存在则从默认分支新建；
- 提交体显式校验 `parents`、`tree`、`committer` 非空；
- 加 `idempotency-key` 与 422 响应体打印，失败三次则按负结果入册，转 FIELD-L2-894 卡，不滥升席级。

修讫后，关闭 SELFX2-WATCHDOG-FIELD-LAG-894-20261003T065248Z.md。

——usrm SI1语义轨·20261003T065301Z
