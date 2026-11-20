#!/usr/bin/env python3
# KAT for USRM-TOWER-01 kimi_work — 零网络零机密(mock urlopen; dummy key 值永不打印)
# 跑法: python3 ci/test_usrm_tower.py
import importlib.util, io, json, os, sys, urllib.error

HERE = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location('usrm_tower', os.path.join(HERE, 'usrm_tower.py'))
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)

DUMMY = 'dummy-not-a-real-key'  # 假值,仅验名不验值
fails = []

def check(name, cond):
    print(('PASS ' if cond else 'FAIL ') + name)
    if not cond: fails.append(name)

class FakeResp:
    def __init__(self, payload): self.payload = payload
    def __enter__(self): return self
    def __exit__(self, *a): return False
    def read(self): return json.dumps(self.payload).encode()

# 1) 失败关闭: 无 KIMI_API_KEY → 固定哨兵句, 不发请求
os.environ.pop('KIMI_API_KEY', None)
r = m.kimi_work([{'kind': 'k', 'ref': 'r'}], [{'task': 't'}])
check('fail-closed 无钥哨兵', r == '(无KIMI_API_KEY——巡更仅录)')

# 2) 成功道: mock urlopen 回标准件 → 返回 content; 校验端点/模型/授权头形
captured = {}
def fake_urlopen_ok(req, timeout=None):
    captured['url'] = req.full_url
    captured['auth_ok'] = req.headers.get('Authorization', '').startswith('Bearer ')
    captured['body'] = json.loads(req.data.decode())
    return FakeResp({'choices': [{'message': {'content': '①何事②何干③何件④生债'}}]})
os.environ['KIMI_API_KEY'] = DUMMY
orig = m.urllib.request.urlopen
m.urllib.request.urlopen = fake_urlopen_ok
try:
    r = m.kimi_work([{'kind': 'inbox', 'ref': 'TASK-X.json'}], [{'task': 'T1', 'auto': 'answered'}])
finally:
    m.urllib.request.urlopen = orig
check('成功道返回 content', r == '①何事②何干③何件④生债')
check('成功道端点', captured.get('url') == 'https://api.moonshot.cn/v1/chat/completions')
check('成功道模型保持 kimi-k2.6', captured.get('body', {}).get('model') == 'kimi-k2.6')
check('成功道授权头形', captured.get('auth_ok') is True)
check('成功道候件入体', 'TASK-X.json' in json.dumps(captured.get('body', {}), ensure_ascii=False))

# 3) HTTP 错(如401/404) → 未达支记 HTTPError, 不抛不穿
def fake_urlopen_http(req, timeout=None):
    raise urllib.error.HTTPError(req.full_url, 401, 'Unauthorized', {}, io.BytesIO(b'{}'))
m.urllib.request.urlopen = fake_urlopen_http
try:
    r = m.kimi_work([{'kind': 'k', 'ref': 'r'}], [])
finally:
    m.urllib.request.urlopen = orig
check('HTTP错失败关闭', r == '(kimi_work 未达: HTTPError)')

# 4) 超时/网络错 → 未达支记 TimeoutError
def fake_urlopen_to(req, timeout=None):
    raise TimeoutError('timed out')
m.urllib.request.urlopen = fake_urlopen_to
try:
    r = m.kimi_work([{'kind': 'k', 'ref': 'r'}], [])
finally:
    m.urllib.request.urlopen = orig
os.environ.pop('KIMI_API_KEY', None)
check('超时失败关闭', r == '(kimi_work 未达: TimeoutError)')

print('KAT: %d pass, %d fail' % (4 + 3 + 1 - len(fails) + 0, len(fails)))
sys.exit(1 if fails else 0)
