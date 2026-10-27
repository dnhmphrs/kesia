import os, sys, re
S = sys.argv[1]
base = open('/home/user/kesia/clean5/10/index.html', encoding='utf-8').read()

IMG = {
 'networked-worlds-1': (990, 1400, 453, 'yellow cover with a curved grid: Networked Worlds, WeTransfer'),
 'networked-worlds-2': (1000, 1400, 457, 'a collage of many small images on black'),
 'networked-worlds-3': (1005, 1400, 460, '&quot;worlding resources&quot;: a timeline of books and texts on black'),
 'protein-1': (1080, 1080, 640, 'pink report cover: dirty word [report #4] community'),
 'protein-2': (1080, 1080, 640, 'overlapping page spreads from the report'),
 'protein-3': (1080, 1080, 640, 'a grid of the report&#x27;s pages in pink, black and white'),
 'protein-4': (1050, 1400, 480, 'the printed report on a wooden floor'),
 'morning-3': (1400, 1400, 640, '3d render of three pink piglet-like creatures curled inside a cracked black egg'),
 'morning-1': (1080, 1080, 640, 'MØRNING newsletter graphic: &quot;#020 uh oh, meet Ø&quot;, a red burn after reading sticker over screenshots of video calls'),
 'morning-2': (1120, 1400, 512, '3d render of a dark glossy egg with orange marbling'),
}
P = [
 dict(id='networked-worlds', n='01', url='https://co-matter.com/project/networked-worlds', name='networked worlds', after=' with co—matter',
      pics=['networked-worlds-1', 'networked-worlds-2', 'networked-worlds-3'],
      text='duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. excepteur sint occaecat cupidatat non proident.'),
 dict(id='protein', n='02', url='https://www.protein.xyz/dirty-words-4-community/', name='protein dirty words #4: community report', after='',
      pics=['protein-1', 'protein-2', 'protein-3', 'protein-4'],
      text='sed ut perspiciatis unde omnis iste natus error sit voluptatem accusantium doloremque laudantium, totam rem aperiam, eaque ipsa quae ab illo.'),
 dict(id='morning', n='03', url='https://www.instagram.com/p/CwOEAMetgc1/?img_index=1', name='MØRNING Ø', after='',
      pics=['morning-3', 'morning-1', 'morning-2'], text=None),
]
def ratio(name): w, h = IMG[name][:2]; return w / h
def img(name, sizes, style=''):
    w, h, sw, alt = IMG[name]
    return (f'<img src="../img/l/{name}.jpg" srcset="../img/s/{name}.jpg {sw}w, ../img/l/{name}.jpg {w}w" sizes="{sizes}" '
            f'width="{w}" height="{h}" alt="{alt}" style="--r: {w/h:.6f};{style}">')
def phone_widths(names):
    out = []
    for i in range(0, len(names), 2):
        pair = names[i:i+2]
        if len(pair) == 2:
            ra, rb = ratio(pair[0]), ratio(pair[1])
            out += [f'calc((100% - 1px) * {ra/(ra+rb):.4f})', f'calc((100% - 1px) * {rb/(ra+rb):.4f})']
        else:
            out.append('100%')
    return out

CSS = r"""
/* the project sheets: without js they open in place of the strip by #target (one at a time) */
.p { display: none; }
.p:target { display: block; }
.p:target ~ .page .strip { display: none; }
.sheet > header { border-bottom: 1px solid var(--line); }
.sheet > header .x { color: var(--grey); text-decoration: none; }
.sheet > header .x:hover { color: var(--ink); }
.pics { display: flex; gap: 1px; justify-content: flex-start; }
.pics img { display: block; width: auto; height: min(78vh, calc((100vw - 3px) / var(--sum))); }
html.js .pics img { height: calc((var(--ww, 100vw) - 5px) / var(--sum)); }
.row { display: grid; grid-template-columns: minmax(0, 1fr); row-gap: 4px; padding: 8px 0 14px; border-bottom: 1px solid var(--line); }
.row p { padding: 0 var(--pad); }
.row .side { display: flex; gap: 2ch; align-items: flex-start; }
.row .lorem { flex: 1 1 0; min-width: 0; max-width: 60em; }
.row .n { margin-right: 1ch; }
.strip > figure > a { display: block; }
@media (max-width: 699px) {
  .pics { flex-wrap: wrap; }
  .pics img { flex: none; width: var(--pw); height: auto; }
}
@media (min-width: 700px) {
  .row { grid-template-columns: minmax(0, 0.707143fr) minmax(0, 2fr); column-gap: 1px; padding-bottom: 12px; }
}

/* the trail: each step of the move is a stamped window that stays; the last one is the live sheet */
html.js .p, html.js .p:target { display: block; position: fixed; left: var(--wx, 0); top: var(--wy, 0); width: var(--ww, 100vw); height: var(--wh, 100vh); opacity: 0; visibility: hidden; pointer-events: none; z-index: 3; background: #fff; border: 1px solid var(--line); box-sizing: border-box; }
html.js .p:target ~ .page .strip { display: flex; }
html.js .p.live { opacity: 1; visibility: visible; pointer-events: auto; overflow: auto; }
html.js .p .sheet > header { position: sticky; top: 0; background: #fff; z-index: 1; }
html.js.away body { overflow: hidden; }
html.js.away .page { pointer-events: none; }
.veil { position: fixed; inset: 0; background: #fff; opacity: 0; pointer-events: none; z-index: 1; transition: opacity .25s; }
html.js.away .veil, html.js.moving .veil { opacity: .55; pointer-events: auto; }
.trail { position: fixed; inset: 0; pointer-events: none; z-index: 2; overflow: hidden; }
.stamp { position: absolute; left: 0; top: 0; background: #fff; border: 1px solid var(--line); box-sizing: border-box; overflow: hidden; pointer-events: auto; cursor: pointer; }
.stamp .bar { display: flex; justify-content: space-between; align-items: center; height: 40px; padding: 0 var(--pad); border-bottom: 1px solid var(--line); color: var(--grey); white-space: nowrap; overflow: hidden; }
.stamp .bar b { font-weight: normal; color: var(--ink); }
.stamp .ghost { position: absolute; left: 0; top: 40px; width: var(--gw); transform-origin: 0 0; transform: scale(var(--gs)); opacity: .45; pointer-events: none; }
.stamp .ghost img { filter: saturate(0); }
.stamp .ghost .sheet > header { display: none; }
/* the live sheet sits exactly on the last stamp: same window chrome */
html.js .p.live .sheet { background: #fff; }
"""

JS = r"""
(function () {
  'use strict';
  var P = __P__, html = document.documentElement, reduce = matchMedia('(prefers-reduced-motion: reduce)').matches;
  if (/\bnojs\b/.test(location.search)) return;
  html.classList.add('js');
  var veil = document.createElement('div'); veil.className = 'veil'; document.body.appendChild(veil);
  var trail = document.createElement('div'); trail.className = 'trail'; document.body.appendChild(trail);
  // the trail is a signature: from a small window at the top-left, N steps down and right, each a step larger,
  // to the window the project lives in. the earlier windows' title bars and left edges stay in view as a staircase.
  function geo() { var W = innerWidth; return W < 700 ? { n: 5, dx: 6, dy: 30, s0: 0.6, m: 0 } : { n: 7, dx: 34, dy: 26, s0: 0.5, m: 16 }; }
  var G = geo(), STEPS = reduce ? 1 : G.n, STEP_MS = reduce ? 0 : 90, cur = 'home', moving = false, stamps = [];
  function finalBox() { var W = innerWidth, H = innerHeight, g = geo(), x = 16 + g.n * g.dx, y = 16 + g.n * g.dy; return { x: x, y: y, w: W - x - g.m, h: H - y - g.m }; }
  function sheetOf(id) { return document.getElementById(id); }
  function leadOf(id) { return document.querySelector('.strip a[href="#' + id + '"] img'); }
  // the single vector: from the clicked picture's box to the full screen, in N equal steps
  function path(id) {
    var f = finalBox(), g = geo(), out = [], i, n = reduce ? 1 : g.n;
    for (i = 1; i <= n; i++) { var t = i / n; out.push({ s: g.s0 + (1 - g.s0) * t, x: 16 + g.dx * i, y: 16 + g.dy * i }); }
    if (reduce) out[0] = { s: 1, x: f.x, y: f.y };
    return out;
  }
  function placeLive(id) { var f = finalBox(), el = sheetOf(id); el.style.setProperty('--wx', f.x + 'px'); el.style.setProperty('--wy', f.y + 'px'); el.style.setProperty('--ww', f.w + 'px'); el.style.setProperty('--wh', f.h + 'px'); }
  function stamp(id, k, pt) {
    var el = document.createElement('div'), f = finalBox(); el.className = 'stamp';
    el.style.left = pt.x + 'px'; el.style.top = pt.y + 'px'; el.style.width = Math.round(f.w * pt.s) + 'px'; el.style.height = Math.round(f.h * pt.s) + 'px';
    el.style.setProperty('--gw', f.w + 'px'); el.style.setProperty('--gs', pt.s); el.style.zIndex = k;
    var bar = document.createElement('div'); bar.className = 'bar';
    bar.innerHTML = '<span><b>kes inkersole</b> · ' + P.filter(function (p) { return p.id === id; })[0].n + '</span><span>×</span>';
    var ghost = document.createElement('div'); ghost.className = 'ghost';
    ghost.appendChild(sheetOf(id).querySelector('.sheet').cloneNode(true));
    el.appendChild(bar); el.appendChild(ghost);
    el.addEventListener('click', function (e) { e.preventDefault(); if (!moving) goHome(); });
    trail.appendChild(el); return el;
  }
  function clearTrail() { trail.innerHTML = ''; stamps = []; }
  function open(id, instant) {
    if (moving || cur === id) return; moving = true; html.classList.add('moving');
    clearTrail(); var pts = path(id), k = 0;
    sheetOf(id).scrollTop = 0;
    function next() {
      if (k < pts.length) { stamps.push(stamp(id, k, pts[k])); k++; if (instant) next(); else setTimeout(next, STEP_MS); return; }
      cur = id; moving = false; html.classList.remove('moving'); html.classList.add('away');
      placeLive(id); P.forEach(function (p) { sheetOf(p.id).classList.toggle('live', p.id === id); });
    }
    next();
  }
  function goHome(instant) {
    if (moving || cur === 'home') return; moving = true; html.classList.add('moving');
    var id = cur; sheetOf(id).classList.remove('live'); html.classList.remove('away');
    function back() {
      if (stamps.length) { var s = stamps.pop(); s.remove(); if (instant) back(); else setTimeout(back, STEP_MS * 0.7); return; }
      cur = 'home'; moving = false; html.classList.remove('moving');
    }
    back();
  }
  function push(url) { try { history.pushState(null, '', url); } catch (e) {} }
  document.addEventListener('click', function (e) {
    if (e.target === veil) { e.preventDefault(); if (!moving) { push(location.pathname + location.search); goHome(); } return; }
    var a = e.target.closest && e.target.closest('a[href^="#"]'); if (!a) return;
    var id = a.getAttribute('href').slice(1); if (id && !sheetOf(id)) return;
    e.preventDefault(); if (moving) return;
    if (id) { push('#' + id); open(id); } else { push(location.pathname + location.search); goHome(); }
  });
  addEventListener('popstate', function () { var id = location.hash.slice(1); if (sheetOf(id)) { if (cur !== 'home') goHome(true); open(id); } else goHome(); });
  var id0 = location.hash.slice(1); if (sheetOf(id0)) open(id0, true);
  var rt; addEventListener('resize', function () { clearTimeout(rt); rt = setTimeout(function () { if (cur === 'home' || moving) return; var id = cur; clearTrail(); var pts = path(id); pts.forEach(function (pt, k) { stamps.push(stamp(id, k, pt)); }); placeLive(id); }, 150); });
  window.__kt = { state: function () { return { cur: cur, moving: moving, stamps: stamps.length }; }, open: open, home: goHome };
})();
"""

def captxt(p):
    return f'<span class="n">{p["n"]}</span><span class="k">for funds ·</span> <a href="{p["url"]}">{p["name"]}</a>{p["after"]}'

sections = ''
for p in P:
    sm = sum(ratio(n) for n in p['pics'])
    pws = phone_widths(p['pics'])
    pics = ''.join(img(n, f'(min-width: 700px) {100 * ratio(n) / sm:.0f}vw, 50vw', f' --pw: {pw};') for n, pw in zip(p['pics'], pws))
    lorem = f'<p class="lorem">{p["text"]}</p>' if p['text'] else '<p class="lorem"></p>'
    sections += (f'  <section class="p" id="{p["id"]}" style="--sum: {sm:.4f}">\n  <div class="sheet">\n'
                 f'    <header><h1><a href="#">kes inkersole</a> <span class="k">· {p["n"]}</span></h1><p><a class="x" href="#" aria-label="close">×</a></p></header>\n'
                 f'    <div class="pics">{pics}</div>\n'
                 f'    <div class="row"><p>{captxt(p)}</p><div class="side">{lorem}<a class="x" href="#" aria-label="close">×</a></div></div>\n'
                 f'  </div>\n  </section>\n')

sizes_home = {'networked-worlds-1': '(min-width: 700px) 27vw, 100vw', 'protein-1': '(min-width: 700px) 37vw, 100vw', 'morning-3': '(min-width: 700px) 37vw, 100vw'}
strip = '  <div class="strip">\n' + ''.join(
    f'    <figure>\n      <a href="#{p["id"]}">{img(p["pics"][0], sizes_home[p["pics"][0]])}</a>\n'
    f'      <figcaption><span class="n">{p["n"]}</span><span class="k">for funds ·</span> <a href="#{p["id"]}">{p["name"]}</a>{p["after"]}</figcaption>\n    </figure>\n'
    for p in P) + '  </div>'

h = base
m = re.search(r'  <div class="strip">\n.*?  </div>\n\n  <div class="grid">', h, re.S); assert m
h = h[:m.start()] + strip + '\n\n  <div class="grid">' + h[m.end():]
m2 = re.search(r'    <section class="c">\n      <h2 class="k">for funds</h2>.*?    </section>\n', h, re.S); assert m2
cell = ('    <section class="c">\n      <h2 class="k">for funds</h2>\n' +
        ''.join(f'      <h3><a href="{p["url"]}">{p["name"]}</a>{p["after"]}</h3>\n' for p in P) + '    </section>\n')
h = h[:m2.start()] + cell + h[m2.end():]
h = h.replace('.c h3 + p { margin-top: .2em; }', '.c h3 + p { margin-top: .2em; }\n.c h3 + h3 { margin-top: .3em; }', 1)
# the sheets come first in the body so :target can hide the strip; the whole home page is one wrapper
h = h.replace('<body>\n\n<header>', '<body>\n' + sections + '<div class="page">\n<header>', 1)
h = h.replace('</main>\n\n</body>', '</main>\n</div>\n<script>' + JS.replace('__P__', str([{'id': p['id'], 'n': p['n']} for p in P]).replace("'", '"')) + '</script>\n</body>', 1)
# the sheet header line sits in the same grid as the page header
h = h.replace('header { display: grid; grid-template-columns: minmax(0, 1fr); padding: 12px 0 11px; }',
              'header { display: grid; grid-template-columns: minmax(0, 1fr); padding: 12px 0 11px; }\n.sheet > header p { text-align: right; }', 1)
h = h.replace('</style>\n</head>', '</style>\n<style>' + CSS + '</style>\n</head>', 1)
os.makedirs(f'{S}/trail/out/01', exist_ok=True)
open(f'{S}/trail/out/01/index.html', 'w', encoding='utf-8').write(h)
print('written', len(h))
