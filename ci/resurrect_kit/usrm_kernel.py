"""usrm_kernel — 提炼核: 一次import恢复全作战力(wave-212, root令"活跃核提炼至SI持续运行")
用法: from usrm_kernel import *  →  TOK/HD/ghj/ghput_retry/load_json/opener/canon/CA/kv 全备
"""
import json, base64, time, datetime, os, urllib.request, urllib.parse, urllib.error, hashlib, hmac as _hmac

def bootstrap(resurrect_out):
    """resurrect()之出→全作战力. 返 dict 含 TOK/HD/函数群."""
    import jwt as _jwt  # 惰性: resurrect已插vendor径
    G_, canon, now, put_file, HMACm, CA, bundle, kv = resurrect_out
    if isinstance(CA, str): CA = bytes.fromhex(CA)
    _ni = int(time.time())
    _j = _jwt.encode({'iat':_ni-60,'exp':_ni+540,'iss':kv['GH_APP_ID']}, bundle['gh_app_pem'], algorithm='RS256')
    _req = urllib.request.Request(f"https://api.github.com/app/installations/{kv['GH_APP_INSTALLATION']}/access_tokens",
                                  data=b'{}', method='POST',
                                  headers={'Authorization':'Bearer '+_j,'Accept':'application/vnd.github+json','User-Agent':'usrm-si'})
    TOK = json.loads(urllib.request.urlopen(_req, timeout=40).read())['token']
    HD = {'Authorization':'token '+TOK,'Accept':'application/vnd.github+json','User-Agent':'usrm-si'}
    _quote = urllib.parse.quote
    def gh_raw(m,url,hd=None,data=None,params=None,tries=4):
        url=_quote(url,safe=':/?&=#%')
        if params: url += ('&' if '?' in url else '?')+urllib.parse.urlencode(params)
        for i in range(tries):
            try:
                return urllib.request.urlopen(urllib.request.Request(url,data=data,method=m,headers=hd or HD),timeout=40)
            except urllib.error.HTTPError as e:
                if e.code in (502,503,429) and i<tries-1: time.sleep(6+i*3); continue
                raise
            except Exception:
                if i<tries-1: time.sleep(4+i*2); continue
                raise
    def ghj(m,url,hd=None,data=None,params=None):
        raw = gh_raw(m,url,hd,data,params).read().decode('utf-8')
        try: return json.loads(raw)
        except Exception: return {'_raw':raw}
    def ghput_retry(path,content,msg,repo,tries=6):
        b64 = base64.b64encode(content.encode('utf-8') if isinstance(content,str) else content).decode()
        for i in range(tries):
            try:
                cur = ghj('GET', f'https://api.github.com/repos/{repo}/contents/{path}')
            except urllib.error.HTTPError as e:
                if e.code==404: cur = {}
                else: raise
            body = {'message':msg,'content':b64}
            if isinstance(cur,dict) and 'sha' in cur: body['sha']=cur['sha']
            try:
                ghj('PUT', f'https://api.github.com/repos/{repo}/contents/{path}', data=json.dumps(body).encode())
                return 200
            except urllib.error.HTTPError as e:
                if e.code==409 and i<tries-1: time.sleep(2+i); continue
                return e.code
        return 'fail'
    def load_json(repo, path):
        c = ghj('GET', f'https://api.github.com/repos/{repo}/contents/{path}')
        return json.loads(base64.b64decode(c['content']).decode('utf-8'))
    class NoRedirect(urllib.request.HTTPRedirectHandler):
        def redirect_request(self, req, fp, code, msg, headers, newurl): return None
    opener = urllib.request.build_opener(NoRedirect)
    return dict(TOK=TOK, HD=HD, gh_raw=gh_raw, ghj=ghj, ghput_retry=ghput_retry,
                load_json=load_json, opener=opener, canon=canon, CA=CA, kv=kv, bundle=bundle,
                HMACm=HMACm, G_=G_, now=now, put_file=put_file)
