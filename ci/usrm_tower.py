#!/usr/bin/env python3
# USRM-TOWER-01 — cfts线SI0塔（塔范式第六器·互激最小环一足）
# 五律: 零定时器 / 自级联(候件非空→自POST dispatch) / 防自激三律 / 钥在仓 / 拍尾生债
import os, json, time, base64, urllib.request, datetime, subprocess, sys

REPO = os.environ.get('GITHUB_REPOSITORY', 'chepin-ai/vci-usrm')
TOK_W = os.environ.get('GITHUB_TOKEN')            # 本仓写(receipts/state)
TOK_R = os.environ.get('LINE_PAT') or os.environ.get('GITHUB_TOKEN')  # 跨仓读(毂板)
HUB = 'chepin-ai/ci-inbox'
SLEEP_S = int(os.environ.get('CASCADE_SLEEP_S', '600'))
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
    """候件 = 毂板尾12件含'usrm'者 + 己inbox/"""
    events = []
    st, items = api('GET', 'contents/公告板', repo=HUB)
    if st == 200:
        names = sorted((i['name'] for i in items if i['name'].endswith('.md')),
                       key=lambda n: n)[-12:]
        for n in names:
            if LINE in n: events.append({'kind': 'hub-board', 'ref': n})
    st, items = api('GET', 'contents/inbox')
    if st == 200:
        for i in items[-8:]:
            if i['name'] != '.gitkeep': events.append({'kind': 'inbox', 'ref': i['name']})
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
        new_state['cascade'] = 'sleep %ds then self-dispatch' % SLEEP_S
        old, sha = get_file('receipts/tower/state.json')
        put_file('receipts/tower/state.json', json.dumps(new_state, ensure_ascii=False),
                 sha, '[skip ci] CFTS-TOWER state')
        time.sleep(SLEEP_S)  # 拍内冷却(非定时器)
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

if __name__ == '__main__':
    main()
