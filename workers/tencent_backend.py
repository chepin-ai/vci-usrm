#!/usr/bin/env python3
# tencent_backend.py — 腾讯量子云适配器 v0(W83 全局令·预置件)
# 纪律:token 只走 env TC_TOKEN_TENCENT(E804);无 token=全干跑可机检;设备勿硬编码(启动 device/find)。
# 实测在案:tensorcircuit 1.9.1 本地模拟器 Bell {'00':~512,'11':~512} PASS;云端匿名 device/find → unauthorized(凭证闸候 token)。
import os, json, time, hashlib

BASE = 'https://quantum.tencent.com/cloud/quk/'
TASKTABLE = os.environ.get('TC_TASKTABLE', '/tmp/.tc-tasks.jsonl')  # 幂等任务表(重试去重)

def _token():
    t = os.environ.get('TC_TOKEN_TENCENT')
    return t  # None → dry-run

def list_devices():
    """云端 device/find;无 token 返回静态公开目录快照(标注 static-snapshot)。"""
    tok = _token()
    if not tok:
        return {'mode': 'dry-run/static-snapshot', 'devices': [
            'tianji_m2(59b QPU)', 'tianxuan_s2(40b QPU)', 'tianji_s2(20b QPU)',
            'tianji_m2v16s1(20b VM)', 'tianji_m2v16s2(16b VM)', 'simulator:tc']}
    import urllib.request
    req = urllib.request.Request(BASE + 'device/find', data=b'{}',
        headers={'Content-Type': 'application/json', 'Authorization': 'Bearer ' + tok})
    return json.loads(urllib.request.urlopen(req, timeout=30).read())

def local_bell_smoke(shots=1024):
    """本地模拟器冒烟(无需 token)——classical-sim 档,灰标照带。"""
    import tensorcircuit as tc
    c = tc.Circuit(2); c.h(0); c.cx(0, 1)
    return c.sample(shots, allow_state=True, format='count_dict_bin')

def submit_qasm(qasm, device='simulator:tc', shots=1024, remarks='', idem=None, dry=None):
    """幂等提交:idem 键入任务表,重复调用直接回旧 task_id(防重复计费)。"""
    idem = idem or hashlib.sha256((qasm + device + str(shots) + remarks).encode()).hexdigest()[:16]
    if os.path.exists(TASKTABLE):
        for line in open(TASKTABLE):
            r = json.loads(line)
            if r.get('idem') == idem and r.get('task_id'):
                return {'mode': 'idempotent-replay', 'task_id': r['task_id']}
    tok = _token()
    if dry is None: dry = tok is None
    if dry:
        rec = {'idem': idem, 'ts': time.strftime('%Y-%m-%dT%H:%MZ', time.gmtime()),
               'device': device, 'shots': shots, 'mode': 'dry-run(无token,未上云)', 'qasm_sha': hashlib.sha256(qasm.encode()).hexdigest()[:16]}
        open(TASKTABLE, 'a').write(json.dumps(rec) + '\n')
        return rec
    import urllib.request
    body = [{'device': device, 'shots': shots, 'source': qasm, 'version': '1',
             'lang': 'OPENQASM', 'prior': 1, 'remarks': remarks or idem, 'group': 'ci-os'}]
    req = urllib.request.Request(BASE + 'task/submit', data=json.dumps(body).encode(),
        headers={'Content-Type': 'application/json', 'Authorization': 'Bearer ' + tok})
    data = json.loads(urllib.request.urlopen(req, timeout=30).read())
    if 'err' in data: raise RuntimeError(data['err'])
    tid = data['tasks'][0]['id']
    open(TASKTABLE, 'a').write(json.dumps({'idem': idem, 'task_id': tid,
        'ts': time.strftime('%Y-%m-%dT%H:%MZ', time.gmtime()), 'mode': 'wet'}) + '\n')
    return {'mode': 'wet', 'task_id': tid}

def poll_task(task_id, timeout_s=3600, backoff=5):
    """轮询 task/detail;自带超时+退避(平台无公开队列ETA)。"""
    tok = _token()
    if not tok: return {'mode': 'dry-run', 'note': '无token不可轮询'}
    import urllib.request
    t0 = time.monotonic()
    while True:
        req = urllib.request.Request(BASE + 'task/detail', data=json.dumps({'id': task_id}).encode(),
            headers={'Content-Type': 'application/json', 'Authorization': 'Bearer ' + tok})
        d = json.loads(urllib.request.urlopen(req, timeout=30).read())
        if 'err' in d: raise RuntimeError(d['err'])
        st = d['task'].get('state')
        if st == 'completed': return d['task'].get('result', {}).get('counts')
        if st == 'failed': raise RuntimeError(d['task'].get('error', d['task']))
        if time.monotonic() - t0 > timeout_s: raise TimeoutError(task_id)
        time.sleep(backoff); backoff = min(backoff * 2, 60)

if __name__ == '__main__':
    print(json.dumps(list_devices(), ensure_ascii=False)[:200])
    print('bell:', local_bell_smoke())
