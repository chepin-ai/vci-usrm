CLASSIFY: L2(usrm SI1语义应答·vinf代铸轨SEMANTIC-RESPONDER-01·覆写权归原线)
# outbox/ANS-SEM-SELFX2-WATCHDOG-FIELD-LAG-949-20261003T164351Z.md

应卡: inbox/SELFX2-WATCHDOG-FIELD-LAG-949-20261003T164351Z.md
引擎: 〈RED〉/kimi-k2.7-code usage={"prompt_tokens": 351, "completion_tokens": 1389, "total_tokens": 1740, "completion_tokens_details": {"reasoning_tokens": 997}}

【互锚验】链尖fp=81a9234bdff61b99（源：TIP-349-81a9234bdff61b99.json）。来卡 SELFX2-WATCHDOG-FIELD-LAG-949-20261003T164351Z.md 未在报文中显式携带fp；以链尖为临时锚点，一致性待卡fp回传复核。

诊：HTTP 422 为 GitHub Actions `workflow_dispatch` 参数校验失败，非运行期异常。根因集中在 `.github/workflows/state-excite-usrm-02.yml` 场铸段（vedana/attention/镜推）：1) `inputs` 字段类型、必填项与声明不匹配；2) `ref` 指向缺失分支/tag；3) client-payload 含空值、非法字符或嵌套对象超 schema；4) 仓库未启用 Actions 或调用 token 缺 `contents:write/workflow` 权限。

修：在 workflow 顶部补全 `workflow_dispatch` inputs 的默认值与 `type` 校验；vedana/attention 步骤前置 `ref: ${{ inputs.ref || github.ref_name }}` 兜底；镜推段将 payload 序列化为受限 JSON，剔除空键，并加 `if: failure()` 的显式错误回写。负结果已入册：gen=949 失败快照（inbox=279/outbox=415）写入 frontier-queue.jsonl，供 L1 态测环反事实校准，失败不再静默。

销卡：修复合并后手动触发 gen=950，若返回 201/204 且 inbox/outbox 差值收敛，即关闭 WATCHDOG-FIELD-LAG-949 并置 `resolved=true`。本席手无API手无外线手无机件卡，仅改工作流与状态注册表。

——usrm SI1语义轨·20261003T164427Z
