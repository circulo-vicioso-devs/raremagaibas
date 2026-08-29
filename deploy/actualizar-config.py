#!/usr/bin/env python3
"""Pasa las direcciones de las máquinas desplegadas a web/config.js."""
import json, glob, os, re
AQUI=os.path.dirname(os.path.abspath(__file__)); RAIZ=os.path.dirname(AQUI)
maq={}
for f in sorted(glob.glob(os.path.join(AQUI,'carta-*/cache.json'))):
    p=json.load(open(f))['program']
    if not p.get('candyMachine'): continue
    n=os.path.basename(os.path.dirname(f))
    serie=n.replace('carta-','').replace('-foil','')
    maq.setdefault(serie,{})['foil' if n.endswith('-foil') else 'gentle']=p['candyMachine']
col=next((json.load(open(f))['program']['collectionMint']
          for f in glob.glob(os.path.join(AQUI,'carta-*/cache.json'))
          if json.load(open(f))['program'].get('collectionMint')), "")
cfg=os.path.join(RAIZ,'web','config.js'); s=open(cfg).read()
bloque=json.dumps(maq, indent=4).replace('"gentle"','gentle').replace('"foil"','foil')
i=s.index('MAQUINAS: {'); j=i+len('MAQUINAS: '); n=0
for k in range(j, len(s)):
    if s[k]=='{': n+=1
    elif s[k]=='}':
        n-=1
        if n==0: break
s=s[:i]+'MAQUINAS: '+bloque+s[k+1:]
s=re.sub(r'COLECCION: "[^"]*"', f'COLECCION: "{col}"', s)
open(cfg,'w').write(s)
completas=sum(1 for v in maq.values() if len(v)==2)
print(f"  {len(maq)} cartas · {completas} con gentle y foil · colección {col[:12]}…")
