#!/usr/bin/env python3
# EXP-049 轮询器自愈启动器 — 醒拍一键: 装pyquafu+供quafu.env(600)+起setsid轮询
# 钥自 vault bundle 运行时取, 本件零密钥
import sys, os, subprocess
sys.path.insert(0, '/mnt/agents/output/resurrect_kit')
from resurrect import resurrect
G, canon, now, put_file, HMACm, CA, bundle, kv = resurrect('8f7f305a242dfe5f922763ae80a978','4ad56ce02eccbed76e61bc9856c14d2588')
q = bundle['quantum']['quafu']
envp = os.path.expanduser('~/.keys/quafu.env')
os.makedirs(os.path.dirname(envp), exist_ok=True)
with open(envp, 'w') as f:
    f.write(f"QUAFU_API_KEY={q['key']}\nQUAFU_USER={q['user']}\nQUAFU_CONSOLE={q.get('console','')}\n")
os.chmod(envp, 0o600)
try:
    import quafu
except ImportError:
    subprocess.run([sys.executable, '-m', 'pip', 'install', '-q', '--user', 'pyquafu', '--no-deps', 'autograd', 'ply'], timeout=300)
import importlib, site; importlib.reload(site)
os.chdir('/mnt/agents/output/kc')
log = open('exp049_retrieve.log', 'a')
p = subprocess.Popen(['setsid', 'nohup', sys.executable, 'exp049_direct.py', '--retrieve', '14400'],
                     stdout=log, stderr=subprocess.STDOUT, stdin=subprocess.DEVNULL)
print('poller started pid', p.pid, now())
