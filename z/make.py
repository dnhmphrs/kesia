import os, sys, re, math
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
IDS = [p['id'] for p in P]
def ratio(name): w, h = IMG[name][:2]; return w / h
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
def img(name, sizes, cls='', style=''):
    w, h, sw, alt = IMG[name]
    c = f' class="{cls}"' if cls else ''
    return (f'<img{c} src="../img/l/{name}.jpg" srcset="../img/s/{name}.jpg {sw}w, ../img/l/{name}.jpg {w}w" sizes="{sizes}" '
            f'width="{w}" height="{h}" alt="{alt}" style="--r: {w/h:.6f};{style}">')
def captxt(p, link):
    t = f'<a href="{p["url"]}">{p["name"]}</a>' if link else p['name']
    return f'<span class="n">{p["n"]}</span><span class="k">for funds ·</span> {t}{p["after"]}'
def sel(tpl):
    """expand a selector template over the three projects: {id} is the project id"""
    return ', '.join(tpl.format(id=i) for i in IDS)

# shared: radio state (focusable but invisible, so arrow keys work), the three figures with go/back labels,
# and a text row under the strip for the open project
SHARED = """
.r { position: absolute; width: 1px; height: 1px; opacity: 0; pointer-events: none; }
.r:focus-visible + * { outline: 1px solid var(--ink); outline-offset: -2px; }
label { cursor: pointer; }
.pic { position: relative; }
.pic > label { display: block; }
.lead { display: block; width: 100%; height: auto; }
.pic > .back, figcaption > .back { display: none; }
.pic > .back { position: absolute; inset: 0; }
figcaption { padding: 8px var(--pad) 12px; display: flex; justify-content: space-between; gap: 2ch; }
figcaption > label { justify-content: space-between; gap: 2ch; flex: 1 1 auto; min-width: 0; }
figcaption > .go { display: flex; }
figcaption .go > span:first-child, figcaption .back > span:first-child { min-width: 0; }
figcaption .tog { color: var(--grey); flex: none; }
figcaption .n { margin-right: 1ch; }
""" + '\n'.join(f"""
#o-{i}:checked ~ .strip #f-{i} .back {{ display: block; }}
#o-{i}:checked ~ .strip #f-{i} figcaption > .back {{ display: flex; }}
#o-{i}:checked ~ .strip #f-{i} figcaption > .go {{ display: none; }}
#o-{i}:checked ~ .txt .t-{i} {{ display: grid; }}""" for i in IDS) + """
.txt > div { display: none; grid-template-columns: minmax(0, 1fr); row-gap: 4px; padding: 8px 0 14px; border-bottom: 1px solid var(--line); }
.txt p { padding: 0 var(--pad); max-width: 60em; }
.txt .side { display: flex; gap: 2ch; align-items: flex-start; }
.txt .lorem { flex: 1 1 0; min-width: 0; }
.txt .x { flex: none; margin-left: auto; color: var(--grey); padding: 0 2px; }
.txt .x:hover { color: var(--ink); }
.txt .k { color: var(--grey); }
@media (min-width: 700px) { .txt > div { grid-template-columns: minmax(0, 0.707143fr) minmax(0, 2fr); column-gap: 1px; padding-bottom: 12px; } }
"""

def radios():
    return ('  <input class="r" type="radio" name="open" id="o-none" checked>\n' +
            ''.join(f'  <input class="r" type="radio" name="open" id="o-{i}">\n' for i in IDS))

def figure(p, lead_sizes, extra=''):
    return (f'    <figure id="f-{p["id"]}">\n'
            f'      <div class="pic"><label class="go" for="o-{p["id"]}">{img(p["pics"][0], lead_sizes, "lead")}</label><label class="back" for="o-none" aria-label="close"></label></div>\n'
            f'{extra}'
            f'      <figcaption><label class="go" for="o-{p["id"]}"><span>{captxt(p, True)}</span><span class="tog" aria-hidden="true">+</span></label>'
            f'<label class="back" for="o-none"><span>{captxt(p, True)}</span><span class="tog" aria-hidden="true">&minus;</span></label></figcaption>\n'
            f'    </figure>\n')

def txtrow(p):
    if not p['text']: return ''
    return (f'    <div class="t-{p["id"]}"><p class="k">{p["n"]}</p>'
            f'<div class="side"><p class="lorem">{p["text"]}</p><label class="x" for="o-none" aria-label="close">×</label></div></div>\n')

def page(name, css, body):
    h = base
    m = re.search(r'  <div class="strip">\n.*?  </div>\n\n  <div class="grid">', h, re.S); assert m
    h = h[:m.start()] + radios() + body + '\n\n  <div class="grid">' + h[m.end():]
    m2 = re.search(r'    <section class="c">\n      <h2 class="k">for funds</h2>.*?    </section>\n', h, re.S); assert m2
    cell = ('    <section class="c">\n      <h2 class="k">for funds</h2>\n' +
            ''.join(f'      <h3><a href="{p["url"]}">{p["name"]}</a>{p["after"]}</h3>\n' for p in P) + '    </section>\n')
    h = h[:m2.start()] + cell + h[m2.end():]
    h = h.replace('.c h3 + p { margin-top: .2em; }', '.c h3 + p { margin-top: .2em; }\n.c h3 + h3 { margin-top: .3em; }', 1)
    # the base strip rules would fight ours
    h = h.replace('.strip { display: flex; flex-direction: column; gap: 1px; }\n', '', 1)
    h = h.replace('  .strip { flex-direction: row; }\n  .strip figure { flex: 1 1 0; }\n  .strip figure:first-child { flex-grow: var(--r1); }\n', '', 1)
    h = h.replace('.strip figure { min-width: 0; }\n.strip img { display: block; width: 100%; height: auto; }\n', '.strip figure { min-width: 0; }\n', 1)
    h = h.replace('figcaption { padding: 8px var(--pad) 14px; }\nfigcaption .n { margin-right: 1ch; }\n', '', 1)
    h = h.replace('  figcaption { padding-bottom: 12px; }\n', '', 1)
    h = h.replace('</style>\n</head>', '</style>\n<style>\n/* ' + name + ' */' + SHARED + css.rstrip() + '\n</style>\n</head>', 1)
    return h

# ====================== A: accordion ======================
# closed: the live strip (three columns whose widths follow the leads' proportions, so one shared height).
# open: the other two columns narrow to 72px spines showing a slice of their lead, the open column takes the rest
# and lays all its pictures in a row at one height; its caption and text in the row beneath. the spines still open.
SP = 72
cssA = """
.strip { display: grid; grid-template-columns: var(--c1) var(--c2) var(--c3); gap: 1px; --c1: 0.707143fr; --c2: 1fr; --c3: 1fr; transition: grid-template-columns .45s cubic-bezier(.4,0,.2,1); }
.strip figure { display: flex; flex-direction: column; min-width: 0; }
.pic { flex: 1 1 auto; min-height: 0; }
.row { display: none; gap: 1px; }
.row > label.back { display: block; flex: none; }
.row img { display: block; width: auto; flex: none; height: var(--h); }
@media (min-width: 700px) {
  .strip figcaption { white-space: nowrap; overflow: hidden; }
""" + '\n'.join(f"""  #o-{i}:checked ~ .strip {{ --c1: {'minmax(0, 1fr)' if i == IDS[0] else f'{SP}px'}; --c2: {'minmax(0, 1fr)' if i == IDS[1] else f'{SP}px'}; --c3: {'minmax(0, 1fr)' if i == IDS[2] else f'{SP}px'}; }}
  #o-{i}:checked ~ .strip #f-{i} .pic {{ display: none; }}
  #o-{i}:checked ~ .strip #f-{i} .row {{ display: flex; --h: min(calc((100vw - 2px) / 2.707143), calc((100vw - {2*SP + 2}px - {(len([p for p in P if p['id']==i][0]['pics'])-1)}px) / var(--sum))); }}
  #o-{i}:checked ~ .strip figure:not(#f-{i}) .pic {{ overflow: hidden; }}
  #o-{i}:checked ~ .strip figure:not(#f-{i}) .lead {{ height: 100%; object-fit: cover; object-position: left top; }}
  #o-{i}:checked ~ .strip figure:not(#f-{i}) figcaption .go > span {{ display: none; }}
  #o-{i}:checked ~ .strip figure:not(#f-{i}) figcaption .go::before {{ content: attr(data-n); color: var(--grey); }}""" for i in IDS) + """
  .strip figure:not(.open) .pic > label { height: 100%; }
  .pic > label, .pic .lead { height: 100%; }
}
@media (max-width: 699px) {
  /* phone: a vertical accordion; the open one shows its other pictures two across under its lead, then its text */
  .strip { display: block; }
  .strip figure + figure { border-top: 1px solid var(--line); }
  .row { flex-wrap: wrap; }
  .row img { height: auto; }
  .row .lead { display: none; }
  .row img { flex: none; width: var(--pw); }
  .row > label.back { display: none !important; }
""" + '\n'.join(f"  #o-{i}:checked ~ .strip #f-{i} .row {{ display: flex; }}" for i in IDS) + """
}
"""
def figA(p):
    sm = sum(ratio(n) for n in p['pics'])
    row = ('      <div class="row" style="--sum: ' + f'{sm:.4f}' + '"><label class="back" for="o-none">' + img(p['pics'][0], '(min-width: 700px) 40vw, 50vw', 'lead') + '</label>'
           + ''.join(img(n, '(min-width: 700px) 40vw, 50vw', '', f' --pw: {pw};') for n, pw in zip(p['pics'][1:], phone_widths(p['pics'][1:]))) + '</div>\n')
    f = figure(p, '(min-width: 700px) 37vw, 100vw', row)
    return f.replace('<label class="go" for="o-' + p['id'] + '"><span>', f'<label class="go" for="o-{p["id"]}" data-n="{p["n"]} +"><span>', 1)
bodyA = '  <div class="strip">\n' + ''.join(figA(p) for p in P) + '  </div>\n  <div class="txt">\n' + ''.join(txtrow(p) for p in P) + '  </div>'

# ====================== B: the stack ======================
# closed: the live strip. open: under the strip, a stage where the project's other pictures stand as plates in
# cabinet projection, each one stepping back and up from the one in front, hairline edges joining their corners;
# the stack rises from the open project's column (and mirrors for the right-hand column). text row beneath.
STEP_X, STEP_Y = 0.9, 0.18   # in plate heights: how far each plate steps right (times its ratio) and up
cssB = """
.strip { display: flex; flex-direction: column; gap: 1px; }
.stage { display: none; position: relative; height: calc(var(--h) * var(--sh)); overflow: hidden; border-top: 1px solid var(--line); }
.stage img { position: absolute; display: block; height: var(--h); width: auto; border: 1px solid var(--line); box-sizing: border-box; background: #fff; }
.edge { position: absolute; height: 1px; background: var(--line); transform-origin: 0 0; }
""" + '\n'.join(f"  #o-{i}:checked ~ .stage.s-{i} {{ display: block; }}" for i in IDS) + """
@media (min-width: 700px) {
  .strip { flex-direction: row; }
  .strip figure { flex: 1 1 0; }
  .strip figure:first-child { flex-grow: 0.707143; }
  .stage { --h: min(52vh, calc(var(--avail) / var(--sw))); }
}
@media (max-width: 699px) {
  /* phone: no stage; the other pictures two across under the strip */
  .stage { height: auto; display: none; flex-wrap: wrap; gap: 1px; }
""" + '\n'.join(f"  #o-{i}:checked ~ .stage.s-{i} {{ display: flex; }}" for i in IDS) + """
  .stage img { position: static; height: auto; border: 0; flex: none; width: var(--pw); }
  .stack { position: static !important; display: contents; }
  .edge { display: none; }
}
"""
def stageB(p, col):
    others = p['pics'][1:]
    n = len(others)
    # plate i: left (in h units) = sum of the previous plates' widths * STEP_X ; bottom = i * STEP_Y
    lefts, acc = [], 0.0
    for name in others:
        lefts.append(acc); acc += STEP_X * ratio(name)
    sw = lefts[-1] + ratio(others[-1])            # stack width in h units
    sh = 1 + STEP_Y * (n - 1)                     # stack height in h units
    mirror = col == 2                             # the right-hand column's stack steps left
    pws = phone_widths(others)
    avail = {0: 'calc(100vw - 32px)', 1: 'calc(73.88vw - 32px)', 2: 'calc(100vw - 32px)'}[col]
    anchor = {0: 'left: 16px', 1: 'left: 26.12%', 2: 'right: 16px'}[col]
    plates, edges = '', ''
    for i, name in enumerate(others):
        side = 'right' if mirror else 'left'
        plates += img(name, '30vw', '', f' {side}: calc({lefts[i]:.4f} * var(--h)); bottom: calc({STEP_Y * i:.4f} * var(--h)); z-index: {n - i}; --pw: {pws[i]};')
        if i < n - 1:
            # four hairlines join this plate's corners to the next plate's: the slab between them, drawn behind
            # (the inner-bottom edge is hidden by the front plate, as it should be)
            r0, r1 = ratio(name), ratio(others[i + 1])
            for v in ('top', 'bottom'):
                for outer in (False, True):
                    near = lefts[i] + (r0 if outer else 0)
                    far = lefts[i + 1] + (r1 if outer else 0)
                    dx, dy = far - near, STEP_Y
                    length, ang = math.hypot(dx, dy), math.degrees(math.atan2(dy, dx))
                    y = f'calc(({STEP_Y * i:.4f} + {1 if v == "top" else 0}) * var(--h))'
                    x = f'calc({near:.4f} * var(--h))'
                    rot = f'rotate({ang:.2f}deg)' if mirror else f'rotate({-ang:.2f}deg)'
                    origin = '100% 0' if mirror else '0 0'
                    edges += f'<i class="edge" style="width: calc({length:.4f} * var(--h)); bottom: {y}; {side}: {x}; transform-origin: {origin}; transform: {rot}; z-index: 0"></i>'
    # with bottom-anchoring, the stack must not clip: the stage is sh tall; shift so the front plate sits on the floor
    inner = f'<div class="stack" style="position: absolute; inset: 0; {anchor}">{edges}{plates}</div>'
    return f'  <div class="stage s-{p["id"]}" style="--sw: {sw + 0.05:.4f}; --sh: {sh + 0.04:.4f}; --avail: {avail}">{inner}</div>\n'
bodyB = ('  <div class="strip">\n' + ''.join(figure(p, '(min-width: 700px) 37vw, 100vw') for p in P) + '  </div>\n' +
         ''.join(stageB(p, k) for k, p in enumerate(P)) + '  <div class="txt">\n' + ''.join(txtrow(p) for p in P) + '  </div>')

for nn, (name, css, body) in {'01': ('accordion', cssA, bodyA), '02': ('the stack', cssB, bodyB)}.items():
    os.makedirs(f'{S}/z/out/{nn}', exist_ok=True)
    open(f'{S}/z/out/{nn}/index.html', 'w', encoding='utf-8').write(page(name, css, body))
print('written')
