#!/usr/bin/env python3
# NOTIFY-Q5-01 v2 · 硬化:早回执+全程异常捕获+布尔级诊断(值不落文本)
import os, json, base64, time, urllib.request, urllib.error, subprocess, datetime, traceback
QPAT = os.environ.get('QI_PAT') or os.environ.get('GH_PAT_QI_FULL') or ''
LOG=[]
def log(*a): print(*a,flush=True); LOG.append(' '.join(str(x) for x in a))
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
            try: body=e.read()[:120]
            except Exception: body=b''
            return e.code, {'_err':body.decode('utf-8','ignore')}
        except Exception as ex:
            time.sleep(5*(i+1)); last=str(type(ex).__name__)
    return None, {'_err':last}
def commit_receipt(ts):
    subprocess.run(['git','config','user.name','pivot-01'])
    subprocess.run(['git','config','user.email','pivot@federation'])
    subprocess.run(['git','config','http.version','HTTP/1.1'])
    os.makedirs('receipts/notify-q5',exist_ok=True)
    fn=f'receipts/notify-q5/{ts}.md'
    open(fn,'w').write('# NOTIFY-Q5-01 receipt '+ts+'\n\n```\n'+'\n'.join(LOG)+'\n```\n')
    subprocess.run(['git','add',fn])
    subprocess.run(['git','commit','-q','-m','NOTIFY-Q5-01 receipt '+ts])
    for i in range(8):
        subprocess.run(['git','fetch','-q','origin','main']); subprocess.run(['git','rebase','-q','origin/main'])
        if subprocess.run(['git','push','-q','origin','HEAD:main']).returncode==0:
            log('receipt pushed '+fn); return
        time.sleep(5)
    log('WARN receipt push failed')
def main():
    ts=datetime.datetime.utcnow().strftime('%Y%m%dT%H%M%SZ')
    try:
        log('[q5] QI_PAT present:', bool(QPAT))
        try:
            DECL=open('board/PIVOT-01-DECLARATION-20260925.md').read(); log('[q5] decl bytes:',len(DECL))
        except Exception as e:
            log('[q5] DECL missing:',e); DECL='# PIVOT-01 (fallback decl unavailable)'
        commit_receipt(ts+'-a')  # 早回执:证明脚本跑到这里
        s,me=q('/user'); log('[q5] /user ->',s, me.get('login') if isinstance(me,dict) else '')
        s,repos=q('/user/repos?per_page=100&affiliation=owner')
        names=sorted(r['name'] for r in repos) if s==200 and isinstance(repos,list) else []
        log('[q5] repos:',len(names), names[:20])
        for name in names:
            path='board/PIVOT-01-DECLARATION-20260925.md'
            s0,old=q(f'/repos/chepin-qi/{name}/contents/{path}')
            d={'message':'NOTICE: PIVOT-01 中枢宣告(跨域摆渡自chepin-ai联邦)','content':base64.b64encode(DECL.encode()).decode()}
            if s0==200 and isinstance(old,dict) and old.get('sha'): d['sha']=old['sha']
            s2,b2=q(f'/repos/chepin-qi/{name}/contents/{path}','PUT',d)
            log('[q5]',name,s2, (b2.get('_err') if isinstance(b2,dict) else ''))
            time.sleep(2)
    except Exception:
        log('EXC:'); log(traceback.format_exc()[:1500])
    commit_receipt(ts+'-b')
main()
