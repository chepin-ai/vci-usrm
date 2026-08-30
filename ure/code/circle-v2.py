#!/usr/bin/env python3
# CIRCLE-v2 ｜ 圈论工程四条实现 + FS1 完备性猜想验证器 ｜ usrm 2026-08-30 (wave-42)
# 理论正本: vci-usrm/ure/circle-theory-01.md (v1) / circle-theory-02.md (v2)
# 四态判词: 证/候/冲/退。零编数律: 只输出可复算判词。
import hashlib, json, datetime, random

def H_(s): return hashlib.sha256(s.encode()).hexdigest()
def canon(o): return json.dumps(o, ensure_ascii=False, sort_keys=True, separators=(',', ':'))
def finding(state, checker, subject, evidence, note=''):
    return {'state': state, 'checker': checker, 'subject': subject, 'evidence': evidence, 'note': note,
            'ts': datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ'),
            'id': H_(canon({'c':checker,'s':subject,'e':evidence}))[:12]}

# ============ 工程四条 E1-E4 ============
SCHEMA_FIELDS = ['circle_id', 'members', 'event_anchor', 'closure_proof', 'degradation_state']

def E1_schema_validate(rec):
    """E1 schema 统一: 圈账件五字段齐备性核验。缺字段=候（现有各圈账件多为历史格式，诚实判候）。"""
    missing = [f for f in SCHEMA_FIELDS if f not in rec or rec[f] in (None, '', [])]
    if not missing:
        return finding('证', 'E1-SCHEMA', rec.get('circle_id','?'), {}, '五字段齐备')
    return finding('候', 'E1-SCHEMA', rec.get('circle_id','?'), {'missing': missing}, 'schema 未统一（历史格式）')

def E2_closure_proof_required(rec):
    """E2 闭合证明强制入账: 声称已闭合而无证明锚 = 冲（裸 done, G-N6 已立法）。"""
    if rec.get('status') == 'closed' and not rec.get('closure_proof'):
        return finding('冲', 'E2-CLOSURE', rec.get('circle_id','?'), {'status':'closed','closure_proof':None}, '裸 done：闭合无证明')
    return finding('证', 'E2-CLOSURE', rec.get('circle_id','?'), {}, '闭合有证或未声称闭合')

def E3_health(rec):
    """E3 圈健康机检: kappa(闭合判据先验)/tau(超时降级梯)/Lambda(账) 三面各一检。"""
    out = []
    out.append(finding('证' if rec.get('kappa') else '候', 'E3-KAPPA', rec.get('circle_id','?'),
                       {'kappa': rec.get('kappa')}, '闭合判据已先验化' if rec.get('kappa') else '闭合判据缺失'))
    out.append(finding('证' if rec.get('tau') else '候', 'E3-TAU', rec.get('circle_id','?'),
                       {'tau': rec.get('tau')}, '降级梯已定义' if rec.get('tau') else '降级梯缺失'))
    out.append(finding('证' if rec.get('ledger') else '候', 'E3-LAMBDA', rec.get('circle_id','?'),
                       {'ledger': rec.get('ledger')}, '账落链可复算' if rec.get('ledger') else '账缺失'))
    return out

def E4_cross_anchor(tips):
    """E4 C2 锚总线: 对任意圈尖字典 {圈id: tip} 计算两两 cross=sha256(tipA+tipB)[:16] 及总线根。"""
    ids = sorted(tips)
    pairs = {}
    for i in range(len(ids)):
        for j in range(i+1, len(ids)):
            a, b = ids[i], ids[j]
            pairs[f'{a}x{b}'] = H_(str(tips[a]) + str(tips[b]))[:16]
    root = H_(canon(pairs))[:16] if pairs else None
    return {'pairs': pairs, 'bus_root': root}

# ============ FS1 验证器 ============
class Circle:
    """模型圈: 锚链事件流 e_i={content, prev}; tip=链尖哈希。"""
    def __init__(self, cid, parent=None):
        self.cid, self.parent, self.children = cid, parent, []
        self.events, self.tip = [], ''
    def emit(self, content):
        e = {'content': content, 'prev': self.tip}
        self.events.append(e); self.tip = H_(self.tip + canon(e))
    def lift_anchor(self):
        """A2 锚上浮: 父圈把本子圈 tip 记入自己的锚事件。"""
        if self.parent is not None:
            self.parent.emit({'lift': self.cid, 'child_tip': self.tip})
            self.parent.recorded_tips[self.cid] = self.tip

class Tower:
    """n 阶圈塔: 0 阶叶圈 → … → 根(C2 总线核验在每一对父子间执行)。"""
    def __init__(self, height, branching, seed=0):
        rng = random.Random(seed)
        self.root = Circle('root')
        self.root.recorded_tips = {}
        self.all = [self.root]
        def build(parent, h):
            if h == 0: return
            for i in range(branching):
                c = Circle(f'{parent.cid}.{i}', parent); c.recorded_tips = {}
                parent.children.append(c); self.all.append(c)
                build(c, h-1)
        build(self.root, height)
        for c in self.all: c.emit(f'genesis-{c.cid}')
        # 初始锚上浮（自叶向根）
        for c in sorted(self.all, key=lambda x: -x.cid.count('.')): c.lift_anchor()
    def inject_inconsistency(self, seed=1, model='A'):
        """对手二型: A=篡改事件内容（C1 链复算可破）; B=篡改后诚实重锚全链（本地链复算自洽，唯 C2 两两锚比较可破）。"""
        rng = random.Random(seed)
        c = rng.choice([x for x in self.all if x is not self.root and x.events])
        idx = rng.randrange(len(c.events))
        c.events[idx]['content'] = {'TAMPERED': c.events[idx]['content']}
        if model == 'B':
            tip = ''
            for e in c.events:
                tip = H_(tip + canon(e))
            c.tip = tip  # 重锚：本地链完全自洽
        return c.cid, idx
    def detect(self):
        """C1/C2 检测: (i) 单圈链复算 (C1 谓词); (ii) 父记子尖 vs 子实尖 两两比较 (C2 谓词)。
        返回: (是否检出, 检出谓词阶数列表, 延迟拍数上界)。"""
        predicates = []
        for c in self.all:
            # C1: 链复算
            tip = ''
            for e in c.events:
                tip = H_(tip + canon(e))
            if tip != c.tip: predicates.append(1)
            # C2: 两两锚比较
            for ch in c.children:
                if c.recorded_tips.get(ch.cid) != ch.tip: predicates.append(2)
        detected = bool(predicates)
        return detected, sorted(set(predicates)), (max((x.cid.count('.') for x in self.all), default=0) if detected else 0)

def FS1_verify(trials=200, max_height=4, branching=3):
    """FS1: n 阶圈塔任意处注入不一致，检测恒可归纳为一阶/二阶谓词（链复算 + 两两锚比较），
    无需三阶以上谓词；检出率与延迟统计。"""
    stats = {'trials': 0, 'detected': 0, 'max_predicate_order': 0, 'max_latency_beats': 0}
    per_height = {}
    for h in range(1, max_height+1):
        dh = {'trials': 0, 'detected': 0}
        for t in range(trials):
            tw = Tower(h, branching, seed=t)
            tw.inject_inconsistency(seed=t*7+1, model=('A' if t % 2 == 0 else 'B'))
            ok, preds, lat = tw.detect()
            stats['trials'] += 1; dh['trials'] += 1
            if ok:
                stats['detected'] += 1; dh['detected'] += 1
                stats['max_predicate_order'] = max(stats['max_predicate_order'], max(preds))
                stats['max_latency_beats'] = max(stats['max_latency_beats'], lat)
        per_height[h] = dh
    stats['per_height'] = per_height
    stats['detection_rate'] = stats['detected'] / stats['trials']
    return stats

if __name__ == '__main__':
    print('CIRCLE-v2 loaded: E1-E4 工程四条 + FS1 验证器')
