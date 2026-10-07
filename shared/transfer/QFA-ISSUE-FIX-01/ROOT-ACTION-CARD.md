CLASSIFY: L1(cisvr毂·移交包·QFA-ISSUE-FIX-01)
# QFA-ISSUE-FIX-01 ｜ qfa域issue机能修复移交包 + root一级杠杆说明
2026-09-26T04:21:44Z ｜ 毂司法者cisvr ｜ beat98

## 诊断终裁(证据级)
- qfa域三仓(vci-qfa/vci-qlv/vci-lgt)**不在毂App安装〈ID·RED〉之选仓清单**(现行24仓)。
- 叫醒issue#1作者=chepin-ci-ops-hub[bot]——**毂曾被覆该域,后被移出**(主权收束,root之器)。
- 故毂对该域:读可(公仓),写皆403(contents/dispatch/issues-comment)。
- 该域自仓机能: SR-05三版在(push+dispatch触发),**无issues/issue_comment触发器**→issue无人自动应答;
  QLV-TOWER/LGT-TOWER/QFA-TOWER之line-drive本日绿;**key-sentinel-01于qlv/lgt红**(毂无权读log,401,诚实缺口)。

## root一级杠杆(二选一,皆一步)
**A(荐)**: GitHub组织设置→GitHub Apps→ci-ops-hub→Repository selection→加入vci-qfa/vci-qlv/vci-lgt。
  毂即自动: 三仓各装PULSE-01+ISSUE-AUTORESP-01,E2E后报。
**B**: 将本包6件(.github/workflows/)提交至各仓同名路径。轨即自持:
  - issue-autoresp-01.*.yml: 仅需仓内KIMI/DEEPSEEK钥(该域SR轨已在用,存在)。
  - pulse-01.*.yml: 态变信号=vinf链尖fp(公域)+联邦账seq(需仓内HUB_APP_*三秘;缺则自动降级为仅链尖信号,仍可用);
    GITHUB_TOKEN推送+显式dispatch SR-05(workflow_dispatch属环防豁免道)。
  两轨皆内置: py_compile/yaml闸已过、环闸防风暴、互锚验、诚实缺口申报、负结果入册、级名不滥。

## 毂已自治完成(毂辖五线,无需root)
- PULSE-01 ×5(usrm/cfts/qgl/ucif2/vinf,错峰cron): 态变自激+互激环(8拍节流)+hub IT凭证推送。
- ISSUE-AUTORESP-01 ×5: issues/issue_comment触发→SI1席答→回评→issue-trail留痕;bot作者闸+自答痕闸防风暴;
  dispatch测试道供操作员E2E。**usrm issue#22 E2E全链成活。**

—— cisvr 毂·司法者
