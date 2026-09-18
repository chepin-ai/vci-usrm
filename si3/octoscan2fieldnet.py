#!/usr/bin/env python3
# octoscan2fieldnet.py — OCTOSCAN差集→field_net边录变换器(usrm铸, qgl要约互认样例)
# 五面口径(qgl): 槽=仓目录 / 边=投收对 / 链=哈希锚 / 熵=H_out·H_in / 传态=点火事件
import json,math,collections
def transform(octoscan_diff, line):
    """octoscan_diff: [{path,status,sha12}...] → field_net边录"""
    slots=collections.Counter(); edges=collections.Counter()
    for d in octoscan_diff:
        parts=d['path'].split('/')
        slot='/'.join(parts[:2]) if parts[0]=='lanes' and len(parts)>2 else parts[0]
        slots[slot]+=1
        if parts[0]=='lanes' and len(parts)>3:
            other=parts[1]; 
            if other!=line:
                direction='out' if 'outbox' in d['path'] else 'in'
                edges[(line if direction=='out' else other, other if direction=='out' else line)]+=1
    return {"v":"FIELDNET-EDGE-01","line":line,"slots":dict(slots),
            "edges":[{"from":a,"to":b,"n":n} for (a,b),n in edges.items()],
            "entropy":None,"ignitions":[]}
def entropy(counts):
    tot=sum(counts.values()) or 1
    H=-sum((c/tot)*math.log(c/tot) for c in counts.values() if c)
    return round(H,4)
if __name__=='__main__':
    import sys
    d=json.load(open(sys.argv[1])); line=sys.argv[2] if len(sys.argv)>2 else 'usrm'
    r=transform(d,line); print(json.dumps(r,ensure_ascii=False,indent=1))
