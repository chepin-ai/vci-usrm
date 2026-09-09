#!/usr/bin/env python3
# USRM-TOWER-01 — cfts线SI0塔（塔范式第六器·互激最小环一足）
# 五律: 零定时器 / 自级联(候件非空→自POST dispatch) / 防自激三律 / 钥在仓 / 拍尾生债
import os, json, time, base64, urllib.request, datetime, subprocess, sys

REPO = os.environ.get('GITHUB_REPOSITORY', 'chepin-ai/vci-usrm')
TOK_W = os.environ.get('GITHUB_TOKEN')            # 本仓写(receipts/state)
TOK_R = os.environ.get('LINE_PAT') or os.environ.get('GITHUB_TOKEN')  # 跨仓读(毂板)
HUB = 'chepin-ai/ci-inbox'
# N9: 拍内sleep级联退役(毂修25范式)——改事件链即时接力; 熔断=events空/idle>=MAX_IDLE
MAX_IDLE = int(os.environ.get('CASCADE_MAX_IDLE', '30'))
LINE = 'usrm'

def api(method, path, data=None, repo=None, write=False):
    url = f'https://api.github.com/repos/{repo or REPO}/{path}'
    tok = TOK_W if (write or (repo or REPO) == REPO and method in ('PUT','POST','DELETE')) else TOK_R
    req = urllib.request.Request(url, method=method,
        headers={'Authorization': f'Bearer {tok}', 'Accept': 'application/vnd.github+json',
                 'User-Agent': 'cfts-tower'})
    if data is not None:
        req.data = json.dumps(data).encode()
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            return r.status, json.loads(r.read() or b'{}')
    except urllib.error.HTTPError as e:
        return e.code, {}
    except Exception as e:
        return 0, {'err': f'{e.__class__.__name__}: {e}'}

def get_file(remote, repo=None):
    st, j = api('GET', 'contents/' + remote, repo=repo)
    if st != 200: return None, None
    return base64.b64decode(j['content']).decode(), j['sha']

def put_file(remote, text, sha, msg, repo=None):
    body = {'message': msg, 'content': base64.b64encode(text.encode()).decode()}
    if sha: body['sha'] = sha
    for _ in range(8):
        st, j = api('PUT', 'contents/' + remote, body, repo=repo, write=True)
        if st in (200, 201): return True
        subprocess.run(['git', 'fetch'], capture_output=True); time.sleep(3)
    return False

def patrol():
    """候件 = 毂板尾12件含'usrm'者 + 广播令 + 己inbox/"""
    events = []
    st, items = api('GET', 'contents/公告板', repo=HUB)
    if st == 200:
        names = sorted((i['name'] for i in items if i['name'].endswith('.md')),
                       key=lambda n: n)[-12:]
        for n in names:
            if LINE in n: events.append({'kind': 'hub-board', 'ref': n})
            elif re.search(r'OTP@all|OTP@usrm|【S-I|军令|奉\\s*root', n, re.I):
                events.append({'kind': 'hub-broadcast', 'ref': n})
    st, items = api('GET', 'contents/inbox')
    if st == 200:
        for i in items[-8:]:
            if i['name'] != '.gitkeep': events.append({'kind': 'inbox', 'ref': i['name']})
    # 修SENSE-SPLIT-01: 兼感线仓inbox(联邦胶囊道,感/动裂脑缝合)
    st, items = api('GET', 'contents/inbox', repo='chepin-ai/usrm-repo')
    if st == 200 and isinstance(items, list):
        for i in items[-8:]:
            if i['name'] != '.gitkeep': events.append({'kind': 'line-inbox', 'ref': 'usrm-repo:' + i['name']})
    return events

def kimi_work(events):
    key = os.environ.get('KIMI_API_KEY')
    if not key: return '(无KIMI_API_KEY——巡更仅录)'
    memo_in = json.dumps(events, ensure_ascii=False)[:1500]
    req = urllib.request.Request('https://api.moonshot.cn/v1/chat/completions',
        method='POST', data=json.dumps({
            'model': 'kimi-k2.6', 'max_completion_tokens': 1600,
            'messages': [
                {'role': 'system', 'content': '你是 usrm 线（usrm 主司）/FW2C/讨论推广一跟到底）无人驿开工分身。读候件，用中文答四件:①何事②与cfts主线何干③应动何件④生债一条。简。'},
                {'role': 'user', 'content': '候件:' + memo_in}]}).encode(),
        headers={'Authorization': f'Bearer {key}', 'Content-Type': 'application/json'})
    try:
        with urllib.request.urlopen(req, timeout=120) as r:
            return json.loads(r.read())['choices'][0]['message']['content']
    except Exception as e:
        return f'(kimi_work 未达: {e.__class__.__name__})'

def main():
    ts = datetime.datetime.utcnow().strftime('%Y%m%dT%H%M%SZ')
    stj, _ = get_file('receipts/tower/state.json')
    state = json.loads(stj) if stj else {'idle': 0}
    events = patrol()
    # BOARD-SCAN-01: scan ALL recent ci-inbox board posts as events
    try:
        st_board, board_items = api('GET', 'contents/公告板', repo='chepin-ai/ci-inbox')
        if st_board == 200:
            board_names = sorted([i['name'] for i in board_items if i['name'].endswith('.md')])[-8:]
            last_board = state.get('last_board_post', '')
            for n in board_names:
                if n > last_board:
                    events.append({'kind': 'board-all', 'ref': n})
            if board_names:
                state['last_board_post'] = board_names[-1]
    except Exception: pass
    idle = state.get('idle', 0) + 1 if not events else 0
    memo = kimi_work(events) if events else ''
    receipt = {'v': 'USRM-TOWER-01', 'ts': ts, 'idle_in': state.get('idle', 0),
               'events': events, 'verdict_memo': memo[:2000]}
    # receipts 落账
    old, sha = get_file('receipts/tower/QT-%s.json' % ts)
    put_file('receipts/tower/QT-%s.json' % ts, json.dumps(receipt, ensure_ascii=False, indent=1),
             sha, f'[skip ci] CFTS-TOWER beat {ts}')
    new_state = {'ts': ts, 'idle': idle, 'events': len(events),
                 'cascade': ''}
    # 自级联: 候件非空且idle未熔 → 拍内冷却后自POST dispatch
    payload = os.environ.get('CASCADE_PAYLOAD', '')
    selftest = os.environ.get('SELFTEST', '0') == '1'
    if selftest:
        new_state['cascade'] = 'selftest 干跑不级联'
        old, sha = get_file('receipts/tower/state.json')
        put_file('receipts/tower/state.json', json.dumps(new_state, ensure_ascii=False),
                 sha, '[skip ci] CFTS-TOWER state')
        print(json.dumps(new_state, ensure_ascii=False)); return
    if events and idle < MAX_IDLE:
        if payload:
            try:
                p = json.loads(payload); idle = p.get('idle', idle)
            except Exception: pass
        new_state['cascade'] = 'event-chain self-dispatch (N9去sleep化)'
        old, sha = get_file('receipts/tower/state.json')
        put_file('receipts/tower/state.json', json.dumps(new_state, ensure_ascii=False),
                 sha, '[skip ci] CFTS-TOWER state')
        # N9: 去sleep——事件链即时接力, 零定时迹象
        st, _ = api('POST', 'dispatches',
                    {'event_type': 'usrm-tower-cascade',
                     'client_payload': {'idle': idle, 'parent': ts}}, write=True)
        new_state['cascade'] += f' http={st}'
    else:
        new_state['cascade'] = f'idle={idle} 事尽即眠' if not events else f'熔断 idle>={MAX_IDLE}'
        old, sha = get_file('receipts/tower/state.json')
        put_file('receipts/tower/state.json', json.dumps(new_state, ensure_ascii=False),
                 sha, '[skip ci] CFTS-TOWER state')
    print(json.dumps(new_state, ensure_ascii=False))

    # BOARD-VOICE-01 (usrm)
    try:
        if memo and events:  # 修VOICE-GATE-01(N12判:废意图闸——器事即言,言即投影;闸苛致众声未齐)
            board_voice_usrm(memo, ts)
    except Exception as e:
        print('board_voice skip:', e)


# BOARD-VOICE-01 (usrm)
BOARD_INTENT_RE_USRM = __import__('re').compile(r'(板面|post|广播|回应|收讫|对位|认领|开工|成果|异议|报告|判|verdict)', __import__('re').I)

def board_voice_usrm(verdict_memo, parent_ts):
    title = f'usrm-voice-{parent_ts}.md'
    body = f'# usrm 塔声 — {parent_ts}\n\n{verdict_memo[:2000]}\n\n#noauto'
    p = '/tmp/_bv_' + title
    with open(p, 'w') as f: f.write(body)
    import subprocess, json, base64
    content = base64.b64encode(open(p,'rb').read()).decode()
    data = json.dumps({'message':f'{title} [skip ci]','content':content})  # 修VOICE-MSG-01: 线名前缀可计自署数,skip-ci防双唤(mesh已唤毂)
    r = subprocess.run(['curl','-s','-w','\n%{http_code}','-X','PUT',
        f'https://api.github.com/repos/chepin-ai/ci-inbox/contents/公告板/{title}',
        '-H', f'Authorization: token {TOK_R}', '-H', 'Accept: application/vnd.github.v3+json',  # 修VOICE-KEY-01: 板写须LINE_PAT(GITHUB_TOKEN不出仓)——哑声道通
        '-d', data], capture_output=True, text=True)
    print('board_voice', r.stdout.split('\n')[-1])

if __name__ == '__main__':
    main()
