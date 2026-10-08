# Copy the built data into the site folder, attach recording credits, and write index.html and credits.html.
# Usage (from the work folder): python export.py <site-folder>
import json, glob, os, re, html, sys
SITE=sys.argv[1]
cr=json.load(open('proto/credits.json'))
def clean(a):
  m=re.match(r'Speaker:\s*(.+?)\s*\nRecorder:\s*(.+)',a)
  if m: return m.group(1) if m.group(1)==m.group(2).strip() else f'{m.group(1)} (speaker), {m.group(2).strip()} (recorder)'
  return ' '.join(a.split())
core=json.loads(open('proto/core.js').read()[len('window.CORE='):].rstrip(';\n'))
names={v['id']:v['name'] for v in core['voices']}
rows=[]
os.makedirs(f'{SITE}/lang',exist_ok=True)
for p in sorted(glob.glob('proto/lang/*.json')):
  d=json.load(open(p))
  for c in d['cells'].values():
    w=c.get('word')
    if w and w.get('file'):
      x=cr[w['file']]; w['credit']=dict(artist=clean(x['artist']),license=x['license'],page=x['page'])
      rows.append((names[d['id']],w['w'],w['credit']))
  json.dump(d,open(f"{SITE}/lang/{os.path.basename(p)}",'w'),ensure_ascii=False)
open(f'{SITE}/core.js','w').write(open('proto/core.js').read())
body=open('proto/varna.html').read().replace('<title>Varna Table</title>','').replace('<h1>Varna Table</h1>','<h1>Indic Letters</h1>')
body=body.replace('words marked ● are real speakers from Wikimedia Commons and Lingua Libre, CC BY-SA.</p>','words marked ● are real speakers from Wikimedia Commons and Lingua Libre. <a href="credits.html">Credits and licenses</a> · <a href="https://github.com/micahchoo/indic-letters">Source</a></p>')
head=open(os.path.join(os.path.dirname(__file__),'head.html')).read()
open(f'{SITE}/index.html','w').write(head+body+'\n</html>\n')
rows.sort(key=lambda r:(r[0],r[1]))
tr=''.join(f'<tr><td>{html.escape(l)}</td><td>{html.escape(w)}</td><td>{html.escape(c["artist"])}</td><td><a href="{html.escape(c["page"])}">{html.escape(c["license"])}</a></td></tr>' for l,w,c in rows)
tpl=open(os.path.join(os.path.dirname(__file__),'credits.tpl.html')).read()
open(f'{SITE}/credits.html','w').write(tpl.replace('{{N}}',str(len(rows))).replace('{{ROWS}}',tr))
print(len(rows),'credited rows')
