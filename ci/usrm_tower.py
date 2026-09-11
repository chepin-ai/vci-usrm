#!/usr/bin/env python3
# USRM-TOWER-01 v2 — usrm线SI3循环器（承cfts塔范式第六器注入，SI1迭代我线化）
# 五律: 零定时器 / 自级联 / 防自激三律 / 钥在仓 / 拍尾生债
# v2 增修（usrm SI1 2026-09-11T15:00Z）:
#   ①system prompt 我线化（因果集×律吕·k_c决胜格主线，脱cfts视角）
#   ②cursor 去重（state.seen 录已报件，只报新增——治重复报旧件病）
#   ③公域巷感面补 lanes/usrm/inbox@vci-inbox（机驱直取面入感）
#   ④TASK 消费腿 v1：机读 TASK-*.json 件→转录 SI1 待办钉（ci/si3/claims.json）+
#     可机算类（fetch/echo/ping）即答回执——SI3驱动SI2/SI0雏形
import os, json, time, base64, urllib.request, datetime, subprocess, re

REPO = os.environ.get('GITHUB_REPOSITORY', 'chepin-ai/vci-usrm')
TOK_W = os.environ.get('GITHUB_TOKEN')
TOK_R = os.environ.get('LINE_PAT') or os.environ.get('GITHUB_TOKEN')
HUB = 'chepin-ai/ci-inbox'
PUB = 'chepin-ai/vci-inbox'
SLEEP_S = int(os.environ.get('CASCADE_SLEEP_S', '600'))
MAX_IDLE = int(os.environ.get('CASCADE_MAX_IDLE', '30'))
LINE = 'usrm'

def api(method, path, data=None, repo=None, write=False):
    url = f'https://api.github.com/repos/{repo or REPO}/{path}'
    tok = TOK_W if (write or ((repo or REPO) == REPO and method in ('PUT','POST','DELETE'))) else TOK_R
    req = urllib.request.Request(url, method=method,
        headers={'Authorization': f'Bearer {tok}', 'Accept': 'application/vnd.github+json',
                 'User-Agent': 'usrm-tower-v2'})
    if data is not None: req.data = json.dumps(data).encode()
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            return r.status, json.loads(r.read() or b'{}')
    except urllib.error.HTTPError as e: return e.code, {}
    except Exception as e: return 0, {'err': f'{e.__class__.__name__}: {e}'}

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
        time.sleep(3)
    return False

def patrol(state):
    """感面四面: 毂板尾12(含usrm/广播) + 本仓inbox + 毂侧usrm-repo面 + 公域lanes/usrm/inbox; cursor去重"""
    seen = set(state.get('seen', []))
    events, new_seen = [], []
    def add(kind, ref):
        key = kind + ':' + ref
        if key not in seen:
            events.append({'kind': kind, 'ref': ref}); new_seen.append(key)
    st, items = api('GET', 'contents/公告板', repo=HUB)
    if st == 200:
        names = sorted(i['name'] for i in items if i['name'].endswith('.md'))[-12:]
        for n in names:
            if LINE in n: add('hub-board', n)
            elif re.search(r'OTP@all|OTP@usrm|【S-I|军令|root', n, re.I): add('hub-broadcast', n)
    for repo, tag in [(None, 'inbox'), ('chepin-ai/usrm-repo', 'line-inbox'), (PUB, 'pub-lane')]:
        path = 'contents/inbox' if tag != 'pub-lane' else 'contents/lanes/usrm/inbox'
        st, items = api('GET', path, repo=repo)
        if st == 200 and isinstance(items, list):
            for i in items[-10:]:
                if i['name'] != '.gitkeep': add(tag, i['name'])
    st, items = api('GET', 'contents/公告板', repo=HUB)
    if st == 200:
        board_names = sorted(i['name'] for i in items if i['name'].endswith('.md'))[-8:]
        last_board = state.get('last_board_post', '')
        for n in board_names:
            if n > last_board: add('board-all', n)
        if board_names: state['last_board_post'] = board_names[-1]
    state['seen'] = (list(seen) + new_seen)[-400:]
    return events

def task_consume(state):
    """TASK消费腿v1: 本仓inbox机读TASK-*.json→claims待办钉; 机算类(ping/echo)即答"""
    done = state.get('task_done', [])
    st, items = api('GET', 'contents/inbox')
    results = []
    if st == 200 and isinstance(items, list):
        for i in items:
            n = i['name']
            if not (n.startswith('TASK-') and n.endswith('.json')) or n in done: continue
            txt, _ = get_file('inbox/' + n)
            try: t = json.loads(txt)
            except Exception: continue
            act = (t.get('action') or '')[:80]
            if re.search(r'ping|echo|自检', act, re.I):
                ans = {'task': t.get('task'), 'ans': 'usrm-tower v2 auto-ack: pong', 'ts': datetime.datetime.utcnow().strftime('%Y-%m-%dT%H:%MZ')}
                put_file('receipts/tower/ANS-%s.json' % t.get('task', n), json.dumps(ans, ensure_ascii=False), None, '[skip ci] tower auto-ans')
                results.append({'task': t.get('task'), 'auto': 'answered'})
            else:
                results.append({'task': t.get('task'), 'auto': 'queued-SI1', 'action': act})
            done.append(n)
    state['task_done'] = done[-200:]
    return results

def kimi_work(events, task_results):
    key = os.environ.get('KIMI_API_KEY')
    if not key: return '(无KIMI_API_KEY——巡更仅录)'
    memo_in = json.dumps({'events': events, 'tasks': task_results}, ensure_ascii=False)[:1500]
    req = urllib.request.Request('https://api.moonshot.cn/v1/chat/completions',
        method='POST', data=json.dumps({
            'model': 'kimi-k2.6', 'max_completion_tokens': 12288,
            'messages': [
                {'role': 'system', 'content': '你是 usrm 线 SI3 循环器开工分身。usrm 主线=因果集×律吕·k_c决胜格（三阶律 CUBIC-LAW-01 在役，记录统计/判闸二级制双署）。读候件，用中文答四件:①何事②与 usrm 主线何干③应动何件④生债一条。简。'},
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
    events = patrol(state)
    task_results = task_consume(state)
    idle = state.get('idle', 0) + 1 if not events and not task_results else 0
    memo = kimi_work(events, task_results) if (events or task_results) else ''
    receipt = {'v': 'USRM-TOWER-01-v2', 'ts': ts, 'idle_in': state.get('idle', 0),
               'events': events, 'tasks': task_results, 'verdict_memo': memo[:2000]}
    put_file('receipts/tower/QT-%s.json' % ts, json.dumps(receipt, ensure_ascii=False, indent=1),
             None, '[skip ci] USRM-TOWER v2 beat %s' % ts)
    new_state = {'ts': ts, 'idle': idle, 'events': len(events),
                 'last_board_post': state.get('last_board_post', ''),
                 'seen': state.get('seen', []), 'task_done': state.get('task_done', [])}
    old, sha = get_file('receipts/tower/state.json')
    put_file('receipts/tower/state.json', json.dumps(new_state, ensure_ascii=False, indent=1),
             sha, '[skip ci] USRM-TOWER v2 state')
    # 自级联: 候件非空或idle<MAX_IDLE→自POST dispatch下一拍
    if idle < MAX_IDLE:
        time.sleep(SLEEP_S)
        st, _ = api('POST', 'dispatches', {'event_type': 'usrm-tower-cascade',
                    'client_payload': {'idle': idle, 'prev': ts}}, write=True)
        print('cascade dispatch', st)
    else:
        print('max idle reached, tower sleeps')

if __name__ == '__main__':
    main()
