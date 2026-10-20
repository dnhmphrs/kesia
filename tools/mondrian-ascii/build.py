"""Build the hand-made Mondrian x ASCII version of Kes's site (home + writing).

usage: python3 build.py <outdir>
"""
import html, json, re, sys
from pathlib import Path

HERE = Path(__file__).parent
S = HERE.parent.parent
KIT = S / "kit" / "pieces"
OUT = Path(sys.argv[1])
OUT.mkdir(parents=True, exist_ok=True)

# ---- source material -------------------------------------------------------
def pres(path):
    t = path.read_text()
    return [(a, html.unescape(re.sub(r"<[^>]+>", "", b))) for a, b in re.findall(r"<pre([^>]*)>(.*?)</pre>", t, re.S)]

def bits(art):
    """the heart sign is drawn in 2-char cells: '<3' on, ' .' off"""
    rows = []
    for line in art.split("\n"):
        line = line.rstrip()
        if not line.startswith(" | ") or "<3" not in line and ". ." not in line:
            continue
        inner = line[2:-2] if line.endswith(" |") else line[2:]
        cells = [inner[i:i + 2] for i in range(0, len(inner) - 1, 2)]
        rows.append("".join("1" if c == "<3" else "0" for c in cells))
    rows = [r for r in rows if "1" in r]
    left = min(r.index("1") for r in rows)
    right = max(len(r) - r[::-1].index("1") for r in rows)
    return [r[left:right] for r in rows]

name_pres = pres(KIT / "i5-03-name-hearts" / "piece.html")
big = bits([b for a, b in name_pres if 'class="big"' in a][0])
small = bits([b for a, b in name_pres if 'class="small"' in a][0])

speaker = [l.rstrip() for l in pres(KIT / "i7-05-speaker" / "piece.html")[0][1].split("\n") if l.strip()]
computer = [l.rstrip() for l in pres(KIT / "i5-08-heart-computer" / "piece.html")[0][1].split("\n") if l.strip()]
garden = [l for l in pres(KIT / "i5-03-garden" / "piece.html")[0][1].split("\n") if l.strip()]
gw = max(len(l) for l in garden)
garden = [l.ljust(gw) for l in garden]

ex = (S / "tools" / "ascii-field-example.txt").read_text(errors="replace")
noise = "".join(sorted(set(c for c in ex[1200:] if c.isprintable() and not c.isspace() and c not in "<>&�")))

ART = {
    "speaker": {"rows": speaker, "w": max(map(len, speaker)), "def": "ar", "cls": {"K": "h", "E": "h", "S": "h", "F": "h", "M": "h"}},
    "computer": {"rows": computer, "w": max(map(len, computer)), "def": "ab", "cls": {}},
    "garden": {"rows": garden, "w": gw, "def": "ar", "cls": {"@": "g1", "*": "g1", "(": "g2", ")": "g2", "_": "g2", "v": "g4", "V": "g4"}},
}

# ---- content (links written {text|url}) ------------------------------------
MAIL = "mailto:inkersolekesia@gmail.com"
home = {
    "name": [["name"]],
    "hello": [
        ["h", "hello, i'm kes <3"], ["gap"],
        ["p", "i'm kes inkersole (kesia on paper), a freelance creative strategist and internet equalities researcher based in london. welcome to kes' little corner of the internet."], ["gap"],
        ["p", "my practice focuses on understanding and critiquing the impacts of emerging technologies on people, culture, and the planet. i work collectively to rethink the narratives and behaviours surrounding technologies — prioritising collaborative research as a process for testing, imagining and prototyping more equitable, alternative futures."],
    ],
    "fm": [["fm"]],
    "speaker": [["art", "speaker"]],
    "cv": [
        ["m", "this website presents"], ["h", "kes inkersole"],
        ["p", "creative strategist, internet equalities researcher, london. available for work."], ["gap"],
        ["kv", "does", "creative strategy, research, workshops, writing and teaching"],
        ["kv", "teaches", "associate lecturer at UAL (LCF + CCI)"],
        ["kv", "clients", "Neu Futur, DAZED, co—matter, MØRNING, WeTransfer, Protein, Midnight Agency, Softer, Selfridges"],
        ["kv", "school", "MA internet equalities, BA creative direction, PhD [ ? ]"],
        ["kv", "cv", "cv & portfolio on request"],
        ["kv", "email", "{inkersolekesia@gmail.com|" + MAIL + "}"], ["gap"],
        ["m", "{[ read mode ]|#read} or press r"],
    ],
    "p1": [["m", "01 · for fun"], ["h", "{latent space|https://latent-space.vercel.app/}"], ["gap"], ["img", 1, 7], ["gap"],
           ["p", "lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. ut enim ad minim veniam."]],
    "p2": [["m", "02 · for funds"], ["h", "{networked worlds|https://co-matter.com/project/networked-worlds} with co—matter"], ["gap"], ["img", 2, 7], ["gap"],
           ["p", "duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. excepteur sint occaecat cupidatat non proident."]],
    "p3": [["m", "03 · for funds"], ["h", "{protein dirty words #4: community report|https://www.protein.xyz/dirty-words-4-community/}"], ["gap"], ["img", 3, 7], ["gap"],
           ["p", "sed ut perspiciatis unde omnis iste natus error sit voluptatem accusantium doloremque laudantium, totam rem aperiam, eaque ipsa quae ab illo."]],
    "more": [["h", "more projects"],
             ["li", "{pro(tech)t|https://protecht.vercel.app/} (for fun)"],
             ["li", "{MØRNING Ø|https://www.instagram.com/p/CwOEAMetgc1/?img_index=1} (for funds)"]],
    "chain": [["h", "my writing"], ["p", "new: short pieces from my notes app, sent in by email. it's called {chainmail|writing.html}."]],
    "written": [["h", "things i've written"],
                ["li", "{mindy seu on sex and the internet|https://www.protein.xyz/sex-and-the-internet/} (Protein)"],
                ["li", "{dreaming and designing a more accessible web|https://midnight.agency/thoughts/dreaming-and-designing-more-accessible-web} (Midnight Agency)"],
                ["li", "{coding a more creative and playful web|https://midnight.agency/thoughts/coding-a-more-creative-and-playful-web} (Midnight Agency)"],
                ["li", "{composing a flexible and modular web|https://midnight.agency/thoughts/composing-a-flexible-and-modular-web} (Midnight Agency)"],
                ["li", "{burn after reading: uh oh, meet o|https://morningfyi.substack.com/p/020-uh-oh-meet} (morningfyi)"],
                ["li", "{burn after reading: entering limbo|https://morningfyi.substack.com/p/024-entering-limb-with} (morningfyi)"]],
    "pods": [["h", "podcasts, for the bus"],
             ["li", "{mindy seu on collaboration, community and the cyberfeminism index|https://podcasts.apple.com/gb/podcast/mindy-seu-on-collaboration-community-and/id1449302502?i=1000597869409}"],
             ["li", "{what can web2 organisations learn from web3 communities?|https://soundcloud.com/proteincommunity/protein-forum-what-can-web2-organisations-learn-from-web3-communities} (Protein)"],
             ["li", "{cherie hu on water & music's journey through web3|https://podcasts.apple.com/gb/podcast/cherie-hu-on-water-musics-journey-through-web3/id1449302502?i=1000581859804}"],
             ["li", "{molly dickson on dao activism|https://podcasts.apple.com/gb/podcast/molly-dickson-on-dao-activism-and-fighting-for/id1449302502?i=1000578164761}"],
             ["li", "{dame on education, accessibility and inclusivity in web3|https://podcasts.apple.com/gb/podcast/dame-on-the-need-for-education-accessibility/id1449302502?i=1000559829008}"],
             ["li", "{nadia piet on creative ai and protopian futures|https://podcasts.apple.com/gb/podcast/nadia-piet-on-creative-ai-and-protopian-futures/id1449302502?i=1000559822732}"],
             ["li", "{cyn bahati on her journey into web3 with her family|https://podcasts.apple.com/gb/podcast/cyn-bahati-on-her-journey-into-web3-with-her-family/id1449302502?i=1000559818509}"],
             ["li", "{latasha on the potential of web3 for music artists|https://podcasts.apple.com/gb/podcast/latash%C3%A1-on-the-potential-of-web3-for-music-artists/id1449302502?i=1000552812458}"]],
    "irl": [["h", "irl (mostly)"],
            ["li", "{olden residency|https://www.instagram.com/p/DRjYCG8jARb/?img_index=1}"],
            ["li", "{softer london|https://www.instagram.com/p/C52uHshIkjq/?img_index=1} (talk + workshop)"],
            ["li", "{tech yard|https://www.arts.ac.uk/creative-computing-institute/public-programme/tech-yard} (workshop)"],
            ["li", "{ovar it|https://www.instagram.com/p/BslwSSPH5Rc/?img_index=2}"]],
    "note": [["p", "this website is mostly plain text: system fonts, no trackers, no photos, one radio that stays quiet until you ask. it's easy for me to update and it loads fine on bad wifi."], ["gap"],
             ["p", "thanks for stopping by <3"], ["p", "say hello: {inkersolekesia@gmail.com|" + MAIL + "}"]],
    "garden": [["garden"]],
}

pieces = [
    ("lorem ipsum", "no. 011 · 18 oct 2026", ["lorem ipsum dolor sit amet."]),
    ("consectetur adipiscing elit", "no. 010 · 14 oct 2026", ["sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur.", "excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum. sed ut perspiciatis unde omnis iste natus error sit voluptatem accusantium doloremque laudantium.", "totam rem aperiam, eaque ipsa quae ab illo inventore veritatis et quasi architecto beatae vitae dicta sunt explicabo."]),
    ("(no subject)", "no. 009 · 9 oct 2026", ["nemo enim ipsam voluptatem quia voluptas sit aspernatur aut odit aut fugit."]),
    ("sed quia consequuntur", "no. 008 · 6 oct 2026", ["magni dolores eos qui ratione voluptatem sequi nesciunt. neque porro quisquam est, qui dolorem ipsum quia dolor sit amet, consectetur, adipisci velit, sed quia non numquam eius modi tempora incidunt ut labore et dolore magnam aliquam quaerat voluptatem."]),
    ("ut enim ad minima", "no. 007 · 2 oct 2026", ["quis autem vel eum", "iure reprehenderit", "qui in ea voluptate", "velit esse quam nihil", "molestiae consequatur"]),
    ("at vero eos et accusamus", "no. 006 · 27 sep 2026", ["et iusto odio dignissimos ducimus qui blanditiis praesentium voluptatum deleniti atque corrupti quos dolores et quas molestias excepturi sint occaecati cupiditate non provident.", "similique sunt in culpa qui officia deserunt mollitia animi, id est laborum et dolorum fuga. et harum quidem rerum facilis est et expedita distinctio."]),
    ("nam libero", "no. 005 · 21 sep 2026", ["tempore, cum soluta nobis est eligendi optio."]),
    ("re: temporibus autem quibusdam", "no. 004 · 14 sep 2026", ["et aut officiis debitis aut rerum necessitatibus saepe eveniet ut et voluptates repudiandae sint et molestiae non recusandae. itaque earum rerum hic tenetur a sapiente delectus, ut aut reiciendis voluptatibus maiores alias consequatur aut perferendis doloribus asperiores repellat."]),
    ("quis nostrum exercitationem", "no. 003 · 3 sep 2026", ["ullam corporis suscipit laboriosam, nisi ut aliquid ex ea commodi consequatur. quis autem vel eum iure reprehenderit qui in ea voluptate velit esse quam nihil molestiae consequatur, vel illum qui dolorem eum fugiat quo voluptas nulla pariatur.", "lorem ipsum dolor sit amet, consectetur adipiscing elit. integer nec odio. praesent libero. sed cursus ante dapibus diam. sed nisi. nulla quis sem at nibh elementum imperdiet. duis sagittis ipsum.", "curabitur sodales ligula in libero."]),
    ("sed dignissim lacinia", "no. 002 · 28 aug 2026", ["nunc. curabitur tortor. pellentesque nibh. aenean quam. in scelerisque sem at dolor. maecenas mattis. sed convallis tristique sem."]),
    ("hello, lorem", "no. 001 · 15 aug 2026", ["proin ut ligula vel nunc egestas porttitor. morbi lectus risus, iaculis vel, suscipit quis, luctus non, massa. fusce ac turpis quis ligula lacinia aliquet.", "mauris ipsum."]),
]
writing = {
    "head": [["m", "{<- kes inkersole|index.html}"], ["gap"], ["h", "chainmail (working title)"], ["gap"],
             ["p", "my own writing. short pieces, the kind i write in my notes app, sent here by email and collected over time into a kind of text moodboard."], ["gap"],
             ["m", "by email"],
             ["p", "each piece arrives as an email to (address tbc). the subject line becomes its title and the newest one lands at the top."], ["gap"],
             ["m", "{[ read mode ]|#read} or press r"]],
    "pc": [["art", "computer"]],
    "garden": [["garden"]],
}
for i, (title, meta, paras) in enumerate(pieces, 1):
    b = [["m", meta], ["h", title], ["gap"]]
    for j, p in enumerate(paras):
        if j: b.append(["gap"])
        b.append(["p", p])
    writing["a%d" % i] = b

# ---- link keys, shared by the grid and the hidden real page ----------------
def key_links(cells, prefix):
    n = [0]
    def sub(m):
        n[0] += 1
        return "{%s|%s|%s%d}" % (m.group(1), m.group(2), prefix, n[0])
    for k in cells:
        for b in cells[k]:
            for i, v in enumerate(b):
                if i and isinstance(v, str):
                    b[i] = re.sub(r"\{([^|}]+)\|([^|}]+)\}", sub, v)
key_links(home, "h")
key_links(writing, "w")

# ---- compositions ------------------------------------------------------------
def c(k=None, kind=None, h=None, tex=None):
    d = {}
    if k: d["k"] = k
    if kind: d["kind"] = kind
    if h is not None: d["h"] = h
    if tex: d["tex"] = tex
    return d

home_desktop = [
    {"cols": [{"w": "rest", "cells": [c("name", tex="dots")]},
              {"w": 0.07, "cells": [c(kind="Y", h=3), c(kind="K", h=2), c(kind="B", h="fill")]}], "line": "L"},
    {"cols": [{"w": 0.25, "cells": [c("hello"), c(kind="P", h="fill")]},
              {"w": 0.34, "cells": [c("fm"), c("speaker", tex="dots")]},
              {"w": 0.26, "cells": [c("cv"), c(kind="Y", h=3), c(h="fill", tex="hearts")]},
              {"w": "rest", "cells": [c(kind="B", h=6), c(h=4, tex="hearts"), c(kind="K", h=2), c(h=3), c(kind="P", h="fill")]}],
     "line": "bw", "bwv": [2]},
    {"cols": [{"w": 0.27, "cells": [c("p1")]},
              {"w": 0.05, "cells": [c(kind="Y", h=2), c(h=3), c(kind="P", h=2), c(h=2, tex="hearts"), c(kind="B", h="fill")]},
              {"w": 0.27, "cells": [c("p2")]},
              {"w": 0.27, "cells": [c("p3")]},
              {"w": "rest", "cells": [c(kind="K", h=3), c(h=4), c(kind="Y", h="fill")]}], "line": "L"},
    {"cols": [{"w": 0.2, "cells": [c("more"), c(kind="Y", h=3), c("chain"), c(h="fill")]},
              {"w": 0.31, "cells": [c("written"), c(kind="P", h="fill")]},
              {"w": 0.3, "cells": [c("pods")]},
              {"w": "rest", "cells": [c("irl"), c(kind="K", h=2), c("note"), c(kind="B", h="fill")]}], "line": "L"},
    {"cols": [{"w": "rest", "cells": [c("garden", tex="dots")]}]},
]
home_mobile = [
    {"cols": [{"w": "rest", "cells": [c("name", tex="dots")]}, {"w": 4, "cells": [c(kind="Y", h=3), c(kind="B", h="fill")]}], "line": "L"},
    {"cols": [{"w": "rest", "cells": [c("fm")]}], "line": "bw"},
    {"cols": [{"w": "rest", "cells": [c("hello")]}, {"w": 3, "cells": [c(kind="P", h="fill")]}], "line": "L"},
    {"cols": [{"w": "rest", "cells": [c("speaker", tex="dots"), c(kind="Y", h=2)]}], "line": "L"},
    {"cols": [{"w": "rest", "cells": [c("cv")]}], "line": "L"},
    {"cols": [{"w": 4, "cells": [c(kind="B", h="fill")]}, {"w": "rest", "cells": [c("p1")]}], "line": "L"},
    {"cols": [{"w": "rest", "cells": [c("p2")]}, {"w": 3, "cells": [c(kind="P", h=4), c(h="fill", tex="hearts")]}], "line": "L"},
    {"cols": [{"w": "rest", "cells": [c("p3"), c(kind="K", h=2)]}], "line": "L"},
    {"cols": [{"w": "rest", "cells": [c("more"), c(kind="Y", h=2), c("chain")]}], "line": "L"},
    {"cols": [{"w": "rest", "cells": [c("written")]}], "line": "L"},
    {"cols": [{"w": "rest", "cells": [c("pods")]}, {"w": 3, "cells": [c(kind="Y", h="fill")]}], "line": "L"},
    {"cols": [{"w": "rest", "cells": [c("irl"), c(kind="P", h=2), c("note")]}], "line": "L"},
    {"cols": [{"w": "rest", "cells": [c("garden", tex="dots")]}]},
]
writing_desktop = [
    {"cols": [{"w": 0.58, "cells": [c("head")]},
              {"w": 0.26, "cells": [c("pc", tex="dots"), c(kind="P", h="fill")]},
              {"w": "rest", "cells": [c(kind="Y", h=4), c(h=3, tex="hearts"), c(kind="B", h="fill")]}], "line": "bw"},
    {"cols": [{"w": 0.34, "cells": [c("a1"), c(kind="Y", h=2), c("a2")]},
              {"w": 0.3, "cells": [c("a3"), c("a4")]},
              {"w": 0.24, "cells": [c("a5"), c(kind="K", h=2), c("a6")]},
              {"w": "rest", "cells": [c(kind="P", h=5), c(h="fill")]}], "line": "L"},
    {"cols": [{"w": 0.22, "cells": [c("a7"), c(kind="B", h="fill")]},
              {"w": 0.36, "cells": [c("a8")]},
              {"w": 0.27, "cells": [c("a9"), c("a10")]},
              {"w": "rest", "cells": [c("a11"), c(kind="Y", h="fill")]}], "line": "L"},
    {"cols": [{"w": "rest", "cells": [c("garden", tex="dots")]}]},
]
writing_mobile = [
    {"cols": [{"w": "rest", "cells": [c("head")]}, {"w": 4, "cells": [c(kind="Y", h=3), c(kind="P", h="fill")]}], "line": "bw"},
    {"cols": [{"w": "rest", "cells": [c("pc", tex="dots")]}], "line": "L"},
]
for i in range(1, 12):
    side = [None, {"w": 3, "cells": [c(kind="B", h="fill")]}, None, {"w": 3, "cells": [c(kind="P", h=3), c(h="fill", tex="hearts")]}][i % 4]
    cols = [{"w": "rest", "cells": [c("a%d" % i)]}]
    if side: cols.append(side)
    writing_mobile.append({"cols": cols, "line": "L"})
writing_mobile.append({"cols": [{"w": "rest", "cells": [c("garden", tex="dots")]}]})

# ---- the hidden real page ----------------------------------------------------
def inline(s):
    out, last = "", 0
    for m in re.finditer(r"\{([^|}]+)\|([^|}]+)\|(\w+)\}", s):
        out += html.escape(s[last:m.start()])
        href, text = m.group(2), m.group(1)
        if href == "#read":
            out += '<button type="button" id="readbtn" aria-pressed="false">read mode</button>'
        else:
            out += '<a href="%s" data-k="%s">%s</a>' % (html.escape(href), m.group(3), html.escape(text))
        last = m.end()
    return out + html.escape(s[last:])

def sr(cells, order, h1, articles=False):
    out = ["<h1>%s</h1>" % h1]
    for k in order:
        blocks = cells[k]
        body, ul = [], []
        def flush():
            if ul:
                body.append("<ul>" + "".join("<li>%s</li>" % x for x in ul) + "</ul>")
                ul.clear()
        for b in blocks:
            t = b[0]
            if t != "li": flush()
            if t == "h": body.append("<h2>%s</h2>" % inline(b[1]))
            elif t in ("p", "m"): body.append("<p>%s</p>" % inline(b[1]))
            elif t == "li": ul.append(inline(b[1]))
            elif t == "kv": body.append("<p>%s: %s</p>" % (html.escape(b[1]), inline(b[2])))
            elif t == "img": body.append('<p>(picture to come)</p>')
        flush()
        if not body: continue
        out.append(("<article>%s</article>" if articles and k.startswith("a") else "<section>%s</section>") % "".join(body))
    return "\n".join(out)

FM = """<div id="fm" hidden>
<div class="ln"><span class="h">KES FM 170.0</span> <span class="m">pirate radio (it's just this website)</span></div>
<div class="ln"><span class="c">a jungle machine running in your browser: every drum and bassline synthesised live, no samples, no files. nothing plays until you press on air, and stop always stops it.</span></div>
<div class="ln"><span class="m">status</span> <span class="status" id="status" role="status">off air</span></div>
<div class="ticker" aria-hidden="true"><div><span>big up all the junglists · big up everyone reading the source · big up the UAL lot, LCF + CCI · text in: inkersolekesia@gmail.com · respect to the sound systems, pirates and producers who built all this · </span><span>big up all the junglists · big up everyone reading the source · big up the UAL lot, LCF + CCI · text in: inkersolekesia@gmail.com · respect to the sound systems, pirates and producers who built all this · </span></div></div>
<div class="tracker" id="tracker" aria-hidden="true">""" + "".join('<span class="rest">--</span>' for _ in range(32)) + """</div>
<div class="ln" aria-hidden="true"><span id="lcdinfo" class="m">break: straight · bass: sub · cute: off · 170bpm</span></div>
<div class="ln keys"><button class="go" id="go" type="button" aria-pressed="false">[&gt; on air]</button> <button class="stop" id="stop" type="button">[# stop]</button></div>
<div class="ln keys" role="group" aria-label="break"><span class="m">break</span> <button type="button" data-break="straight" aria-pressed="true">[straight]</button> <button type="button" data-break="chopped" aria-pressed="false">[chopped]</button> <button type="button" data-break="rollin" aria-pressed="false">[rollin']</button> <button type="button" id="chop" aria-pressed="false">[x chop it]</button></div>
<div class="ln keys" role="group" aria-label="bass"><span class="m">bass </span> <button type="button" data-bass="sub" aria-pressed="true">[sub]</button> <button type="button" data-bass="reese" aria-pressed="false">[reese]</button> <button type="button" data-bass="off" aria-pressed="false">[off]</button></div>
<div class="ln keys"><button type="button" id="cute" aria-pressed="false">[cute]</button> <button type="button" id="pullup">[&lt;&lt; pull up]</button> <button type="button" id="siren">[siren]</button> <label class="vol"><span class="m">vol</span> <input type="range" id="vol" min="0" max="1" step="0.05" value="0.5"></label></div>
<div class="ln"><span class="m">text in your shout-outs:</span> <a href="mailto:inkersolekesia@gmail.com">inkersolekesia@gmail.com</a></div>
</div>
<button class="floatstop" id="floatstop" type="button" hidden>[# stop KES FM]</button>"""

CSS = """
:root {
  --paper: #fafaf7; --tex: #c8c8c4; --ink: #a9a9a4; --head: #95958f; --meta: #bdbdb8;
  --read: #1b1b1b; --quiet: #ececE8;
  --line: #121212; --pink: #ff2e93; --blue: #1f3dff; --yellow: #ffcf1a;
  --mono: ui-monospace, Menlo, Consolas, "DejaVu Sans Mono", "Liberation Mono", "Courier New", monospace;
}
html, body { margin: 0; background: var(--paper); }
body { font: 13px/1.2 var(--mono); color: var(--ink); overflow-x: hidden; }
#field { position: relative; overflow: hidden; }
#grid { margin: 0; font: inherit; line-height: inherit; white-space: pre; }
#grid span, #grid a { transition: color .25s; }
.t { color: var(--tex); } .nd { color: #dcdcd8; } .c { color: var(--ink); } .h { color: var(--head); } .m { color: var(--meta); }
.L { color: var(--line); } .K { color: #1a1a1a; } .P { color: var(--pink); } .B { color: var(--blue); } .Y { color: var(--yellow); }
.n { color: var(--pink); } .ah { color: var(--pink); } .ar { color: #a9a9a4; } .ab { color: #8f9bff; } .ig { color: #b7b7b2; }
.g1 { color: var(--pink); } .g2 { color: #8f9bff; } .g4 { color: #c2c2bd; }
.q0 { color: var(--pink); } .q1 { color: var(--blue); } .q2 { color: #c4c4c0; }
#field[data-beat="1"] .q0 { color: var(--blue); } #field[data-beat="1"] .q1 { color: #c4c4c0; } #field[data-beat="1"] .q2 { color: var(--pink); }
#field[data-beat="2"] .q0 { color: #c4c4c0; } #field[data-beat="2"] .q1 { color: var(--pink); } #field[data-beat="2"] .q2 { color: var(--blue); }
#field.lit .n { color: var(--blue); }
a { color: var(--blue); text-decoration: none; }
#grid a.a, #grid a { color: var(--blue); }
#grid a:hover, #grid a.f { background: var(--pink); color: #fff; }
body.read .c, body.read .m { color: var(--read); } body.read .h { color: #000; } body.read .t, body.read .nd { color: var(--quiet); } body.read .ig { color: #888; }
main.sr, .sr { position: absolute !important; width: 1px; height: 1px; overflow: hidden; clip: rect(0 0 0 0); clip-path: inset(50%); white-space: nowrap; }
#fm { position: absolute; z-index: 2; white-space: normal; color: var(--ink); }
#fm .ln, #fm .ticker, #fm .tracker { display: block; }
#fm .ln > *, #fm .ticker, #fm .tracker span { background: var(--paper); }
#fm .h { color: #000; } #fm .c { color: var(--head); }
#fm .status { color: var(--pink); }
#fm button { font: inherit; line-height: inherit; color: var(--blue); background: var(--paper); border: 0; padding: 0; margin: 0; cursor: pointer; }
#fm button:hover { background: var(--pink); color: #fff; }
#fm button[aria-pressed="true"] { background: #121212; color: var(--paper); }
#fm button.go { color: var(--pink); }
#fm button:focus-visible, #fm input:focus-visible, main.sr :focus { outline: 2px solid var(--pink); outline-offset: 1px; }
#fm .vol { white-space: nowrap; }
#fm input[type=range] { width: 12ch; height: 1em; margin: 0; vertical-align: -2px; accent-color: var(--blue); }
#fm .ticker { overflow: hidden; white-space: nowrap; color: var(--meta); }
#fm .ticker > div { display: inline-block; }
#fm .tracker { display: grid; grid-template-columns: repeat(16, 3ch); color: var(--meta); }
#fm.narrow .tracker { grid-template-columns: repeat(8, 3ch); }
#fm .tracker .rest { color: var(--tex); } #fm .tracker .rev { color: var(--pink); } #fm .tracker .up { color: var(--blue); }
#fm .tracker .roll { text-decoration: underline; }
#fm .tracker .on { background: var(--pink); color: #fff; }
.floatstop { position: fixed; right: 12px; bottom: 12px; z-index: 5; font: 13px/1.2 var(--mono); color: #fff; background: var(--pink); border: 0; padding: 2px 4px; cursor: pointer; }
.floatstop[hidden], #fm[hidden] { display: none; }
@media (prefers-reduced-motion: no-preference) { #fm .ticker > div { animation: run 60s linear infinite; } }
@keyframes run { to { transform: translateX(-50%); } }
"""

PRELUDE = """var onAir = false;
var happy = false;
var still = matchMedia("(prefers-reduced-motion: reduce)").matches;
function look() { if (window.__beat) window.__beat(); }
"""

def page(title, desc, cells, desktop, mobile, order, h1, with_fm, articles):
    data = {"cells": cells, "art": ART, "name": {"big": big, "small": small}, "desktop": desktop, "mobile": mobile, "mobileBelow": 110}
    core = (HERE / "core.js").read_text().replace("__DATA__", json.dumps(data, ensure_ascii=False)).replace("__NOISE__", json.dumps(noise, ensure_ascii=False))
    engine = (HERE / "engine.js").read_text() if with_fm else ""
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<meta name="description" content="{desc}">
<style>{CSS}</style>
<style id="rv"></style>
</head>
<body>
<main class="sr">
{sr(cells, order, h1, articles)}
</main>
<div id="field" class="tower"><pre id="grid" aria-hidden="true"></pre>{FM if with_fm else ""}</div>
<script>
{core}
</script>
{"<script>" + PRELUDE + engine + "</script>" if with_fm else ""}
<script>console.log("hi, it's kes. everything on this page is a character. view source is free, take whatever's useful <3");</script>
</body>
</html>
"""

desc = "Kes Inkersole: freelance creative strategist and internet equalities researcher, based in london."
(OUT / "index.html").write_text(page("kes inkersole", desc, home, home_desktop, home_mobile,
    ["hello", "cv", "p1", "p2", "p3", "more", "chain", "written", "pods", "irl", "note"], "kes inkersole", True, False))
(OUT / "writing.html").write_text(page("chainmail · kes inkersole", "chainmail: short pieces of writing by Kes Inkersole, sent in by email.", writing, writing_desktop, writing_mobile,
    ["head"] + ["a%d" % i for i in range(1, 12)], "chainmail (working title)", False, True))
print("wrote", OUT / "index.html", (OUT / "index.html").stat().st_size, "and writing.html", (OUT / "writing.html").stat().st_size)
print("name bits", len(big), "x", len(big[0]), "small", len(small), "x", len(small[0]), "noise chars", len(noise))
