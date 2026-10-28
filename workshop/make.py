import sys,os,re,json
S=sys.argv[1]
base=open(f'{S}/fresh/out/02/index.html',encoding='utf-8').read()
def css(h,c): return h.replace('</style>','/* variant */\n'+c+'\n</style>',1)
V={}
V['01']=('as is','the ten-project page as it stands: one row of squares, the index below.',base)

# 02 index first, strip after
h=base; a=h.index('<div class="thumbs">'); b=h.index('</div>',a)+6; strip=h[a:b]; h=h[:a]+h[b:]
k=h.index('<section class="row idx2 sec">'); h=h[:k]+strip+'\n'+h[k:]
V['02']=('index first','the project lines come first, the picture strip closes the list.',h)

# 03 strip with titles under each square
h=base
titles={m.group(1):m.group(2) for m in re.finditer(r'<section class="p" id="([a-z-]+)">\s*<div class="row idx"[^>]*><span class="n g">\d+</span><span class="t u">([^<]+)</span>',h)}
for id,t in titles.items():
    h=re.sub(r'(<button data-open="%s"[^>]*>.*?<span class="g">)(\d+)(</span>)'%re.escape(id), lambda m: m.group(1)+m.group(2)+'</span><span class="u tt">'+t+m.group(3).replace('</span>',''), h, count=1, flags=re.S)
h=css(h,'.thumbs span.tt { padding-top: 0; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }')
V['03']=('captioned strip','each square carries its number and title, so the strip reads on its own.',h)

# 04 hover link: hovering a line marks its square and vice versa
h=css(base,'.thumbs button { transition: opacity .15s; } .thumbs.hl button { opacity: .25; } .thumbs.hl button.on { opacity: 1; } .idx.on { background: #fafafa; }')
h=h.replace('  var h = location.hash','''  var th = document.querySelector('.thumbs');
  function hl(id) { th.classList.toggle('hl', !!id); document.querySelectorAll('[data-open]').forEach(function (b) { b.classList.toggle('on', b.dataset.open === id); }); document.querySelectorAll('.p').forEach(function (p) { p.querySelector('.idx').classList.toggle('on', p.id === id); }); }
  document.querySelectorAll('.idx').forEach(function (r) { r.addEventListener('mouseenter', function () { hl(r.parentNode.id); }); r.addEventListener('mouseleave', function () { hl(null); }); });
  document.querySelectorAll('[data-open]').forEach(function (b) { b.addEventListener('mouseenter', function () { hl(b.dataset.open); }); b.addEventListener('mouseleave', function () { hl(null); }); });
  var h = location.hash''',1)
V['04']=('linked hover','hover a line and its square stays lit while the rest of the strip dims, and the other way round.',h)

# 05 split: index left, squares in a grid right
h=base
h=h.replace('<div class="thumbs">','<div class="split"><div class="list">',1)
a=h.index('<div class="list">')+len('<div class="list">'); b=h.index('</div>',h.index('<div class="list">'))
thumbs=h[a:b]; h=h[:a]+h[b+6:]
k=h.index('<section class="row idx2 sec">'); h=h[:k]+'</div><div class="thumbs">'+thumbs+'</div></div>\n'+h[k:]
h=css(h,'@media (min-width: 700px) { .split { display: grid; grid-template-columns: 7fr 5fr; border-bottom: 1px solid var(--line); } .split .list { border-right: 1px solid var(--line); } .split .thumbs { grid-auto-flow: row; grid-template-columns: repeat(3, minmax(0, 1fr)); align-content: start; border-bottom: 0; } .split .p.open .body .pics img { height: min(40vh, calc((58vw - 3px) / var(--sum))); } }')
V['05']=('split','the index on the left, the squares as a grid on the right; a project opens inside the list.',h)

# 06 big strip: full-bleed horizontal scroll at strip height, natural proportions
h=css(base,'.thumbs { grid-auto-columns: auto; overflow-x: auto; scrollbar-width: thin; } .thumbs img { aspect-ratio: auto; height: 38vh; width: auto; } @media (max-width: 699px) { .thumbs { grid-auto-flow: column; grid-template-columns: none; } .thumbs img { height: 30vh; } }')
V['06']=('big strip','the squares become a tall full-bleed row at natural proportions that scrolls sideways.',h)

# 07 small strip: a thin contact strip of tiny squares
h=css(base,'.thumbs { grid-auto-columns: 72px; justify-content: start; background: #fff; gap: 1px; padding: 8px var(--pad); } .thumbs button { border: 1px solid var(--line); } .thumbs span { padding: 2px 4px; } @media (max-width: 699px) { .thumbs { grid-template-columns: repeat(5, minmax(0, 1fr)); } }')
V['07']=('contact strip','the squares shrink to a quiet row of icons above the index.',h)

# 08 open project shows in the strip slot: the strip is replaced by the open project's pictures
h=css(base,'body.has-open .thumbs button:not(.on) { opacity: .2; } .thumbs button.on { outline: 1px solid var(--ink); outline-offset: -1px; }')
h=h.replace("    var open = document.querySelector('.p.open');","    var open = document.querySelector('.p.open');\n    document.body.classList.toggle('has-open', !!open); document.querySelectorAll('[data-open]').forEach(function (b) { b.classList.toggle('on', !!open && b.dataset.open === open.id); });",1)
V['08']=('marked strip','when a project is open its square is outlined and the others dim, so the strip shows where you are.',h)

notes={}
for nn,(name,note,h) in V.items():
    os.makedirs(f'{S}/ws/out/{nn}',exist_ok=True); open(f'{S}/ws/out/{nn}/index.html','w',encoding='utf-8').write(h)
    notes[f'ws/{nn}']=f'{name} · {note}'
json.dump(notes,open(f'{S}/tools/notes-ws.json','w'),ensure_ascii=False,indent=0)
