# CIRCLE-PATTERN-TOWER v2.2 附录：场景识别四层管 × fold-n 统一（wave-69）

> 锚：v2 双塔 + 全息米田直通场；v2.1 消解算子 D=Y(F) 重写。
> 本附录答 root wave-69 两问：pattern 自动触发的场景识别依赖；fold-n/FINDING 与 pattern 识别-触发的关联/统一。

## 一、场景识别四层管（pattern 塔之识机）

pattern 自动触发不是关键词碰撞，而是**场景识别**。一次开火 = 依次穿过四环：

1. **语境（context）**：发现来自何方——checker/organ/subject/state，源流不合即弃。
   噪音闸亦在此环：`exclude_checker`（如 M14-CROSSFACE 注册表噪音面），
   把"系统性误候"挡在语义环之外——语用级噪音控制的语境实现。
2. **语法（syntax）**：结构形——必需字段路径、id 前缀。形不合者，义无从谈起。
3. **语义（semantic）**：意义命中——keyword/class + 同义群（keywords/classes 并集）。
   此环即 wave-68 的全部触发逻辑；v2.2 把它降为四环之一。
4. **语用（pragmatic）**：行事条件——最小重复计数、升级阈。义中而机未熟，仍不开火。

四环全过，方得 fire。每 fire 携四环诊断（gates 字段），可审计、可复算。
形式化：pattern p 是四维场景空间的一点，finding f 开火 ⟺ f ∈ ⋂ᵢ gateᵢ(p)。

向后兼容：无 scene 字段的 pattern 退化为语义单环（wave-68 行为不变）。

## 二、fold-n × pattern 统一

**多重折叠发现**（fold-n：kernel 死折、verdict 漏洞折、失察折……）是 Yoneda 场的自指折叠点——
FINDING 的引用网 Y(F) 在场中自我弯折处。统一命题：

> **fold-n 的发现、识别、触发、消融，与 pattern 四层管是同一机械。**
> - 发现：折叠处于 L1/L2 检查器显形（多重=折上加折，n=折数）；
> - 识别：四层管读其场景（语义环命中 fold 族 kind）；
> - 触发：语用环达条件即开火；
> - 消融：fold 族 fire 自动追加 dissolution 记录——**D 算子 = 语用环对 fold 族的标准动作**，
>   把该 FINDING 的引用网改写（Y(F) rewrite）入 pattern 归档，折叠在场中被抚平为模式。

于是：pattern 识别-触发与 fold 消融不再两事——前者是后者的识别面，后者是前者的语用面。
关联/统一毕。

## 三、严格化注记：零火的合法性

四层管上线后首拍 L5_fires=0 非"无作为"，而是**正确判别**：该拍 L1 四面候（M14 注册表噪音）
无一场景命中——T1 冒烟复核同一零火。判别力（该火则火、不该火不火）即严格性本身：
T5 冒烟证 exclude_checker 噪音闸双向有效（M14 面不开火、他 checker 开火）。

## 四、机械落地锚

- 引擎：`kernel-derive-engine-01.py` autofire_L5 v2（四环管+dissolution 发射+legacy 兼容），冒烟 6/6。
- 注册表：`PATTERN-REG-01.json` v2，七模式全配 scene；P-GHOST 携 exclude_checker 示范噪音闸。
- 主线环：kernel-loop FLIGHT-DECK 影子拍每拍消费（wave-68 已接线），fire 与 dissolution 随拍入 findings 归档。

— usrm wave-69，场塔 v2.2
