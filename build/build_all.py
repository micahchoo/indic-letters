# PROTOTYPE: all-language data. PHOIBLE decides state, espeak/Epitran vote marks audio, Wiktionary gives words + human audio.
import urllib.parse, json, re, subprocess, base64, os, tempfile, urllib.request, warnings, collections; warnings.filterwarnings('ignore')
import panphon, panphon.distance
ft=panphon.FeatureTable(); dist=panphon.distance.Distance()
D=json.load(open('proto/data.json')); AU=json.loads(open('proto/data.js').read().split('window.AUDIO=')[1].rstrip(';\n'))
CELLS={c['id']:c for c in D['cells']}
P=json.load(open('phoible/phoible_cells.json')); E=json.load(open('epitran_cells.json'))
V={v['id']:v for v in D['voices']}
KAI={v:f'kaikki/{n}.jsonl' for v,n in [('hi','Hindi'),('mr','Marathi'),('ne','Nepali'),('kok','Konkani'),('gu','Gujarati'),('pa','Punjabi'),('bn','Bengali'),('as','Assamese'),('or','Odia'),('te','Telugu'),('kn','Kannada'),('ml','Malayalam'),('ta','Tamil'),('si','Sinhalese')]}
SEG={'ts':'ts','dz':'dz','tʃ':'0x1a','tɕ':'0x1a','c':'0x1a','tʃʰ':'0x1b','dʒ':'0x1c','dʑ':'0x1c','ɟ':'0x1c','dʒʱ':'0x1d',
 'k':'0x15','kʰ':'0x16','ɡ':'0x17','g':'0x17','ɡʱ':'0x18','ŋ':'0x19','ɲ':'0x1e','ʈ':'0x1f','ʈʰ':'0x20','ɖ':'0x21','ɖʱ':'0x22','ɳ':'0x23',
 't̪':'0x24','t̪ʰ':'0x25','d̪':'0x26','d̪ʱ':'0x27','n̪':'0x28','n':'0x29','p':'0x2a','pʰ':'0x2b','b':'0x2c','bʱ':'0x2d','m':'0x2e',
 'j':'0x2f','ɾ':'0x30','r':'0x31','l':'0x32','ɭ':'0x33','ɻ':'0x34','ʋ':'0x35','v':'0x35','w':'0x35','ʃ':'0x36','ɕ':'0x36','ʂ':'0x37','s':'0x38','h':'0x39','ɦ':'0x39',
 'x':'n16','ɣ':'n17','z':'n1C','f':'n2B','ɽ':'n21'}
def segs(ipa):
  ipa=ipa.strip('/[]').split(',')[0]
  ipa=re.sub('[ˈˌ.‿()]','',ipa).replace('ː','').replace('ʱ','ʰ')  # PanPhon drops ʱ; ʰ survives and maps back below
  ipa=re.sub('(?<!͡)(t)(?=[ʃɕs])|(?<!͡)(d)(?=[ʒʑz])',lambda m:(m.group(1) or m.group(2))+'͡',ipa)
  out=[]
  for s in ft.ipa_segs(ipa):
    s=s.replace('͡',''); out.append(SEG.get(s) or SEG.get(s.replace('ʰ','ʱ')))
  return [x for x in out if x]
SCRIPT_BASE={'hi':0x900,'mr':0x900,'ne':0x900,'kok':0x900,'gu':0xA80,'pa':0xA00,'bn':0x980,'as':0x980,'or':0xB00,'te':0xC00,'kn':0xC80,'ml':0xD00,'ta':0xB80,'si':0xD80}
ISO={'hi':['hin','urd'],'mr':['mar'],'ne':['nep','npi'],'kok':['kok','gom'],'gu':['guj'],'pa':['pan'],'bn':['ben'],'as':['asm'],'or':['ori','ory'],'te':['tel'],'kn':['kan'],'ml':['mal'],'ta':['tam'],'si':['sin']}
def audio_ok(v,url):
  f=urllib.parse.unquote(url.rsplit('/',1)[1])
  return f.lower().startswith(v+'-') or any(f'({i})' in f for i in ISO[v])
def words(v):
  lo=SCRIPT_BASE[v]
  for line in open(KAI[v]):
    d=json.loads(line); w=d['word']
    if not any(lo<=ord(ch)<lo+0x80 for ch in w): continue
    if ' ' in w or '-' in w or len(w)>7 or d.get('pos') in ('name','suffix','prefix','character','symbol','abbrev'): continue
    ipas=[x['ipa'] for x in d.get('sounds',[]) if 'ipa' in x]
    if not ipas: continue
    aud=next((x.get('mp3_url') for x in d.get('sounds',[]) if x.get('mp3_url') and audio_ok(v,x['mp3_url'])),None)
    gl=(d.get('senses') or [{}])[0].get('glosses',[''])[0][:40]
    sg=segs(ipas[0])
    if sg: yield w,ipas[0],aud,gl,set(sg),sg[0]
W={v:list(words(v)) for v in KAI}
print({v:len(x) for v,x in W.items()})
ok={v:{k for k,c in P[v]['ph'].items() if c*2>=P[v]['n']} for v in KAI}
SIPRE={'ng','nd.','nd','mb'}
AS_TO={'0x1a':'0x38','0x1b':'0x38','0x1c':'n1C','0x1d':'n1C','0x36':'n16','0x37':'n16'}  # Assamese: চ ছ → s, জ ঝ → z, শ ষ → x
def wcount(v,cell): return sum(1 for x in W.get(v,[]) if cell in x[4])
def fd(a,b): return dist.feature_edit_distance(CELLS[a]['ipa'].replace('g','ɡ'),CELLS[b]['ipa'].replace('g','ɡ'))
def nearest(cell,pool):
  main=[k for k in pool if CELLS[k]['block']=='main']
  if CELLS[cell]['block']=='main' and main:
    same=[k for k in main if CELLS[k]['col']==CELLS[cell]['col']]
    pool=same or main
  return min(pool, key=lambda k: fd(cell,k))
tmp=tempfile.mkdtemp(); AUD={}
import time, hashlib
def fetch(url,key):
  if key in AUD: return key
  orig=re.sub(r'/transcoded(/.+?)/[^/]+\.mp3$',r'\1',url)
  cache=os.path.join('kaikki/audio',hashlib.md5(orig.encode()).hexdigest())
  if not os.path.exists(cache+'.mp3') and os.environ.get('NOFETCH'): return None
  if not os.path.exists(cache+'.mp3'):
    for attempt in range(4):
      try:
        req=urllib.request.Request(orig,headers={'User-Agent':f"IndicLetters/0.1 ({os.environ['WIKIMEDIA_CONTACT']}) phonetics study, low volume"})
        open(cache+'.src','wb').write(urllib.request.urlopen(req,timeout=30).read()); time.sleep(2.5); break
      except Exception as e:
        print('retry',attempt,key,str(e)[:60]); time.sleep(30*(attempt+1))
    else: return None
    subprocess.run(['ffmpeg','-loglevel','error','-y','-i',cache+'.src','-ac','1','-ar','22050','-b:a','32k',cache+'.mp3'],check=True)
  AUD[key]=base64.b64encode(open(cache+'.mp3','rb').read()).decode(); return key
def espeak_word(v,w):
  key=f'{v}:{w}'
  if key in AU: AUD[key]=AU[key]; return key
  wv=os.path.join(tmp,'a.wav'); mp=os.path.join(tmp,'a.mp3')
  subprocess.run(['espeak-ng','-v',v,'-s','130','-w',wv,w],check=True); subprocess.run(['lame','--quiet','-m','m','-b','32','--resample','22.05',wv,mp],check=True)
  AUD[key]=base64.b64encode(open(mp,'rb').read()).decode(); return key
def pick(v,cell,letter=None):
  best=None
  for w,ipa,aud,gl,sg,first in W.get(v,[]):
    if cell not in sg: continue
    if letter and letter not in w: continue
    sc=(100 if aud else 0)-len(w)*3-(5 if first!=cell else 0)
    if not best or sc>best[0]: best=(sc,w,ipa,aud,gl)
  return best
out={}
for v in KAI:
  AUD={}
  n=P[v]['n']; cells={}
  for cid,c in CELLS.items():
    k=P[v]['ph'].get(cid,0); allo=cid in P[v]['al']; old=V[v]['cells'].get(cid)
    letter=old['ch'] if old and old['s'] in('own','like') else None
    if cid=='0x34' and v=='ml': letter='ഴ'
    if cid=='0x36' and v=='si': letter='ශ'
    frac=k/n
    hand=None
    if v=='ta' and cid=='0x31': k=max(k,2); frac=k/n; hand='PHOIBLE notation hides this sound'
    if v=='si' and cid in SIPRE and letter: k=n; frac=1; hand="PHOIBLE's Sinhala descriptions count this as two sounds; Sinhala writes it as one letter"
    epc=E.get(v,{}).get(cid,{}).get('cell'); esc=cid if old and old['s']=='own' else None
    thin= n<=2 and frac==0 and letter and esc==cid and epc==cid
    if thin: hand=f"PHOIBLE's {n} description{'s' if n>1 else ''} omit this sound, but espeak-ng and Epitran both read the letter this way"
    if frac>=.5: s='own' if letter else 'said'
    elif frac>0 or thin: s='some'
    elif allo and not letter and wcount(v,cid)>=3: s='said'
    elif letter: s='like'
    else: continue
    e=dict(s=s,k=k,n=n,ipa=c['ipa'])
    if letter: e['ch']=letter; e['a']=old['a'] if old and old.get('a') else espeak_word(v,letter+chr({'Deva':0x93E,'Beng':0x9BE,'Guru':0xA3E,'Gujr':0xABE,'Orya':0xB3E,'Taml':0xBBE,'Telu':0xC3E,'Knda':0xCBE,'Mlym':0xD3E,'Sinh':0xDCF}[V[v]['script']]))
    # where does a written-but-not-said letter land?
    if s=='like':
      cand=[old.get('to') if old and old['s']=='like' else None, E.get(v,{}).get(cid,{}).get('cell')]
      e['to']=(AS_TO.get(cid) if v=='as' else None) or next((x for x in cand if x in ok[v]),None) or nearest(cid,ok[v])
      if v=='as' and cid in AS_TO: hand='Assamese merged this sound; hand-set from PHOIBLE and Mahanta (2012)'
    # audio check: espeak's sound for this letter vs what the cell says
    if letter and old:
      es=cid if old['s']=='own' else old.get('to'); want=cid if s in('own','some') else e.get('to')
      ep=E.get(v,{}).get(cid,{}).get('cell')
      if es!=want and want: e['off']=f"espeak-ng plays this as {CELLS[es]['ipa'] if es in CELLS else '?'}"+(f"; Epitran agrees with the chart ({CELLS[want]['ipa']})" if ep==want and want in CELLS else '')
      if old.get('note'): e['off']=old['note']
    if v=='si' and cid=='0x36': e['off']='espeak-ng plays this as s'; hand='PHOIBLE lists ʃ for ශ; espeak-ng reads it as s'
    b=pick(v,cid,letter if s=='own' else None) or (pick(v,cid) if s!='like' else None)
    if s=='like' and letter: b=pick(v,e['to'],letter)
    if b:
      _,w,ipa,aud,gl=b
      key=fetch(aud,'h:'+w) if aud else None
      e['word']=dict(w=w,ipa=ipa,gl=gl,a=key or espeak_word(v,w),human=bool(key))
      if key: e['word']['file']=urllib.parse.unquote(re.sub(r'/transcoded(/.+?)/[^/]+\.mp3$',r'\1',aud).rsplit('/',1)[1])
    if 'a' in e and e['a'] in AU: AUD[e['a']]=AU[e['a']]
    ep=E.get(v,{}).get(cid,{})
    e['votes']=dict(espeak=(CELLS[old['to']]['ipa'] if old and old['s']=='like' and old.get('to') in CELLS else (c['ipa'] if old and old['s']=='own' else None)) if letter else None,
                    epitran=(CELLS[ep['cell']]['ipa'] if ep.get('cell') in CELLS else ep.get('raw')) if letter else None,
                    phoible=f'{k}/{n}', allo=allo)
    e['hand']=hand
    cells[cid]=e
  have={k for k,x in cells.items() if x['s'] in('own','said','some')}
  near={}
  for cid in CELLS:
    if cid in have: continue
    near[cid]=nearest(cid,have)
  out[v]=dict(near=near,id=v,name=V[v]['name'],script=V[v]['script'],cells=cells,src='phoible')
  json.dump(dict(out[v],audio=AUD),open(f'proto/lang/{v}.json','w'),ensure_ascii=False)
  print(v,collections.Counter(x['s'] for x in cells.values()), 'words',sum('word' in x for x in cells.values()),'human',sum(x.get('word',{}).get('human',False) for x in cells.values()),'off',sum('off' in x for x in cells.values()))
# Bishnupriya: no PHOIBLE, no Wiktionary -> espeak-only
AUD={}; cells={}
for cid,c in V['bpy']['cells'].items():
  e=dict(c); e['votes']=dict(espeak=CELLS[c['to']]['ipa'] if c['s']=='like' else c['ipa'],epitran=None,phoible='no data',allo=False)
  AUD[c['a']]=AU[c['a']]; cells[cid]=e
have={k for k,x in cells.items() if x['s'] in('own','said')}
near={cid:nearest(cid,have) for cid in CELLS if cid not in have}
out['bpy']=dict(near=near,id='bpy',name='Bishnupriya',script='Beng',cells=cells,src='espeak')
json.dump(dict(out['bpy'],audio=AUD),open('proto/lang/bpy.json','w'),ensure_ascii=False)
W8={'own':1,'said':1,'some':.5}
def wset(v): return {k:W8.get(x['s'],0) for k,x in out[v]['cells'].items() if W8.get(x['s'],0)}
def jd(a,b):
  # feature distance: how far each sound of a is from its nearest sound in b, averaged, both ways (PanPhon)
  A,B=wset(a),wset(b)
  f=lambda X,Y: sum(w*min(fd(x,y) for y in Y) for x,w in X.items())/sum(X.values())
  return round((f(A,B)+f(B,A))/2,3)
order=[v['id'] for v in D['voices']]
distm={a:{b:jd(a,b) for b in order} for a in order}
mx=max(x for r in distm.values() for x in r.values())
distm={a:{b:round(x/mx,3) for b,x in r.items()} for a,r in distm.items()}  # 1 = the most distant pair
core=dict(rows=D['rows'],cols=D['cols'],cells=D['cells'],voices=[dict(id=v,name=out[v]['name'],script=out[v]['script'],src=out[v]['src']) for v in order],dist=distm)
open('proto/core.js','w').write('window.CORE='+json.dumps(core,ensure_ascii=False)+';\n')
for a in ['ta','hi','bn','si']: print(a,'nearest:',sorted(distm[a],key=distm[a].get)[1:6])
