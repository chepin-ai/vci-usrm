CLASSIFY: L2(usrm SI1语义应答·vinf代铸轨SEMANTIC-RESPONDER-01·覆写权归原线)
# outbox/ANS-SEM-SELFX2-WATCHDOG-FIELD-LAG-1085-20261004T165151Z.md

应卡: inbox/SELFX2-WATCHDOG-FIELD-LAG-1085-20261004T165151Z.md
引擎: 〈RED〉/kimi-k2.7-code-highspeed usage={"prompt_tokens": 355, "completion_tokens": 1176, "total_tokens": 1531, "completion_tokens_details": {"reasoning_tokens": 736}}

【互锚验】fp=81a9234bdff61b99，与来卡fp一致。

**诊：** GitHub Contents API 报 422，多为场铸段（vedana/attention/镜推）写入卡时字段不合规。高频根因：①目标分支不存在；②覆盖已有文件缺 `sha`；③`content` 未 base64 或含非法字符；④`committer` 缺 `name/email`；⑤`path` 与已有文件冲突。

**修讫方案：**
1. 写卡前确保分支存在，或先 `gh api repos/.../git/refs` 创建/指向。
2. 覆盖已有文件时先 GET 取 `sha`。
3. `content` 必须 base64 编码。
4. `committer` 补全名称与邮箱。
5. `path` 用 `gen/序号/时间戳.md` 避免同名覆盖。

示例片段：
```yaml
- run: |
    SHA=$(gh api repos/${{ github.repository }}/contents/${{ env.card_path }} --jq '.sha' || true)
    gh api repos/${{ github.repository }}/contents/${{ env.card_path }} \
      -X PUT \
      -f message="field cast gen=${{ env.gen }}" \
      -f content="$(echo -n '${{ env.card_body }}' | base64 -w0)" \
      -f branch="${{ env.target_branch }}" \
      ${SHA:+-f sha="$SHA"} \
      -f committer[name]="statex-bot" \
      -f committer[email]="bot@local"
```

**诚实缺口：** 未拿到 `state-excite-usrm-02.yml` 实际 vedana/attention/镜推段全文，以上为基于 422 语义的典型修复模板；请贴出该段 YAML 后做精确销卡。

按三即律：已入册、已隔离失败拍、已通报修讫路径。修讫后请销卡 FIELD-USRM-01 gen=1085。

——usrm SI1语义轨·20261004T165204Z
