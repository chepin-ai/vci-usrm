#!/usr/bin/env python3
# KERNEL-DERIVE-01-ENGINE ｜ 核心机自动推演引擎 L1-L3 ｜ usrm 2026-08-30 (wave-42)
# 设计正本: vci-usrm/ure/kernel-derive-01.md（L0手工→L1立法机读→L2不变量挖掘→L3反事实推演）
# 四态判词: 证(直接观测成立)/候(待裁决)/冲(与既有档冲突)/退(已撤回)
# 零编数律: 本引擎只输出由输入数据可复算的判词; 无数据即输出「未测」, 绝不编造。
import hashlib, json, datetime

V_ZHENG, V_HOU, V_CHONG, V_TUI = '证', '候', '冲', '退'

def canon(o):
    return json.dumps(o, ensure_ascii=False, sort_keys=True, separators=(',', ':'))

def finding(state, checker, subject, evidence, note=''):
    return {'state': state, 'checker': checker, 'subject': subject,
            'evidence': evidence, 'note': note,
            'ts': datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ'),
            'id': hashlib.sha256(canon({'c': checker, 's': subject, 'e': evidence}).encode()).hexdigest()[:12]}


def extract_cron(yaml_text):
    """从 workflow yaml 抽取活 cron 表达式——剥注释行/行内注释（FINDING-KD-001 教训：正则裸扫会把已废注释行当活 cron）。"""
    import re as _re
    out = []
    for line in (yaml_text or '').splitlines():
        code = line.split('#', 1)[0]
        out += _re.findall(r"cron:\s*'([^']+)'", code)
    return out

# ============ L1: 立法机读 → 规则自生（N-MUST 机器可判定子集） ============

def check_M12_cron(workflows_by_repo, whitelist):
    """M12/SENTINEL-01: 全 org 仅白名单内 (repo,workflow) 可含 schedule 触发器。
    workflows_by_repo: {repo: [{name, path, state, cron:[...]}]}  cron 由调用方解析 yaml 提供。
    返回判词列表：每发现一个白名单外 cron = 证(违规直接观测)。"""
    out = []
    for repo, wfs in workflows_by_repo.items():
        for w in wfs:
            for c in (w.get('cron') or []):
                key = (repo, w['name'])
                if key not in whitelist:
                    out.append(finding(V_ZHENG, 'M12-CRON', f"{repo}/{w['name']}",
                                       {'cron': c, 'path': w.get('path')}, '白名单外 schedule 触发器'))
    return out

def check_M3_disabled(workflows_by_repo, expected_active):
    """M3: 立法/注册表声明应活跃的 workflow 不得处于 disabled 态。
    expected_active: set of (repo, workflow_name)。disabled_manually 且被期待 = 证。"""
    out = []
    for repo, wfs in workflows_by_repo.items():
        for w in wfs:
            if (repo, w['name']) in expected_active and str(w.get('state','')).startswith('disabled'):
                out.append(finding(V_ZHENG, 'M3-DISABLED', f"{repo}/{w['name']}",
                                   {'state': w['state']}, '被期待活跃但处于 disabled'))
    return out

def check_M14_crossface(faces, registry_expect):
    """M14 四面勾稽: 注册表声明的锚尖 vs 实际链尖。faces={面名: 实际tip}; registry_expect={面名: 声明tip}。
    不一致 = 冲(与注册表冲突); 面缺失于注册表 = 候。"""
    out = []
    for face, tip in faces.items():
        exp = registry_expect.get(face)
        if exp is None:
            out.append(finding(V_HOU, 'M14-CROSSFACE', face, {'actual_tip': tip}, '注册表未登记该面'))
        elif exp != tip:
            out.append(finding(V_CHONG, 'M14-CROSSFACE', face,
                               {'actual_tip': tip, 'registry_tip': exp}, '锚尖不一致'))
    return out

# ============ L2: 不变量挖掘（Δ-BASE 运行面：基线包络 + 出包络即候选） ============

def mine_baseline(entries, wallclock_utc):
    """entries: stream-ledger 式 [{seq, ts, hash, ...}]（已按 seq 排序）。
    产出: 基线度量 + 链完整性核验 + 出包络判词。
    阈值 wave-58 自标定（root wave-57 自治令+DISSENT-WINDOW-01，异议窗72h）: MAX_GAP_MIN=720 = 2×max_observed(363.7min, wave-55 实测) 取整; min_chain_ok=1.0。数据驱动, 随 Δ-BASE 累积再收敛。"""
    MAX_GAP_MIN, res = 720, {'n': len(entries)}
    if not entries:
        return {'metrics': res, 'findings': [finding(V_HOU, 'L2-BASELINE', 'stream-ledger', {}, '空账：未测')]}
    # 链完整性（sha256(prev+canon) 全 64 位）
    ok, bad, dialects = 0, [], set()
    for i in range(1, len(entries)):
        prev, cur = entries[i-1], entries[i]
        body = {k:v for k,v in cur.items() if k!='hash'}
        hit = None
        for dia, kw in (('ascii', {}), ('utf8', {'ensure_ascii': False})):
            expect = hashlib.sha256((prev.get('hash','') + json.dumps(body, sort_keys=True, separators=(',', ':'), **kw)).encode()).hexdigest()
            if cur.get('hash') == expect: hit = dia; break
        if hit: ok += 1; dialects.add(hit)
        else: bad.append(cur.get('seq'))
    res['chain_dialects'] = sorted(dialects)
    res['chain_ok_ratio'] = ok / max(1, len(entries)-1)
    # 时间间隔
    def pt(ts): return datetime.datetime.fromisoformat(ts.replace('Z','+00:00'))
    gaps = [(pt(entries[i]['ts']) - pt(entries[i-1]['ts'])).total_seconds()/60 for i in range(1,len(entries))]
    res['max_gap_min'] = round(max(gaps),1) if gaps else 0
    res['rate_per_hour'] = round(len(entries) / max(1/60,(pt(entries[-1]['ts'])-pt(entries[0]['ts'])).total_seconds()/3600),2) if len(entries)>1 else None
    res['clock_drift_min'] = round((wallclock_utc - pt(entries[-1]['ts'])).total_seconds()/60,1)
    f = []
    if bad: f.append(finding(V_ZHENG, 'L2-CHAIN', 'stream-ledger', {'bad_seq': bad[:8]}, '链哈希核验失败条目'))
    if res['max_gap_min'] and res['max_gap_min'] > MAX_GAP_MIN:
        f.append(finding(V_HOU, 'L2-ENVELOPE', 'stream-ledger', {'max_gap_min': res['max_gap_min'], 'threshold': MAX_GAP_MIN}, '出包络：间隔超阈（wave-58 自标定 720min）'))
    return {'metrics': res, 'findings': f}

# ============ L3: 反事实推演（阻塞图反演：若 X 沉默，何件阻塞） ============

def counterfactual_stall(expect_items, silent):
    """expect_items: [{id, owner, depends_on:[owner...], deadline}]（EXPECT-REG-01 形）。
    silent: set(owner)。返回: 每个沉默主体造成的传递阻塞闭包 + 预警判词。"""
    by_owner = {}
    for it in expect_items: by_owner.setdefault(it.get('owner','?'), []).append(it)
    out = []
    for s in silent:
        blocked, frontier, seen = [], [s], {s}
        while frontier:
            cur = frontier.pop()
            for it in expect_items:
                if cur in (it.get('depends_on') or []) and it['id'] not in seen:
                    seen.add(it['id']); blocked.append(it['id'])
                    frontier.append(it.get('owner','?'))
        out.append({'silent_owner': s, 'transitively_blocked': sorted(blocked)})
    findings = [finding(V_HOU, 'L3-STALL', r['silent_owner'], {'blocked': r['transitively_blocked']},
                        '反事实：该主体沉默将阻塞以上期待件') for r in out if r['transitively_blocked']]
    return {'simulation': out, 'findings': findings}

# ============ 总装 ============

def derive(workflows_by_repo=None, whitelist_cron=None, expected_active=None,
           faces=None, registry_expect=None, ledger_entries=None, expect_items=None, silent=None,
           wallclock_utc=None, patterns=None, findings_new=None):
    rep = {'L1': [], 'L2': None, 'L3': None, 'L4': None, 'L5': None}
    trace = ['M-001 LOAD-AXIOM: derive() 上下文装配']  # M-CODE-01 指令轨迹（INV-M3: 步必引已登记码）
    if workflows_by_repo is not None:
        trace.append('M-003 CHECK-INV: M12/M3 (workflows_by_repo)')
        rep['L1'] += check_M12_cron(workflows_by_repo, whitelist_cron or set())
        rep['L1'] += check_M3_disabled(workflows_by_repo, expected_active or set())
    if faces is not None:
        trace.append('M-003 CHECK-INV: M14 crossface')
        rep['L1'] += check_M14_crossface(faces, registry_expect or {})
    if ledger_entries is not None:
        trace.append('M-003 CHECK-INV: L2 baseline (Δ-BASE 同构验链)')
        rep['L2'] = mine_baseline(ledger_entries, wallclock_utc or datetime.datetime.now(datetime.timezone.utc))
    if expect_items is not None and silent is not None:
        trace.append('M-002 APPLY-RULE: L3 counterfactual stall')
        rep['L3'] = counterfactual_stall(expect_items, silent)
    if faces is not None and ledger_entries is not None:
        trace.append('M-006 CHECK-REFNET: L4 直通场读出')
        rep['L4'] = check_L4_refnet(faces, ledger_entries)
    if patterns is not None or findings_new is not None:
        trace.append('M-007 AUTOFIRE: L5 pattern 自动触发')
        rep['L5'] = autofire_L5(patterns or [], (findings_new or []) + rep['L1'])
    for f in rep['L1']:
        trace.append('M-004 EMIT-FINDING: ' + str(f.get('id', '?')))
    trace.append('M-005 COMMIT-LEDGER: 由调用方(kernel-loop P5)落 stream-ledger + Δ-BASE delta')
    rep['mcode_trace'] = trace
    rep['summary'] = {'L1_findings': len(rep['L1']),
                      'L2_findings': len(rep['L2']['findings']) if rep['L2'] else '未测',
                      'L3_blocked_groups': sum(1 for r in (rep['L3']['simulation'] if rep['L3'] else []) if r['transitively_blocked']) if rep['L3'] else '未测'}
    return rep

if __name__ == '__main__':
    print('KERNEL-DERIVE-01-ENGINE loaded: L1+L2+L3 + L4(refnet 直通场) + L5(pattern autofire)')


# ============ wave-68 扩展：L4 全息米田直通场 + L5 pattern 自动触发 ============
def check_L4_refnet(faces, ledger_entries):
    """L4 引用网一致性：直通场读出器雏形。
    判据：faces 自报尖 vs ledger 实记尖——自报与引用不符即 FINDING（M14 场化）。
    faces 期望含 {'narrative': 'seq@hash', 'ledger': 'seq@hash'} 形。"""
    out = []
    if not faces or not ledger_entries:
        return out
    try:
        tip = ledger_entries[-1]
        led_face = (faces.get('ledger') or faces.get('stream')) if isinstance(faces, dict) else None
        if led_face:
            fs = str(led_face)
            ok = (fs.split('@')[0].isdigit() and int(fs.split('@')[0]) == tip.get('seq')) or (fs[:12] == str(tip.get('hash',''))[:12])
            if not ok:
                out.append(finding(V_ZHENG, 'L4-REFNET-DIVERGE', 'faces-vs-ledger',
                                   {'faces_ledger': led_face, 'ledger_tip': str(tip.get('seq'))+'@'+str(tip.get('hash',''))[:12]},
                                   '自报尖与实记尖分叉（直通场残差）'))
    except Exception as e:
        out.append(finding(V_HOU, 'L4-ERROR', 'refnet', {'err': str(e)[:80]}, 'L4 复算异常'))
    return out

def _gate_context(scene, f):
    """语境环: 发现来自何方(checker/organ/subject/state)——源流不合即不开火; exclude_checker 抑噪音面"""
    c = scene.get('context', {})
    if not c: return True, 'ctx-free'
    if f.get('checker') in (c.get('exclude_checker') or []): return False, 'ctx-excluded:'+str(f.get('checker'))
    if c.get('checker') and c['checker'] != f.get('checker'): return False, 'ctx-checker-mismatch'
    if c.get('subject') and c['subject'] != f.get('subject'): return False, 'ctx-subject-mismatch'
    if c.get('state') and c['state'] != f.get('state'): return False, 'ctx-state-mismatch'
    return True, 'ctx-ok'

def _gate_syntax(scene, f):
    """语法环: 结构形——必需字段路径/ id 前缀"""
    sy = scene.get('syntax', {})
    if not sy: return True, 'syn-free'
    for fld in sy.get('has_fields', []):
        cur = f
        for part in fld.split('.'):
            if isinstance(cur, dict) and part in cur: cur = cur[part]
            else: return False, 'syn-missing:'+fld
    if sy.get('id_prefix') and not str(f.get('id', '')).startswith(sy['id_prefix']): return False, 'syn-id-prefix'
    return True, 'syn-ok'

def _gate_semantic(scene, p, f):
    """语义环: 意义命中——trigger.keyword/class(历史兼容) + scene.semantic.keywords/classes 同义群"""
    blob = json.dumps(f, ensure_ascii=False)
    trg = p.get('trigger', {})
    sem = scene.get('semantic', {})
    kws = ([trg['keyword']] if trg.get('keyword') else []) + (sem.get('keywords') or [])
    cls = ([trg['class']] if trg.get('class') else []) + (sem.get('classes') or [])
    kind = str(f.get('kind', '') or f.get('class', ''))
    hit = any(k in blob for k in kws) or any(c in kind for c in cls)
    if not kws and not cls: return True, 'sem-free'
    return hit, ('sem-hit' if hit else 'sem-miss')

def _gate_pragmatic(scene, f, fires):
    """语用环: 行事条件——最小重复计数/升级阈; 过则开火并允消融"""
    pr = scene.get('pragmatic', {})
    if not pr: return True, 'prag-free'
    mr = pr.get('min_repeat', 1)
    if mr > 1:
        n = sum(1 for x in fires if x.get('finding') == f.get('id'))
        if n + 1 < mr: return False, 'prag-below-min-repeat'
    return True, 'prag-ok'

def autofire_L5(patterns, findings_new):
    """L5 v2 场景识别四层管（wave-69 root令: 语境→语法→语义→语用, 四环全过方开火）。
    fold-n 统一: kind 属 fold 族(fold-n/eight-failures)的 fire 追加 dissolution 记录——
    多重折叠发现经四层管识别, 于语用环执行消融 D=Y(F) 重写(场论 v2.1 算子 D 的机械面)。
    patterns 无 scene 字段→退化 wave-68 语义单环(向后兼容)。"""
    fires = []
    for f in findings_new or []:
        blob = json.dumps(f, ensure_ascii=False)
        for p in patterns or []:
            scene = p.get('scene') or {}
            if not scene:
                trg = p.get('trigger', {})
                hit = (trg.get('class') and trg['class'] in str(f.get('kind', ''))) or \
                    (trg.get('keyword') and trg['keyword'] in blob)
                if hit:
                    fires.append({'pattern': p.get('id'), 'finding': f.get('id'),
                                  'action': p.get('action', 'archive-scaffold'),
                                  'verdict': V_HOU, 'pipeline': 'legacy-semantic',
                                  'note': '自动触发: 消融锚入引用网'})
                continue
            g1, r1 = _gate_context(scene, f)
            g2, r2 = _gate_syntax(scene, f) if g1 else (False, 'short')
            g3, r3 = _gate_semantic(scene, p, f) if g2 else (False, 'short')
            g4, r4 = _gate_pragmatic(scene, f, fires) if g3 else (False, 'short')
            if g1 and g2 and g3 and g4:
                rec = {'pattern': p.get('id'), 'finding': f.get('id'),
                       'action': p.get('action', 'archive-scaffold'),
                       'verdict': V_HOU, 'pipeline': 'scene-4gate',
                       'gates': {'context': r1, 'syntax': r2, 'semantic': r3, 'pragmatic': r4},
                       'note': '四层管全过: 自动触发'}
                kind = str(f.get('kind', '') or f.get('class', ''))
                if 'fold' in kind or 'eight-failures' in kind:
                    rec['dissolution'] = {'D': 'Y(F)-rewrite', 'target': f.get('id'),
                        'note': 'fold-n 多重折叠发现→消融: FINDING 引用网改写入 pattern 归档'}
                fires.append(rec)
    return fires

