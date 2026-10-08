import csv, json, re, collections, sys
ISO={'hi':'hin','mr':'mar','ne':'npi','kok':'knn','gu':'guj','pa':'pan','bn':'ben','as':'asm','or':'ory','te':'tel','kn':'kan','ml':'mal','ta':'tam','si':'sin'}
D=json.load(open(sys.argv[1])); CELLS={c['id']:c for c in D['cells']}; BY={c['ipa']:c['id'] for c in D['cells']}
BY['r']='0x31'; BY['n']='0x29'
def norm(p,inv):
  p=p.split('|')[0]; p=re.sub('[ːˑ]','',p); p=p.replace('̻','̪').replace('̠','')
  breathy=('\u0324' in p) or ('ʱ' in p); p=p.replace('\u0324','')
  p=p.replace('ʱ','').replace('ɡ','g')
  if p.endswith('ʰ'): asp=True; p=p[:-1]
  else: asp=False
  m={'cç':'tʃ','c':'tʃ','tʃ':'tʃ','ɟʝ':'dʒ','ɟ':'dʒ','dʒ':'dʒ','t':'t̪','d':'d̪','d̻':'d̪','t̻':'t̪','ɦ':'h','χ':'x','ʁ':'ɣ','w':'ʋ','β̞':'ʋ','v':'ʋ','s̪':'s','z̪':'z','ʐ':'ɻ','l̠˞':'ɻ','ɽ̃':'ɽ','ç':'ʃ','l̪':'l','r̪':'r','ɕ':'ʃ'}
  p=m.get(p,p)
  if p=='n' and 'n̪' not in inv: p='n̪'
  if p=='r' and 'ɾ' not in inv: p='ɾ'
  if breathy or (asp and p in('g','dʒ','ɖ','d̪','b','ɽ','dz')): p+='ʱ'
  elif asp: p+='ʰ'
  if p in('tsʰ',):p='ts'
  if p in('dzʱ',):p='dz'
  return BY.get(p)
rows=list(csv.DictReader(open('phoible.csv',encoding='utf-8')))
out={}
for v,iso in ISO.items():
  invs=collections.defaultdict(list)
  for r in rows:
    if r['ISO6393']==iso and r['SegmentClass']=='consonant': invs[r['InventoryID']].append(r)
  n=len(invs); ph=collections.Counter(); al=collections.Counter()
  for iid,rs in invs.items():
    raw={x['Phoneme'] for x in rs}
    P={norm(x['Phoneme'],raw) for x in rs}-{None}
    A=set()
    for x in rs:
      if x['Allophones'] and x['Allophones']!='NA':
        for a in x['Allophones'].split(): A.add(norm(a,raw))
    A=A-{None}-P
    ph.update(P); al.update(A)
  out[v]=dict(n=n,ph=dict(ph),al=dict(al))
json.dump(out,open('phoible_cells.json','w'),ensure_ascii=False,indent=0)
# compare with espeak
print('lang  inv  espeak-has-PHOIBLE-majority-lacks | PHOIBLE-majority-has-espeak-lacks | allophone-only')
for x in D['voices']:
  v=x['id']
  if v not in out: continue
  o=out[v]; maj={k for k,c in o['ph'].items() if c*2>=o['n']}
  es={k for k,c in x['cells'].items() if c['s'] in('own','said')}
  ip=lambda S:' '.join(sorted(CELLS[k]['ipa'] for k in S))
  print(f"{v:4} {o['n']}   {ip(es-maj):28} | {ip(maj-es):22} | {ip(set(o['al'])-maj-es)}")
