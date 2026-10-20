/* the page is one character grid. a mondrian composition is cut into it:
   black lines are runs of █, colour planes are ▓, every other rectangle is
   a field of bytes (regular at the top, dissolving into noise further down)
   with kes's words written straight into it. the real, readable page for
   screen readers is the hidden <main> above. */
(function () {
  "use strict";
  var D = __DATA__;
  var PAT = "Q±0ðLDDDDDDDDDDDDDDÅÂÀ3ÏDDDDDDDDDDDDDDT,<";
  var NOISE = __NOISE__;
  var field = document.getElementById("field"), grid = document.getElementById("grid");
  var fm = document.getElementById("fm"), rv = document.getElementById("rv");
  var still = matchMedia("(prefers-reduced-motion: reduce)").matches;
  var cw = 8, lh = 16, C = 0, R = 0, cells = [];

  function measure() {
    var s = document.createElement("span");
    s.textContent = "M".repeat(200);
    s.style.cssText = "position:absolute;visibility:hidden;white-space:pre";
    grid.appendChild(s);
    cw = s.getBoundingClientRect().width / 200;
    grid.removeChild(s);
    lh = parseFloat(getComputedStyle(grid).lineHeight);
  }
  function rnd(x, y, s) {
    var h = (x * 374761393 + y * 668265263 + s * 982451653) | 0;
    h = Math.imul(h ^ (h >>> 13), 1274126177);
    return ((h ^ (h >>> 16)) >>> 0) / 4294967296;
  }

  /* ---- words ---- */
  function segs(str, cls) {
    var out = [], re = /\{([^|}]+)\|([^|}]+)\|(\w+)\}/g, m, last = 0;
    while ((m = re.exec(str))) {
      if (m.index > last) out.push({ t: str.slice(last, m.index), c: cls });
      out.push({ t: m[1], c: "a", href: m[2], k: m[3] });
      last = re.lastIndex;
    }
    if (last < str.length) out.push({ t: str.slice(last), c: cls });
    return out;
  }
  function wrap(parts, width, ind) {
    var words = [];
    parts.forEach(function (p) {
      p.t.split(/(\s+)/).forEach(function (w) { if (w) words.push({ t: w, c: p.c, href: p.href, k: p.k, sp: /^\s+$/.test(w) }); });
    });
    var lines = [], line = [], len = 0, W = width;
    function push() {
      while (line.length && line[line.length - 1].sp) { len -= 1; line.pop(); }
      lines.push({ ind: lines.length ? ind : 0, segs: line });
      line = []; len = 0; W = width - ind;
    }
    words.forEach(function (w) {
      if (w.sp) { if (len && len < W) { line.push({ t: " ", c: w.c, href: w.href, k: w.k, sp: true }); len++; } return; }
      var t = w.t;
      if (len && len + t.length > W) push();
      while (t.length > W) { line.push({ t: t.slice(0, W), c: w.c, href: w.href, k: w.k }); t = t.slice(W); push(); }
      if (t) { line.push({ t: t, c: w.c, href: w.href, k: w.k }); len += t.length; }
    });
    if (line.length) push();
    return lines;
  }
  function pad(s, n) { while (s.length < n) s += " "; return s; }
  function content(key, iw) {
    var out = [];
    (D.cells[key] || []).forEach(function (b) {
      var ty = b[0];
      if (ty === "gap") out.push({ ind: 0, segs: [] });
      else if (ty === "h" || ty === "p" || ty === "m") out = out.concat(wrap(segs(b[1], ty === "p" ? "c" : ty), iw, 0));
      else if (ty === "li") out = out.concat(wrap([{ t: "* ", c: "m" }].concat(segs(b[1], "c")), iw, 2));
      else if (ty === "kv") {
        var kw = iw < 30 ? 0 : 9;
        if (!kw) { out = out.concat(wrap(segs(b[1], "m"), iw, 0)); out = out.concat(wrap(segs(b[2], "c"), iw, 0)); }
        else out = out.concat(wrap([{ t: pad(b[1], kw), c: "m" }].concat(segs(b[2], "c")), iw, kw));
      }
      else if (ty === "art") { var a = D.art[b[1]]; if (a && a.w <= iw) out.push({ art: a }); }
      else if (ty === "img") out.push({ img: { seed: b[1], rows: b[2] } });
      else if (ty === "name") out.push({ name: true });
      else if (ty === "fm") out.push({ fm: true });
      else if (ty === "garden") out.push({ garden: true });
    });
    return out;
  }
  function nameBits(iw) {
    var big = D.name.big, small = D.name.small;
    if (big[0].length * 2 <= iw) return { bits: big, px: 2 };
    if (big[0].length <= iw) return { bits: big, px: 1 };
    if (small[0].length * 2 <= iw) return { bits: small, px: 2 };
    return { bits: small, px: 1 };
  }
  function fmRows(w) {
    if (!fm) return 12;
    fm.hidden = false;
    fm.style.width = (w * cw) + "px";
    fm.classList.toggle("narrow", w < 50);
    return Math.ceil(fm.offsetHeight / lh);
  }
  function need(key, iw) {
    var n = 0;
    content(key, iw).forEach(function (l) {
      if (l.art) n += l.art.rows.length;
      else if (l.img) n += l.img.rows;
      else if (l.name) n += nameBits(iw).bits.length;
      else if (l.fm) n += fmRows(iw);
      else if (l.garden) n += D.art.garden.rows.length;
      else n += 1;
    });
    return n + 2;
  }

  /* ---- composition ---- */
  function compose() {
    var spec = C < D.mobileBelow ? D.mobile : D.desktop;
    var V = C < D.mobileBelow ? 1 : 2, H = 1, y = 0, out = [], lines = [];
    spec.forEach(function (band, bi) {
      var n = band.cols.length, avail = C - V * (n - 1), fixed = 0, fr = 0, rest = 0;
      band.cols.forEach(function (c) { if (typeof c.w === "number" && c.w >= 1) fixed += c.w; else if (c.w === "rest") rest++; else fr += c.w; });
      var widths = band.cols.map(function (c) { return typeof c.w === "number" && c.w >= 1 ? c.w : c.w === "rest" ? 0 : Math.round((avail - fixed) * c.w); });
      var used = widths.reduce(function (a, b) { return a + b; }, 0);
      band.cols.forEach(function (c, i) { if (c.w === "rest") widths[i] = Math.max(2, Math.floor((avail - used) / rest)); });
      var colsH = band.cols.map(function (c, i) {
        return c.cells.map(function (cell) {
          if (typeof cell.h === "number") return cell.h;
          if (cell.h === "fill") return 1;
          return need(cell.k, widths[i] - 2);
        });
      });
      var bandH = Math.max(band.min || 0, Math.max.apply(null, colsH.map(function (hs) { return hs.reduce(function (a, b) { return a + b; }, 0) + (hs.length - 1) * H; })));
      var x = 0;
      band.cols.forEach(function (c, i) {
        var hs = colsH[i], tot = hs.reduce(function (a, b) { return a + b; }, 0) + (hs.length - 1) * H, extra = bandH - tot;
        var fills = c.cells.map(function (cell, j) { return cell.h === "fill" ? j : -1; }).filter(function (j) { return j > -1; });
        if (!fills.length) fills = [c.cells.length - 1];
        fills.forEach(function (j, q) { hs[j] += Math.floor(extra / fills.length) + (q < extra % fills.length ? 1 : 0); });
        var yy = y;
        c.cells.forEach(function (cell, j) {
          out.push({ x: x, y: yy, w: widths[i], h: hs[j], k: cell.k, kind: cell.kind || (cell.k ? "c" : "tex"), tex: cell.tex || "dump", id: out.length });
          yy += hs[j];
          if (j < c.cells.length - 1) { lines.push({ x: x, y: yy, w: widths[i], h: H, bw: false }); yy += H; }
        });
        x += widths[i];
        if (i < n - 1) { lines.push({ x: x, y: y, w: V, h: bandH, bw: (band.bwv || []).indexOf(i) > -1 }); x += V; }
      });
      y += bandH;
      if (bi < spec.length - 1) { lines.push({ x: 0, y: y, w: C, h: H, bw: band.line === "bw" }); y += H; }
    });
    R = y; cells = out;
    return lines;
  }

  /* ---- paint ---- */
  function render() {
    measure();
    var nc = Math.max(20, Math.floor(document.documentElement.clientWidth / cw));
    if (nc === C && grid.firstChild) return;
    C = nc;
    var lines = compose();
    var ch = [], cl = [], lk = [], hrefs = {};
    for (var y = 0; y < R; y++) { ch.push(new Array(C).fill(" ")); cl.push(new Array(C).fill("t")); lk.push(new Array(C).fill(null)); }
    function put(x, y, c, k, link) { if (y >= 0 && y < R && x >= 0 && x < C) { ch[y][x] = c; cl[y][x] = k; lk[y][x] = link || null; } }
    function linkOf(s) { if (!s.href) return null; hrefs[s.k] = s.href; return s.k; }

    cells.forEach(function (r) {
      for (var y = r.y; y < r.y + r.h; y++) for (var x = r.x; x < r.x + r.w; x++) {
        var c, k;
        if (r.kind === "P" || r.kind === "B" || r.kind === "Y" || r.kind === "K") { c = "▓"; k = r.kind; }
        else if (r.tex === "dots") { c = (x % 2 === 1) ? "." : " "; k = "nd"; }
        else if (r.tex === "hearts") { var m = (x + (y % 2) * 3) % 6; c = m === 0 ? "<" : m === 1 ? "3" : " "; k = "t"; }
        else {
          var p = Math.min(0.92, Math.pow(y / Math.max(1, R), 1.15) * 1.05);
          c = rnd(x, y, 1) < p ? NOISE.charAt(Math.floor(rnd(x, y, 2) * NOISE.length)) : PAT.charAt((x + y * 7) % PAT.length);
          k = "t";
        }
        put(x, y, c, k + " r" + r.id);
      }
    });
    lines.forEach(function (l, li) {
      for (var y = l.y; y < l.y + l.h; y++) for (var x = l.x; x < l.x + l.w; x++) {
        var k = "L";
        if (l.bw) { var q = Math.floor((l.h > 1 ? y : x) / 2); var v = rnd(q, li, 9); k = v < 0.16 ? "q0" : v < 0.27 ? "q1" : v < 0.34 ? "q2" : "Y"; }
        put(x, y, "█", k);
      }
    });
    cells.forEach(function (r) {
      if (!r.k) return;
      var iw = r.w - 2, yy = r.y + 1, rc = " r" + r.id;
      content(r.k, iw).forEach(function (l) {
        if (l.fm) { var fr = fmRows(iw); r.fm = { x: r.x + 1, y: yy }; yy += fr; return; }
        if (l.name) {
          var nb = nameBits(iw), w = nb.bits[0].length * nb.px, x0 = r.x + 1 + Math.max(0, Math.floor((iw - w) / 2));
          nb.bits.forEach(function (row, j) {
            for (var i = 0; i < row.length; i++) {
              if (row[i] !== "1") continue;
              if (nb.px === 2) { put(x0 + i * 2, yy + j, "<", "n" + rc); put(x0 + i * 2 + 1, yy + j, "3", "n" + rc); }
              else put(x0 + i, yy + j, i % 2 ? "3" : "<", "n" + rc);
            }
          });
          yy += nb.bits.length; return;
        }
        if (l.art || l.garden) {
          var a = l.art || D.art.garden;
          a.rows.forEach(function (row, j) {
            var full = l.garden ? row.repeat(Math.ceil(r.w / row.length) + 1).slice(0, r.w) : row;
            var x0 = l.garden ? r.x : r.x + 1;
            for (var i = 0; i < full.length; i++) {
              var c = full.charAt(i);
              if (c === " ") continue;
              var k = a.cls[c] || a.def;
              if (c === "<" && full.charAt(i + 1) === "3") k = "ah";
              if (c === "3" && full.charAt(i - 1) === "<") k = "ah";
              put(x0 + i, yy + j, c, k + rc);
            }
          });
          yy += a.rows.length; return;
        }
        if (l.img) {
          var ramp = " .:-=+*#%@", s = l.img.seed;
          for (var j = 0; j < l.img.rows; j++) for (var i = 0; i < iw; i++) {
            var u = i / iw, v = j / l.img.rows;
            var val = 0.5 + 0.25 * Math.sin(u * (5 + s) + v * 3 * s) + 0.25 * Math.cos(Math.hypot(u - 0.3 * s % 1, v - 0.6) * (7 + s));
            val = Math.max(0, Math.min(0.999, val + (rnd(i, j, 30 + s) - 0.5) * 0.25));
            put(r.x + 1 + i, yy + j, ramp.charAt(Math.floor(val * ramp.length)), "ig" + rc);
          }
          yy += l.img.rows; return;
        }
        var x = r.x + 1 + l.ind;
        if (l.segs.length) put(x - 1, yy, " ", "c" + rc);
        l.segs.forEach(function (s) {
          var lo = linkOf(s);
          for (var i = 0; i < s.t.length; i++) put(x + i, yy, s.t.charAt(i), (s.c === "a" ? "a" : s.c) + rc, lo);
          x += s.t.length;
        });
        if (l.segs.length && x < r.x + r.w) put(x, yy, " ", "c" + rc);
        yy++;
      });
    });

    var html = [];
    for (var y2 = 0; y2 < R; y2++) {
      var row = "", x2 = 0;
      while (x2 < C) {
        var k0 = cl[y2][x2], l0 = lk[y2][x2], run = "";
        while (x2 < C && cl[y2][x2] === k0 && lk[y2][x2] === l0) { run += ch[y2][x2]; x2++; }
        run = run.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
        if (l0) row += '<a class="' + k0 + '" href="' + hrefs[l0].replace(/&/g, "&amp;").replace(/"/g, "&quot;") + '" data-k="' + l0 + '" tabindex="-1">' + run + "</a>";
        else row += '<span class="' + k0 + '">' + run + "</span>";
      }
      html.push(row);
    }
    // a link that wraps onto two lines is two runs pointing at the same object, so they share data-k
    grid.innerHTML = html.join("\n");
    field.style.height = (R * lh) + "px";
    cells.forEach(function (r) { if (r.fm && fm) { fm.style.left = (r.fm.x * cw) + "px"; fm.style.top = (r.fm.y * lh) + "px"; fm.hidden = false; } });
  }

  /* ---- reading ---- */
  function reveal(id) {
    rv.textContent = id == null ? "" : ".r" + id + ".c,.r" + id + ".m{color:var(--read)}.r" + id + ".h{color:#000}.r" + id + ".t{color:var(--quiet)}.r" + id + ".ig{color:#777}";
  }
  var last = null;
  grid.addEventListener("mousemove", function (e) {
    var b = grid.getBoundingClientRect(), x = Math.floor((e.clientX - b.left) / cw), y = Math.floor((e.clientY - b.top) / lh), hit = null;
    cells.forEach(function (r) { if (r.k && x >= r.x && x < r.x + r.w && y >= r.y && y < r.y + r.h) hit = r.id; });
    if (hit !== last) { last = hit; reveal(hit); }
  });
  grid.addEventListener("mouseleave", function () { last = null; reveal(null); });
  function readMode() { document.body.classList.toggle("read"); var b = document.getElementById("readbtn"); if (b) b.setAttribute("aria-pressed", document.body.classList.contains("read")); }
  grid.addEventListener("click", function (e) {
    var a = e.target.closest("a");
    if (a && a.getAttribute("href") === "#read") { e.preventDefault(); readMode(); }
  });
  var rb = document.getElementById("readbtn"); if (rb) rb.addEventListener("click", readMode);
  addEventListener("keydown", function (e) { if (e.key === "r" && !e.metaKey && !e.ctrlKey && !/INPUT|TEXTAREA/.test(e.target.tagName)) readMode(); });
  // keyboard: focus lands on the hidden real links; light up their twin in the grid
  document.querySelectorAll("main.sr a[data-k]").forEach(function (a) {
    a.addEventListener("focus", function () {
      var twins = grid.querySelectorAll('a[data-k="' + a.dataset.k + '"]');
      twins.forEach(function (t) { t.classList.add("f"); });
      if (twins[0]) { var m = twins[0].className.match(/r(\d+)/); reveal(m ? +m[1] : null); twins[0].scrollIntoView({ block: "center" }); }
    });
    a.addEventListener("blur", function () { grid.querySelectorAll("a.f").forEach(function (t) { t.classList.remove("f"); }); reveal(null); });
  });

  var t0;
  addEventListener("resize", function () { clearTimeout(t0); t0 = setTimeout(render, 120); });
  render();
  window.__beat = function () { if (still) return; field.dataset.beat = ((+field.dataset.beat || 0) + 1) % 4; };
})();
