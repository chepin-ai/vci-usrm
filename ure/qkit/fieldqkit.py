# fieldqkit v1 — QF-OS 通用/可复用量子接口共享库（canonical in-repo）
# 三引擎统一面: numpy(本地态矢,without基座) / quafu(北量子院云) / qr(QuantumRings scarlet)
# 纪律: 优先 QuantumRings(并发主引擎); quafu 同账户并发降级→走顺序/异步轮询
# 参数序差异已封装: quafu qc.ry(q,θ) vs QR qc.ry(θ,q) —— 调用方永不感知
import json, math, time
def _counts_numpy(qc_ops, nq, shots):
    import numpy as np
    st=np.zeros(2**nq,complex); st[0]=1.0
    def apply1(g,q,th=None):
        nonlocal st
        H=2**-0.5*np.array([[1,1],[1,-1]],complex)
        if g=='h': M=H
        elif g=='ry':
            c,s=math.cos(th/2),math.sin(th/2); M=np.array([[c,-s],[s,c]],complex)
        elif g=='rz':
            M=np.diag([1,complex(math.cos(th),math.sin(th))])
        elif g=='x': M=np.array([[0,1],[1,0]],complex)
        else: raise ValueError(g)
        n=st.shape[0]; out=np.zeros_like(st)
        for i in range(n):
            b=(i>>q)&1
            j=i^(1<<q)
            if b==0: out[i]+=M[0,0]*st[i]; out[j]+=M[1,0]*st[i]
            else:    out[j]+=M[0,1]*st[i]; out[i]+=M[1,1]*st[i]
        st=out
    def cnot(c_,t_):
        nonlocal st
        n=st.shape[0]; out=np.zeros_like(st)
        for i in range(n):
            if (i>>c_)&1: out[i^(1<<t_)]+=st[i]
            else: out[i]+=st[i]
        st=out
    for op in qc_ops:
        if op[0]=='cnot': cnot(op[1],op[2])
        else: apply1(op[0],op[1],op[2] if len(op)>2 else None)
    import numpy as np
    probs=np.abs(st)**2
    rng=np.random.default_rng()
    samp=rng.choice(2**nq,size=shots,p=probs)
    counts={}
    for s in samp:
        k=format(s,'0%db'%nq)[::-1]  # little-endian string like cloud convention
        counts[k]=counts.get(k,0)+1
    exact={format(i,'0%db'%nq)[::-1]:float(p) for i,p in enumerate(probs) if p>1e-9}
    return counts, exact
BELL=[('h',0),('cnot',0,1)]
GHZ3=[('h',0),('cnot',0,1),('cnot',1,2)]
def chsh_settings():
    a,a2,b,b2=0.0,math.pi/2,math.pi/4,-math.pi/4
    return {'a_b':(a,b),'a_b2':(a,b2),'a2_b':(a2,b),'a2_b2':(a2,b2)}
def _chsh_circuit(theta_a,theta_b):
    # measure in rotated bases: ry(-θ) then Z-measure
    return [('h',0),('cnot',0,1),('ry',0,-theta_a),('ry',1,-theta_b)]
def list_engines(): return ['numpy','quafu','qr']
def run(ops, nq, engine='numpy', shots=1024, creds=None, backend=None, wait=True):
    if engine=='numpy':
        c,e=_counts_numpy(ops,nq,shots); return {'engine':'numpy','counts':c,'exact':e}
    if engine=='quafu':
        from quafu import User, Task, QuantumCircuit
        u=User(api_token=creds['QUAFU_KEY']); t=Task(user=u)
        qc=QuantumCircuit(nq)
        for op in ops:
            if op[0]=='h': qc.h(op[1])
            elif op[0]=='cnot': qc.cnot(op[1],op[2])
            elif op[0]=='ry': qc.ry(op[1],op[2])
            elif op[0]=='rz': qc.rz(op[1],op[2])
            elif op[0]=='x': qc.x(op[1])
        qc.measure(list(range(nq)))
        t.config(backend=backend or 'ScQ-Sim10',shots=shots)
        res=t.send(qc,wait=False)
        if not wait: return {'engine':'quafu','task_id':res.taskid,'status':res.task_status}
        for _ in range(120):
            res=t.retrieve(res.taskid)
            if res.task_status not in ('In Queue','Running'): break
            time.sleep(5)
        return {'engine':'quafu','counts':dict(res.counts),'task_id':res.taskid,'status':res.task_status}
    if engine=='qr':
        from QuantumRingsLib import QuantumRegister, ClassicalRegister, QuantumCircuit, QuantumRingsProvider, job_monitor
        prov=QuantumRingsProvider(token=creds['QR_KEY_64'], name=creds['QR_USER'])
        be=prov.get_backend(backend or 'scarlet_quantum_rings')
        q=QuantumRegister(nq); c=ClassicalRegister(nq); qc=QuantumCircuit(q,c)
        for op in ops:
            if op[0]=='h': qc.h(op[1])
            elif op[0]=='cnot': qc.cx(op[1],op[2])
            elif op[0]=='ry': qc.ry(op[2],op[1])
            elif op[0]=='rz': qc.rz(op[2],op[1])
            elif op[0]=='x': qc.x(op[1])
        qc.measure_all()
        job=be.run(qc,shots=shots)
        if not wait: return {'engine':'qr','job_id':job.job_id(),'status':'submitted'}
        job_monitor(job)
        return {'engine':'qr','counts':job.result().get_counts()}
    raise ValueError(engine)
def chsh(engine, shots=1024, creds=None, backend=None):
    st=chsh_settings(); Es={}
    for k,(ta,tb) in st.items():
        r=run(_chsh_circuit(ta,tb),2,engine,shots,creds,backend)
        co=r['counts']
        tot=sum(co.values())
        E=((co.get('00',0)+co.get('11',0))-(co.get('01',0)+co.get('10',0)))/tot
        Es[k]=E
    S=Es['a_b']+Es['a_b2']+Es['a2_b']-Es['a2_b2']
    return {'engine':engine,'S':S,'E':Es,'violation':S>2}
def bell(engine,shots=1024,creds=None,backend=None): return run(BELL,2,engine,shots,creds,backend)
def ghz3(engine,shots=1024,creds=None,backend=None): return run(GHZ3,3,engine,shots,creds,backend)
CONCURRENCY_POLICY={'qr':'concurrent-primary(4/4 实证全成)','quafu':'sequential-or-async-poll(同账户并发降级空counts)','numpy':'local-free'}
