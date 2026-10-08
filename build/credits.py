import os, json, glob, re, time, urllib.request, urllib.parse, html
UA={'User-Agent':f"IndicLetters/0.1 ({os.environ['WIKIMEDIA_CONTACT']}) phonetics study, low volume"}
fs=sorted({c['word']['file'] for p in glob.glob('proto/lang/*.json') for c in json.load(open(p))['cells'].values() if c.get('word',{}).get('file')})
out={}
for i in range(0,len(fs),50):
  q=urllib.parse.urlencode({'action':'query','format':'json','prop':'imageinfo','iiprop':'extmetadata|url','iiextmetadatafilter':'Artist|LicenseShortName|LicenseUrl','titles':'|'.join('File:'+f for f in fs[i:i+50])})
  d=json.load(urllib.request.urlopen(urllib.request.Request('https://commons.wikimedia.org/w/api.php?'+q,headers=UA),timeout=60))
  norm={n['to']:n['from'] for n in d['query'].get('normalized',[])}
  for p in d['query']['pages'].values():
    t=norm.get(p['title'],p['title'])[5:]
    ii=(p.get('imageinfo') or [{}])[0]; m=ii.get('extmetadata',{})
    artist=re.sub('<[^>]+>','',html.unescape(m.get('Artist',{}).get('value',''))).strip()
    out[t]=dict(artist=artist or 'unknown',license=m.get('LicenseShortName',{}).get('value','?'),licenseUrl=m.get('LicenseUrl',{}).get('value',''),page=ii.get('descriptionurl',''))
  time.sleep(2)
json.dump(out,open('proto/credits.json','w'),ensure_ascii=False,indent=0)
import collections
print(len(out),'files'); print(collections.Counter(x['license'] for x in out.values()))
print(collections.Counter(x['artist'] for x in out.values()).most_common(8))
print([k for k,x in out.items() if x['artist']=='unknown' or x['license']=='?'][:10])
