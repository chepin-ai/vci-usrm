#!/usr/bin/env python3
# KEY-SYNC-01 v2 · 联邦密钥中继:可编程(names/targets/rename) · 名值分离 · 事件驱动 · 幂等
import os, json, base64, time, urllib.request, urllib.error, subprocess, datetime
from nacl.public import PublicKey, SealedBox
from nacl.encoding import Base64Encoder

PAT = os.environ.get('SYNC_PAT') or os.environ.get('AI_FULL_PAT')
DEFAULT_TARGETS = ['vci-aiq','vci-qlv','vci-lgt','vci-qfa','vci-qtlv','vci-control']
DEFAULT_SET = ['BLUEQUBIT_GMAIL','BLUEQUBIT_PW','CF_ACCOUNT_API_TOKEN','CF_ACCOUNT_ID',
 'CF_R2_USER_ACCESS_KEY_ID','CF_R2_USER_SECRET_ACCESS_KEY','CI_OPS_LINE_KEY','FORMAFLOW_CMD_AUTH',
 'GH_TOTP_SEED','IBMID_PW','IBM_TOTP_SECRET','KAGGLE_KEY','KAGGLE_USERNAME','OTP_PHONE','QUAFU_KEY',
 'SUPABASE_PUBLISHABLE_KEY','SUPABASE_SECRET_KEY','SUPABASE_URL',
 'LONGCAT_AK_N1','LONGCAT_AK_N2','LONGCAT_AK_N3','LONGCAT_AK_N4','LONGCAT_AK_N5',
 'LONGCAT_SK_N4','LONGCAT_SK_N5','NODE_SK_N4','NODE_SK_N5','MS_TOTP_SEED_V2']

csv = lambda s: [x.strip() for x in (s or '').split(',') if x.strip()]
TARGETS = csv(os.environ.get('IN_TARGETS')) or DEFAULT_TARGETS
SYNC_SET = csv(os.environ.get('IN_NAMES')) or [n for n in DEFAULT_SET if os.environ.get(n)]
try: RENAME = json.loads(os.environ.get('IN_RENAME') or '{}')
except Exception: RENAME = {}

def gh(path, method='GET', data=None):
    for i in range(5):
        req = urllib.request.Request('https://api.github.com'+path,
            data=json.dumps(data).encode() if data is not None else None,
            headers={'Authorization':f'token {PAT}','Accept':'application/vnd.github+json',
                     'Content-Type':'application/json'}, method=method)
        try:
            r = urllib.request.urlopen(req, timeout=30)
            return r.status, json.loads(r.read() or b'{}')
        except urllib.error.HTTPError as e:
            if e.code in (403,429,502,503) and i<4: time.sleep(8*(i+1)); continue
            return e.code, {}
        except Exception: time.sleep(5*(i+1))
    return None, {}

def seal(repo, name, value):
    s,k = gh(f'/repos/chepin-ai/{repo}/actions/secrets/public-key')
    if s != 200: return f'PK{s}'
    sb = SealedBox(PublicKey(k['key'].encode(), Base64Encoder))
    enc = base64.b64encode(sb.encrypt(value.encode())).decode()
    s2,_ = gh(f'/repos/chepin-ai/{repo}/actions/secrets/{name}','PUT',
              {'encrypted_value':enc,'key_id':k['key_id']})
    return s2

def set_var(repo, name, value):
    s,_ = gh(f'/repos/chepin-ai/{repo}/actions/variables/{name}')
    if s == 200:
        s2,_ = gh(f'/repos/chepin-ai/{repo}/actions/variables/{name}','PATCH',{'name':name,'value':value})
    else:
        s2,_ = gh(f'/repos/chepin-ai/{repo}/actions/variables','POST',{'name':name,'value':value})
    return s2

def main():
    ts = datetime.datetime.utcnow().strftime('%Y%m%dT%H%M%SZ')
    pairs = []
    for n in SYNC_SET:
        v = os.environ.get(n)
        if not v: continue
        pairs.append((n, v))
        for dst in RENAME.get(n, []): pairs.append((dst, v))
    print(f'[key-sync] pairs={len(pairs)} targets={len(TARGETS)} (values masked)')
    lines = [f'# KEY-SYNC-01 v2 receipt {ts}', f'- source_repo: {os.environ.get("GITHUB_REPOSITORY")}',
             f'- run: {os.environ.get("GITHUB_RUN_ID")}', '',
             '| name | ' + ' | '.join(TARGETS) + ' |', '|---|' + '---|'*len(TARGETS)]
    for name, val in pairs:
        row = [str(seal(t, name, val)) for t in TARGETS]
        lines.append('| ' + name + ' | ' + ' | '.join(row) + ' |')
        print('[key-sync]', name, row)
    v = os.environ.get('SUPABASE_URL')
    if v and os.environ.get('IN_SYNC_VAR','1') == '1':
        row = [str(set_var(t, 'SUPABASE_URL', v)) for t in TARGETS]
        lines += ['', '## Variables', '| SUPABASE_URL | ' + ' | '.join(row) + ' |']
        print('[key-sync][var] SUPABASE_URL', row)
    os.makedirs('receipts/key-sync', exist_ok=True)
    fn = f'receipts/key-sync/{ts}.md'
    open(fn,'w').write('\n'.join(lines)+'\n')
    subprocess.run(['git','config','user.name','key-sync'],check=True)
    subprocess.run(['git','config','user.email','key-sync@federation'],check=True)
    subprocess.run(['git','config','http.version','HTTP/1.1'],check=True)
    subprocess.run(['git','add',fn],check=True)
    subprocess.run(['git','commit','-q','-m',f'KEY-SYNC-01 receipt {ts}'],check=True)
    for i in range(8):
        subprocess.run(['git','fetch','-q','origin','main']); subprocess.run(['git','rebase','-q','origin/main'])
        if subprocess.run(['git','push','-q','origin','HEAD:main']).returncode == 0:
            print('[key-sync] receipt pushed', fn); return
        time.sleep(5)
    print('[key-sync] WARN receipt push failed')
main()
