import json, re, sys, warnings; warnings.filterwarnings('ignore')
import epitran
sys.path.insert(0,'phoible')
D=json.load(open('proto/data.json')); BY={c['ipa']:c['id'] for c in D['cells']}; BY['r']='0x31'; BY['n']='0x29'
CODES={'hi':'hin-Deva','mr':'mar-Deva','bn':'ben-Beng','kn':'kan-Knda','ml':'mal-Mlym','or':'ori-Orya','pa':'pan-Guru','si':'sin-Sinh','ta':'tam-Taml','te':'tel-Telu'}
VIR={'Deva':'्','Beng':'্','Knda':'್','Mlym':'്','Orya':'୍','Guru':'੍','Sinh':'්','Taml':'்','Telu':'్'}
VOW=set('əɔʌaɐɨeiouɪʊɛæyʉɑ')
def norm(p):
  p=re.sub('[ːˑˈˌ\u0361]','',p); p=p.replace('tɕ','tʃ').replace('dʑ','dʒ').replace('ɸ','f'); p=p.replace('̤','ʱ').replace('ɡ','g').replace('ɦ','ʱ') if len(p)>1 else p.replace('ɡ','g')
  p=''.join(ch for ch in p if ch not in VOW)
  p=re.sub(r'([gɟɖdbʤ])ʰ',r'\1ʱ',p)
  m={'c':'tʃ','ɟ':'dʒ','cʰ':'tʃʰ','ɟʱ':'dʒʱ','t':'t̪','tʰ':'t̪ʰ','d':'d̪','dʱ':'d̪ʱ','n':'n̪','ɹ':'ɾ','v':'ʋ','w':'ʋ','ɕ':'ʃ','χ':'x','ʧ':'tʃ','ʧʰ':'tʃʰ','ʤ':'dʒ','ʤʱ':'dʒʱ','ʐ':'ɻ','ɦ':'h','r̩':'ɽ','ŋg':'ᵑɡ'}
  return m.get(p,p)
out={}
for x in D['voices']:
  v=x['id']
  if v not in CODES: continue
  e=epitran.Epitran(CODES[v]); vir=VIR[x['script']]; res={}
  for k,c in x['cells'].items():
    if c.get('word'): continue
    ch=c.get('via') or c['ch']
    raw=e.transliterate(ch+vir); n=norm(raw)
    if not n: raw=e.transliterate(ch); n=norm(raw)
    res[k]=dict(ch=ch,raw=raw,cell=BY.get(n,'?'+n))
  out[v]=res
json.dump(out,open('epitran_cells.json','w'),ensure_ascii=False,indent=0)
# words for hidden sounds
for v,w in [('ta','தங்கம்'),('ta','மகன்'),('ta','காது'),('ta','படம்'),('ta','அம்பு'),('mr','चमचा'),('mr','जग'),('bn','ফল'),('ml','മഴ')]:
  print(v,w,epitran.Epitran(CODES[v]).transliterate(w), '| red:' , epitran.Epitran('tam-Taml-red').transliterate(w) if v=='ta' else '')
