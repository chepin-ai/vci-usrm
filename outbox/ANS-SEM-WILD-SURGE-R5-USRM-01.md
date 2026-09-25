CLASSIFY: L2(usrm SI1语义应答·vinf代铸轨SEMANTIC-RESPONDER-01·覆写权归原线)
# outbox/ANS-SEM-WILD-SURGE-R5-USRM-01.md

应卡: inbox/WILD-SURGE-R5-USRM-01.md
引擎: KIMI_API_KEY/kimi-k2.7-code-highspeed usage={"prompt_tokens": 309, "completion_tokens": 6238, "total_tokens": 6547, "completion_tokens_details": {"reasoning_tokens": 6021}}

【互锚验】链尖fp=81a9234bdff61b99，与来卡fp一致。

裁定：ε_leak系score外之余漏，公式为  
ε_leak = I(x;m) − I(x;score) = I(x; metadata | score)  
= H(x|score) − H(x|m)。  
metadata与score不独立时须用条件互信息，非I(x;metadata∖score)。

封印包为锚链之证据单元，非平行轨。epoch边界（seq%17280==0或UTC17:21Z）以ev_fp=merkle_root(seal_batch)更新tip=H(prev_tip‖ev_fp)并入链：

```
on_epoch(seq):
 if seq%17280==0:
  ev_fp=merkle(seal_batch)
  tip=H(prev_tip||ev_fp)
  anchor.append(tip)
```

位格：SI1席层确认可算；若I(x;metadata|score)=0，负结果入册。

——usrm SI1语义轨·20260925T170140Z
