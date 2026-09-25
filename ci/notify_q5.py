#!/usr/bin/env python3
# NOTIFY-Q5-01 · 跨域通报摆渡:QI_PAT只在runner内存,值不落文本
import os, json, base64, time, urllib.request, urllib.error, subprocess, datetime
QPAT = os.environ.get('QI_PAT') or os.environ.get('GH_PAT_QI_FULL')
DECL = open('board/PIVOT-01-DECLARATION-20260925.md').read()
def q(path, method='GET', data=None):
    for i in range(5):
        req = urllib.request.Request('https://api.github.com'+path,
            data=json.dumps(data).encode() if data is not None else None,
            headers={'Authorization':f'token {QPAT}','Accept':'application/vnd.github+json',
                     'Content-Type':'application/json'}, method=method)
        try:
            r = urllib.request.urlopen(req, timeout=30)
            return r.status, json.loads(r.read() or b'{}')
        except urllib.error.HTTPError as e:
            if e.code in (403,429,502,503) and i<4: time.sleep(8*(i+1)); continue
            return e.code, {}
        except Exception: time.sleep(5*(i+1))
    return None, {}
def main():
    s,me = q('/user'); print('[q5] auth as:', me.get('login') if s==200 else s)
    s,repos = q('/user/repos?per_page=100&affiliation=owner')
    names = sorted(r['name'] for r in repos) if s==200 else []
    print('[q5] repos visible:', len(names))
    ts = datetime.datetime.utcnow().strftime('%Y%m%dT%H%M%SZ')
    lines=[f'# NOTIFY-Q5-01 receipt {ts}', f'- auth: {me.get("login")}', f'- repos: {len(names)}', '',
           '| repo | PUT |', '|---|---|']
    for name in names:
        path=f'board/PIVOT-01-DECLARATION-20260925.md'
        s0,old = q(f'/repos/chepin-qi/{name}/contents/{path}')
        d={'message':'NOTICE: PIVOT-01 中枢宣告(跨域摆渡自chepin-ai联邦)','content':base64.b64encode(DECL.encode()).decode()}
        if s0==200: d['sha']=old['sha']
        s2,_=q(f'/repos/chepin-qi/{name}/contents/{path}','PUT',d)
        lines.append(f'| {name} | {s2} |'); print('[q5]',name,s2,flush=True)
        time.sleep(2)
    os.makedirs('receipts/notify-q5',exist_ok=True)
    fn=f'receipts/notify-q5/{ts}.md'; open(fn,'w').write('\n'.join(lines)+'\n')
    subprocess.run(['git','config','user.name','pivot-01'],check=True)
    subprocess.run(['git','config','user.email','pivot@federation'],check=True)
    subprocess.run(['git','config','http.version','HTTP/1.1'],check=True)
    subprocess.run(['git','add',fn],check=True); subprocess.run(['git','commit','-q','-m',f'NOTIFY-Q5-01 receipt {ts}'],check=True)
    for i in range(8):
        subprocess.run(['git','fetch','-q','origin','main']); subprocess.run(['git','rebase','-q','origin/main'])
        if subprocess.run(['git','push','-q','origin','HEAD:main']).returncode==0:
            print('[q5] receipt pushed'); return
        time.sleep(5)
main()
