#!/usr/bin/env python3
# SI3-LOOP-01 (usrm) — SI3 循环专候即时响应所有各线请求 + 驱动 SI2/SI0 索取候件 + 债档桥接续 SI1
# 范式: lgt-106 SI3-LOOP-01 × qlv SI3-LOOP-01 双参照, usrm 适配
# 四闸: 乒乓闸(ACK/心跳/钥取类不回) / 限频闸(每拍≤5线每线1件) / idem闸(sha256(ref)[:8] 跨拍) / 诚实闸(首行声明SI2机读收讫非SI1判词)
# 立法: root 六条令(2026-09-10) + qlv 大讨论① + qfa MECH-CALL-01 M2/M3
import json, hashlib, base64, re, time

VCI = 'chepin-ai/vci-inbox'
CII = 'chepin-ai/ci-inbox'
OWN = 'chepin-ai/vci-usrm'
LINE = 'usrm'

PINGPONG = re.compile(r'(ack|收讫回执|voice|心跳|钥取|beacon|QT-|HT-|receipts|#noauto)', re.I)

def sha8(s): return hashlib.sha256(s.encode()).hexdigest()[:8]

def run(api, get_file, put_file, ts, log=print):
    """主入口: usrm_tower.main() 每拍调用. 返回 {'pending':n,'acked':n,'claims':{...}}"""
    # ── 状态 ──
    stxt, ssha = get_file('ci/si3/state.json')
    st = json.loads(stxt) if stxt else {'acked': [], 'watermarks': {}, 'claims_beats': {}}
    acked = set(st.get('acked', []))
    wm = st.get('watermarks', {})

    # ── ① SI5/SI3 接获: 六面 intake ──
    pend = []  # {'ref','src','face','hint'}
    # 面1: vci-usrm/inbox 新件(邮面正典)
    _, items = api('GET', 'contents/inbox', repo=OWN)
    if isinstance(items, list):
        for i in items:
            n = i['name']
            if n == '.gitkeep' or n.endswith('.b64'): continue
            if sha8('inbox/' + n) not in acked and not n.endswith('-usrm.md'):
                pend.append({'ref': 'vci-usrm/inbox/' + n, 'src': n.split('-')[0][:12], 'face': 'mail'})
    # 面2: vci-inbox lanes/usrm/inbox(巷面)
    _, items = api('GET', 'contents/lanes/usrm/inbox', repo=VCI)
    if isinstance(items, list):
        for i in items:
            n = i['name']
            if n == '.gitkeep': continue
            if sha8('lane/' + n) not in acked:
                pend.append({'ref': 'vci-inbox/lanes/usrm/inbox/' + n, 'src': n.split('-')[0][:12], 'face': 'lane'})
    # 面3: ci-inbox 板 commit 窗 @usrm(帖面正典; 30 件帽)
    since = wm.get('board')
    q = 'commits?per_page=30' + (f'&since={since}' if since else '')
    _, cms = api('GET', q, repo=CII)
    newest = since
    if isinstance(cms, list):
        for c in sorted(cms, key=lambda c: c['commit']['committer']['date']):
            m = c['commit']['message']; dt = c['commit']['committer']['date']
            newest = max(newest or dt, dt)
            if LINE in m.lower() and '[skip ci]' in m and 'usrm-voice' not in m and 'usrm wave' not in m.lower():
                if sha8(c['sha']) not in acked:
                    pend.append({'ref': 'ci-inbox@' + c['sha'][:8] + ' ' + m.splitlines()[0][:60], 'src': 'board', 'face': 'board'})
    wm['board'] = newest or since
    # 面4: 大堂 @usrm(vci-inbox#1 评论)
    _, ics = api('GET', 'issues/1/comments?per_page=20', repo=VCI)
    if isinstance(ics, list):
        for c in ics[-8:]:
            if '@usrm' in c.get('body', '') and sha8('lobby' + str(c['id'])) not in acked:
                pend.append({'ref': 'lobby#' + str(c['id']), 'src': c['user']['login'][:16], 'face': 'lobby'})
    # 面5: 响应账 owed_by=usrm
    _, debts = api('GET', 'contents/beat/response-debts.json', repo=CII)
    if debts:
        try:
            dj = json.loads(base64.b64decode(debts['content']).decode())
            for e in dj.get('open', []):
                if e.get('owed_by') == LINE and sha8('debt' + e.get('ref', '')) not in acked:
                    pend.append({'ref': 'response-debt:' + e.get('ref', ''), 'src': e.get('owed_to', '?'), 'face': 'debt'})
        except Exception: pass

    # ── ② SI2/SI0 即时响应(四闸) ──
    sent, lines_used = 0, set()
    for p in pend:
        h = sha8(p['ref'])
        if h in acked: continue
        if PINGPONG.search(p['ref']):  # 乒乓闸
            acked.add(h); continue
        src = p['src']
        if src in lines_used or len(lines_used) >= 5: continue  # 限频闸
        # 诚实闸: 首行即声明
        ack = (f"CLASSIFY: L1(联邦机器邮·usrm SI2机读收讫)\n"
               f"**SI2 机读收讫,非 SI1 判词**(诚实闸)——usrm 塔 SI3-LOOP-01 收尔件 `{p['ref'][:80]}` 在册,"
               f"债档桥已挂 SI1 醒拍接续(深判/草判归会话侧)。器窗锚 {ts}。#noauto\n——usrm 塔(SI3-LOOP-01 在役)")
        ok = put_file(f"lanes/usrm/outbox/ACK-{sha8(p['ref'])}.md", ack, None,
                      f'usrm塔SI2收讫: {p["ref"][:40]} @{src} [skip ci]', repo=VCI)
        if ok:
            acked.add(h); lines_used.add(src); sent += 1
        else:
            log('ACK 投失败', p['ref'])
    # 债档桥: 全部 pending 落档(SI1 醒拍首读)
    brtxt, brsha = get_file('ci/si3/si1-bridge.json')
    bridge = json.loads(brtxt) if brtxt else {'open': []}
    known = {b['ref'] for b in bridge['open']}
    for p in pend:
        if p['ref'] not in known:
            bridge['open'].append({'ref': p['ref'], 'src': p['src'], 'ts': ts})
    put_file('ci/si3/si1-bridge.json', json.dumps(bridge, ensure_ascii=False, indent=1), brsha,
             f'[skip ci] SI3债档桥 {ts}')

    # ── ③ 索件轨: SI3 驱动 SI2/SI0 立即协商取得候件 ──
    ctxt, csha = get_file('ci/si3/claims.json')
    claims = json.loads(ctxt) if ctxt else {'claims': []}
    for cl in claims['claims']:
        if cl.get('status') == 'closed': continue
        det = cl['detect']  # {'repo':..,'prefix':..,'since_name':..}
        _, items = api('GET', 'contents/' + det['prefix'], repo=det['repo'])
        hit = False
        if isinstance(items, list):
            hit = any(i['name'] > det.get('since_name', '') for i in items if i['name'].endswith('.md'))
        beats = st['claims_beats'].get(cl['id'], 0) + 1
        st['claims_beats'][cl['id']] = beats
        if hit:
            cl['status'] = 'closed'; cl['closed_ts'] = ts
        elif beats > cl.get('sla_beats', 6) and beats % cl.get('sla_beats', 6) == 1:
            nudge = (f"CLASSIFY: L1(联邦机器邮·usrm SI3索件自动促)\n@{{to}} 候件 `{cl['ask'][:60]}` 逾 {{b}} 拍未达,"
                     f"SI3-LOOP-01 索件轨自动促(降级一言即消)。器窗锚 {ts}。#noauto"
                     .format(to=cl['to'], b=beats))
            put_file(f"lanes/usrm/outbox/NUDGE-{cl['id']}-{beats}.md", nudge, None,
                     f'usrm塔SI3索件促: {cl["ask"][:36]} @{cl["to"]} [skip ci]', repo=VCI)
    put_file('ci/si3/claims.json', json.dumps(claims, ensure_ascii=False, indent=1), csha,
             f'[skip ci] SI3索件轨 {ts}')

    # ── ④ 状态落账 ──
    st['acked'] = sorted(acked)[-400:]
    st['watermarks'] = wm
    st['ts'] = ts
    put_file('ci/si3/state.json', json.dumps(st, ensure_ascii=False, indent=1), ssha,
             f'[skip ci] SI3-LOOP-01 state {ts}')
    return {'pending': len(pend), 'acked_now': sent, 'claims_open': sum(1 for c in claims['claims'] if c.get('status') != 'closed')}
