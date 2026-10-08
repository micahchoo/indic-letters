# PROTOTYPE data builder: espeak-ng -> data.js (cells, per-voice letters, states, mp3 audio)
import subprocess, json, re, base64, os, tempfile, unicodedata as u
B={'Deva':0x900,'Beng':0x980,'Guru':0xA00,'Gujr':0xA80,'Orya':0xB00,'Taml':0xB80,'Telu':0xC00,'Knda':0xC80,'Mlym':0xD00}
VOICES=[('hi','Hindi','Deva'),('mr','Marathi','Deva'),('ne','Nepali','Deva'),('kok','Konkani','Deva'),
 ('gu','Gujarati','Gujr'),('pa','Punjabi','Guru'),('bn','Bengali','Beng'),('as','Assamese','Beng'),('bpy','Bishnupriya','Beng'),
 ('or','Odia','Orya'),('te','Telugu','Telu'),('kn','Kannada','Knda'),('ml','Malayalam','Mlym'),('ta','Tamil','Taml'),('si','Sinhala','Sinh')]
# cell id -> (ipa, plain label, row, col, block)
ROWS=['throat','back','roof','curled','teeth','lips']
COLS=['plain','puff','buzz','buzz + puff','nose','roll','smooth','hiss']
C={}
def cell(i,ipa,row,col,label=None,block='main'): C[i]=dict(id=i,ipa=ipa,row=row,col=col,block=block,label=label)
main=[(0x15,'k','back',0),(0x16,'kʰ','back',1),(0x17,'g','back',2),(0x18,'gʱ','back',3),(0x19,'ŋ','back',4),
 (0x1A,'tʃ','roof',0),(0x1B,'tʃʰ','roof',1),(0x1C,'dʒ','roof',2),(0x1D,'dʒʱ','roof',3),(0x1E,'ɲ','roof',4),
 (0x1F,'ʈ','curled',0),(0x20,'ʈʰ','curled',1),(0x21,'ɖ','curled',2),(0x22,'ɖʱ','curled',3),(0x23,'ɳ','curled',4),
 (0x24,'t̪','teeth',0),(0x25,'t̪ʰ','teeth',1),(0x26,'d̪','teeth',2),(0x27,'d̪ʱ','teeth',3),(0x28,'n̪','teeth',4),
 (0x2A,'p','lips',0),(0x2B,'pʰ','lips',1),(0x2C,'b','lips',2),(0x2D,'bʱ','lips',3),(0x2E,'m','lips',4),
 (0x30,'ɾ','teeth',5),(0x2F,'j','roof',6),(0x33,'ɭ','curled',6),(0x32,'l','teeth',6),(0x35,'ʋ','lips',6),
 (0x39,'h','throat',7),(0x36,'ʃ','roof',7),(0x37,'ʂ','curled',7),(0x38,'s','teeth',7)]
for o,ipa,r,c in main: cell(hex(o),ipa,r,c)
EXTRA=[('n15','q','deep back, plain','loans'),('n16','x','back, rough hiss','loans'),('n17','ɣ','back, buzzing hiss','loans'),
 ('n1C','z','teeth, buzzing hiss','loans'),('n2B','f','lip on teeth, hiss','loans'),('n21','ɽ','curled, flap','loans'),('n22','ɽʱ','curled, flap + puff','loans'),
 ('0x34','ɻ','curled far back, smooth','dravidian'),('0x31','r','tongue-tip roll','dravidian'),('0x29','n','gum ridge, nose','dravidian'),
 ('ts','ts','teeth, stop + hiss','affricate'),('dz','dz','teeth, stop + buzzing hiss','affricate'),
 ('ng','ᵑɡ','nose then back stop','sinhala'),('nd.','ⁿɖ','nose then curled stop','sinhala'),('nd','ⁿd̪','nose then teeth stop','sinhala'),('mb','ᵐb','nose then lips stop','sinhala')]
for i,ipa,lab,blk in EXTRA: cell(i,ipa,None,None,lab,blk)
ALIAS={'c':'tʃ','ɟ':'dʒ','cʰ':'tʃʰ','ɟʱ':'dʒʱ','ɟʰ':'dʒʱ','t':'t̪','tʰ':'t̪ʰ','d':'d̪','dʱ':'d̪ʱ','n':'n̪','ɡ':'g','ɡʱ':'gʱ','ɹ':'ɾ','v':'ʋ','w':'ʋ','ɕ':'ʃ','χ':'x','r.':'ɽ','r̩':'ɽ','kh':'kʰ','gh':'gʱ','ch':'tʃʰ','jh':'dʒʱ','th':'t̪ʰ','dh':'d̪ʱ','ph':'pʰ','bh':'bʱ','ʈh':'ʈʰ','ɖh':'ɖʱ','ɟh':'dʒʱ','ŋɡ':'ᵑɡ','ɳɖ':'ⁿɖ','ŋg':'ᵑɡ','ç':'h','ʒ':'z','kʰː':'kʰ'}
BYIPA={c['ipa']:k for k,c in C.items()}
BYIPA['r']='0x31'; BYIPA['n']='0x29'
VOW=set('əɔʌaɐɨeiouɪʊɛæyʉɑ')
def norm(s):
  s=re.sub(r'\([a-z]+\)','',s); s=re.sub('[ˈˌː+0-9 ]','',s); s=s.replace('̩','')
  s=''.join(ch for ch in s if ch not in VOW)
  s=re.sub(r'([ɡgɟɖdb])ʰ',r'\1ʱ',s)
  if s in ('r.',): return 'ɽ'
  return ALIAS.get(s,s)
def espeak(v,t,ipa=True):
  return subprocess.run(['espeak-ng','-v',v,'-q','--ipa' if ipa else '-x',t],capture_output=True,text=True).stdout.strip()
def realize(v,ch,vir):
  for t in ([ch+vir,ch] ):
    n=norm(espeak(v,t))
    if v!='si' and n=='ᵑɡ': n='ŋ'
    if v=='ml' and n=='n̪' : pass
    if n in BYIPA or n=='r' or n=='n': return n,t
  return None,None
SIN={0x15:0xD9A,0x16:0xD9B,0x17:0xD9C,0x18:0xD9D,0x19:0xD9E,0x1A:0xDA0,0x1B:0xDA1,0x1C:0xDA2,0x1D:0xDA3,0x1E:0xDA4,0x1F:0xDA7,0x20:0xDA8,0x21:0xDA9,0x22:0xDAA,0x23:0xDAB,0x24:0xDAD,0x25:0xDAE,0x26:0xDAF,0x27:0xDB0,0x28:0xDB1,0x2A:0xDB4,0x2B:0xDB5,0x2C:0xDB6,0x2D:0xDB7,0x2E:0xDB8,0x2F:0xDBA,0x30:0xDBB,0x32:0xDBD,0x33:0xDC5,0x35:0xDC0,0x36:0xDC1,0x37:0xDC2,0x38:0xDC3,0x39:0xDC4,'n2B':0xDC6,'ng':0xD9F,'nd.':0xDAC,'nd':0xDB3,'mb':0xDB9}
NUK={'Deva','Beng','Guru','Gujr','Orya'}
SKIP_DEVA={'0x29','0x31','0x34'}
def letters_for(v,s):
  out={}
  if s=='Sinh':
    for k,cp in SIN.items(): out[hex(k) if isinstance(k,int) else k]=chr(cp)
    return out,'්','ා'
  b=B[s]
  for k in C:
    if k.startswith('0x'): ch=chr(b+int(k,16))
    elif re.fullmatch(r'n[0-9A-F]{2}',k) and s in NUK: ch=chr(b+int(k[1:],16))+chr(b+0x3C)
    else: continue
    if not u.name(ch[0],''): continue
    if s=='Deva' and k in SKIP_DEVA: continue
    out[k]=ch
  if v=='as': out['0x30']='ৰ'; out['0x35']='ৱ'
  if s=='Telu': out['ts']='ౘ'; out['dz']='ౙ'
  return out,chr(b+0x4D),chr(b+0x3E)
SAID={'ta':[('0x17','தங்கம்','thaṅgam, gold'),('0x26','காது','kādu, ear'),('0x21','படம்','paḍam, picture'),('0x2c','அம்பு','ambu, arrow'),('0x1c','பஞ்சு','pañju, cotton')],
      'mr':[('ts','चमचा','tsamtsā, spoon'),('dz','जग','dzag, world')]}
NOTE={('mr','ts'):'espeak-ng plays this as tʃ. It cannot make the Marathi ts.',('mr','dz'):'espeak-ng plays this as dʒ. It cannot make the Marathi dz.'}
audio={}; tmp=tempfile.mkdtemp()
def clip(v,text):
  key=f'{v}:{text}'
  if key in audio: return key
  w=os.path.join(tmp,'a.wav'); m=os.path.join(tmp,'a.mp3')
  subprocess.run(['espeak-ng','-v',v,'-s','130','-w',w,text],check=True)
  subprocess.run(['lame','--quiet','-m','m','-b','32','--resample','22.05',w,m],check=True)
  audio[key]=base64.b64encode(open(m,'rb').read()).decode(); return key
voices=[]
for v,name,s in VOICES:
  L,vir,aa=letters_for(v,s); st={}
  real={}
  for k,ch in L.items():
    n,t=realize(v,ch,vir)
    if n is None: continue
    tgt=BYIPA.get(n) if n not in('r','n') else BYIPA[n]
    real[k]=(ch,n,tgt)
  for k,(ch,n,tgt) in real.items():
    spoken=ch if norm(espeak(v,ch))==n else ch+aa
    a=clip(v,spoken)
    if tgt==k: st[k]=dict(s='own',ch=ch,ipa=n,a=a)
    else: st[k]=dict(s='like',ch=ch,ipa=n,to=tgt,a=a)
  for k,(ch,n,tgt) in real.items():
    if tgt!=k and tgt in C and (tgt not in st or st[tgt]['s']=='like'):
      st[tgt]=dict(s='said',ch=ch,ipa=n,a=st[k]['a'],via=ch)
  for k,word,gloss in SAID.get(v,[]):
    if k in st and st[k]['s']=='own': continue
    st[k]=dict(s='said',ch=word,ipa=C[k]['ipa'],a=clip(v,word),word=gloss,note=NOTE.get((v,k)))
  voices.append(dict(id=v,name=name,script=s,cells=st))
# hand fix: espeak-ng maps Malayalam ഴ to a flap; it is the same sound as Tamil ழ
for x in voices:
  if x['id']=='ml':
    c=x['cells']['0x34']; c.update(s='own',ipa='ɻ',note='espeak-ng plays this as a flap. The real sound is the same as Tamil ழ.'); c.pop('to',None)
    if x['cells'].get('n21',{}).get('via')=='ഴ': del x['cells']['n21']
# distance = 1 - Jaccard over sounds the language makes (own + said)
S={x['id']:{k for k,c in x['cells'].items() if c['s'] in('own','said')} for x in voices}
dist={a:{b:round(1-len(S[a]&S[b])/len(S[a]|S[b]),3) for b in S} for a in S}
json.dump(dict(rows=ROWS,cols=COLS,cells=list(C.values()),voices=voices,dist=dist),open('data.json','w'),ensure_ascii=False)
open('data.js','w').write('window.DATA='+json.dumps(dict(rows=ROWS,cols=COLS,cells=list(C.values()),voices=voices,dist=dist),ensure_ascii=False)+';\nwindow.AUDIO='+json.dumps(audio)+';\n')
print(len(audio),'clips', os.path.getsize('data.js')//1024,'KB')
for x in voices: print(x['id'], {s:sum(1 for c in x['cells'].values() if c['s']==s) for s in('own','like','said')})
for a in ['ta','hi','bn']: print(a,'nearest:',sorted(dist[a],key=dist[a].get)[:6])
