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
/* the project sheets: without webgl they open in place of the strip by #target (one at a time) */
.p { display: none; }
.p:target { display: block; }
.p:target ~ .page .strip { display: none; }
.sheet > header { border-bottom: 1px solid var(--line); }
.sheet > header .x { color: var(--grey); text-decoration: none; }
.sheet > header .x:hover { color: var(--ink); }
.pics { display: flex; gap: 1px; justify-content: flex-start; }
.pics img { display: block; width: auto; height: min(78vh, calc((100vw - 3px) / var(--sum))); }
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

/* with webgl: the dom is the invisible, clickable, scrollable truth; the canvas behind it draws the sheets in 3d */
html.gl, html.gl body { background: transparent; }
canvas.gl { display: none; }
html.gl canvas.gl { position: fixed; inset: 0; width: 100%; height: 100%; z-index: -1; display: block; }
html.gl .page { opacity: 0; }
html.gl .p, html.gl .p:target, html.measuring .p { display: block; position: fixed; inset: 0; overflow: auto; opacity: 0; visibility: hidden; z-index: 2; }
html.measuring .page { opacity: 0; }
html.gl .p.open { visibility: visible; }
html.gl .p:target ~ .page .strip { display: flex; }
html.gl.away .page { visibility: hidden; }
html.gl.away body { overflow: hidden; }
html.gl.moving .page, html.gl.moving .p { pointer-events: none; }
"""

JS = r"""
(function () {
  'use strict';
  var P = __P__;
  var canvas = document.createElement('canvas'); canvas.className = 'gl';
  var gl = canvas.getContext('webgl', { antialias: true, alpha: false, depth: true, preserveDrawingBuffer: true });
  var reduce = matchMedia('(prefers-reduced-motion: reduce)').matches;
  if (!gl || reduce || /\bnogl\b/.test(location.search)) return;
  var html = document.documentElement; document.body.appendChild(canvas);   // the page stays plain until the sheets are built

  var DPR = Math.min(window.devicePixelRatio || 1, 2);
  // ---------- gl: one quad, placed and tinted by uniforms ----------
  function shader(type, src) { var s = gl.createShader(type); gl.shaderSource(s, src); gl.compileShader(s); return s; }
  var prog = gl.createProgram();
  gl.attachShader(prog, shader(gl.VERTEX_SHADER,
    'attribute vec2 aUV; uniform mat4 uVP; uniform vec4 uRect; uniform float uTop; uniform float uZ; varying vec2 vUV;' +
    'void main(){ vUV = aUV; vec2 p = uRect.xy + aUV * uRect.zw; gl_Position = uVP * vec4(p.x, uTop - p.y, uZ, 1.0); }'));
  gl.attachShader(prog, shader(gl.FRAGMENT_SHADER,
    'precision mediump float; uniform sampler2D uTex; uniform float uFade; uniform float uReveal; uniform float uAlpha; varying vec2 vUV;' +
    'void main(){ vec4 c = texture2D(uTex, vUV); c = mix(vec4(1.0), c, uReveal); c = mix(c, vec4(1.0), uFade); gl_FragColor = vec4(c.rgb, uAlpha); }'));
  gl.linkProgram(prog); gl.useProgram(prog);
  var quadBuf = gl.createBuffer(); gl.bindBuffer(gl.ARRAY_BUFFER, quadBuf);
  gl.bufferData(gl.ARRAY_BUFFER, new Float32Array([0, 0, 1, 0, 0, 1, 1, 1]), gl.STATIC_DRAW);
  var aUV = gl.getAttribLocation(prog, 'aUV'); gl.enableVertexAttribArray(aUV); gl.vertexAttribPointer(aUV, 2, gl.FLOAT, false, 0, 0);
  var U = {}; ['uVP', 'uRect', 'uTop', 'uZ', 'uTex', 'uFade', 'uReveal', 'uAlpha'].forEach(function (n) { U[n] = gl.getUniformLocation(prog, n); });
  gl.enable(gl.DEPTH_TEST); gl.depthFunc(gl.LEQUAL); gl.enable(gl.BLEND); gl.blendFunc(gl.SRC_ALPHA, gl.ONE_MINUS_SRC_ALPHA); gl.clearColor(1, 1, 1, 1);
  var lineProg = gl.createProgram();
  gl.attachShader(lineProg, shader(gl.VERTEX_SHADER, 'attribute vec3 aPos; uniform mat4 uVP; uniform float uTop; uniform float uZ; void main(){ gl_Position = uVP * vec4(aPos.x, uTop - aPos.y, aPos.z + uZ, 1.0); }'));
  gl.attachShader(lineProg, shader(gl.FRAGMENT_SHADER, 'precision mediump float; uniform vec4 uColor; void main(){ gl_FragColor = uColor; }'));
  gl.linkProgram(lineProg);
  var L = {}; ['uVP', 'uTop', 'uZ', 'uColor'].forEach(function (n) { L[n] = gl.getUniformLocation(lineProg, n); }); var aPos = gl.getAttribLocation(lineProg, 'aPos');
  var dynBuf = gl.createBuffer(), BONE = DPR > 1 ? [0.63, 0.63, 0.63] : [0.72, 0.72, 0.72];
  function lines(buf, count, top, z, alpha, vp) {
    gl.useProgram(lineProg); gl.uniformMatrix4fv(L.uVP, false, vp); gl.uniform1f(L.uTop, top); gl.uniform1f(L.uZ, z); gl.uniform4f(L.uColor, BONE[0], BONE[1], BONE[2], alpha);
    gl.bindBuffer(gl.ARRAY_BUFFER, buf); gl.enableVertexAttribArray(aPos); gl.vertexAttribPointer(aPos, 3, gl.FLOAT, false, 0, 0); gl.drawArrays(gl.LINES, 0, count);
    gl.useProgram(prog); gl.bindBuffer(gl.ARRAY_BUFFER, quadBuf); gl.enableVertexAttribArray(aUV); gl.vertexAttribPointer(aUV, 2, gl.FLOAT, false, 0, 0);
  }
  // the bones of a layout: every box of it as four hairlines, in the sheet's own page coordinates
  function bones(root, sel) {
    var o = root.getBoundingClientRect(), v = [], els = root.querySelectorAll(sel), i, r;
    function box(x, y, w, h) { v.push(x, y, 0, x + w, y, 0, x + w, y, 0, x + w, y + h, 0, x + w, y + h, 0, x, y + h, 0, x, y + h, 0, x, y, 0); }
    box(0, 0, Math.round(o.width), Math.round(Math.max(o.height, root.scrollHeight)));
    for (i = 0; i < els.length; i++) { r = els[i].getBoundingClientRect(); if (r.width && r.height) box(r.left - o.left, r.top - o.top, r.width, r.height); }
    var buf = gl.createBuffer(); gl.bindBuffer(gl.ARRAY_BUFFER, buf); gl.bufferData(gl.ARRAY_BUFFER, new Float32Array(v), gl.STATIC_DRAW);
    return { buf: buf, n: v.length / 3 };
  }
  var grey = gl.createTexture(); gl.bindTexture(gl.TEXTURE_2D, grey); gl.texImage2D(gl.TEXTURE_2D, 0, gl.RGBA, 1, 1, 0, gl.RGBA, gl.UNSIGNED_BYTE, new Uint8Array([200, 200, 200, 255]));
  function quad(tex, x, y, w, h, top, z, fade, reveal, alpha) {
    gl.bindTexture(gl.TEXTURE_2D, tex); gl.uniform4f(U.uRect, x, y, w, h); gl.uniform1f(U.uTop, top); gl.uniform1f(U.uZ, z);
    gl.uniform1f(U.uFade, fade); gl.uniform1f(U.uReveal, reveal); gl.uniform1f(U.uAlpha, alpha); gl.drawArrays(gl.TRIANGLE_STRIP, 0, 4);
  }

  // ---------- rasterising a dom subtree into tiles: text word by word at the dom's own positions ----------
  var TILE = 1024;
  function font(cs) { return cs.fontStyle + ' ' + cs.fontWeight + ' ' + cs.fontSize + ' ' + cs.fontFamily; }
  function paint(ctx, root, ox, oy, y0, y1) {
    var els = root.querySelectorAll('*'), i, el, cs, r, x, y;
    for (i = 0; i < els.length; i++) {
      el = els[i]; if (el.tagName === 'SCRIPT' || el.tagName === 'CANVAS') continue;
      r = el.getBoundingClientRect(); if (!r.width || !r.height) continue;
      x = r.left - ox; y = r.top - oy; if (y > y1 || y + r.height < y0) continue;
      cs = getComputedStyle(el);
      if (cs.backgroundColor && cs.backgroundColor !== 'rgba(0, 0, 0, 0)' && cs.backgroundColor !== 'transparent') { ctx.fillStyle = cs.backgroundColor; ctx.fillRect(x, y, r.width, r.height); }
      var bw = [parseFloat(cs.borderTopWidth), parseFloat(cs.borderRightWidth), parseFloat(cs.borderBottomWidth), parseFloat(cs.borderLeftWidth)];
      if (bw[0]) { ctx.fillStyle = cs.borderTopColor; ctx.fillRect(x, y, r.width, bw[0]); }
      if (bw[2]) { ctx.fillStyle = cs.borderBottomColor; ctx.fillRect(x, y + r.height - bw[2], r.width, bw[2]); }
      if (bw[3]) { ctx.fillStyle = cs.borderLeftColor; ctx.fillRect(x, y, bw[3], r.height); }
      if (bw[1]) { ctx.fillStyle = cs.borderRightColor; ctx.fillRect(x + r.width - bw[1], y, bw[1], r.height); }
      if (el.tagName === 'IMG' && el.complete && el.naturalWidth) { try { ctx.drawImage(el, x, y, r.width, r.height); } catch (e) {} }
      if (el.tagName === 'A' && /underline/.test(cs.textDecorationLine || cs.textDecoration)) {
        var rg = document.createRange(); rg.selectNodeContents(el); var rects = rg.getClientRects(), k;
        ctx.fillStyle = cs.textDecorationColor || cs.color;
        for (k = 0; k < rects.length; k++) ctx.fillRect(rects[k].left - ox, rects[k].bottom - oy - 2, rects[k].width, 1);
      }
    }
    var walker = document.createTreeWalker(root, NodeFilter.SHOW_TEXT), node, range = document.createRange();
    while ((node = walker.nextNode())) {
      var s = node.nodeValue; if (!s || !s.trim()) continue;
      var pel = node.parentElement, pcs = getComputedStyle(pel); if (pcs.display === 'none') continue;
      ctx.font = font(pcs); ctx.fillStyle = pcs.color; ctx.textBaseline = 'alphabetic';
      var m = ctx.measureText('M'), asc = m.fontBoundingBoxAscent || parseFloat(pcs.fontSize) * 0.8;
      var re = /\S+/g, w, last = null;
      while ((w = re.exec(s))) {
        range.setStart(node, w.index); range.setEnd(node, w.index + w[0].length);
        var rr = range.getClientRects(); if (!rr.length) continue; var q = rr[0]; last = q;
        var ty = q.top - oy; if (ty > y1 || ty + q.height < y0) continue;
        ctx.fillText(w[0], q.left - ox, ty + asc);
      }
      var acs = getComputedStyle(pel, '::after');   // the flower after the name and the thanks: a pseudo-element, drawn by hand
      if (last && acs.content && acs.content.indexOf('✿') > -1 && node === pel.lastChild) { ctx.fillStyle = acs.color; ctx.fillText(' ✿', last.right - ox, last.top - oy + asc); }
    }
  }
  function rasterize(root) {
    var o = root.getBoundingClientRect(), w = Math.round(o.width), h = Math.round(Math.max(o.height, root.scrollHeight)), tiles = [], y;
    for (y = 0; y < h; y += TILE) {
      var th = Math.min(TILE, h - y), c = document.createElement('canvas');
      c.width = Math.round(w * DPR); c.height = Math.round(th * DPR);
      var ctx = c.getContext('2d'); ctx.scale(DPR, DPR); ctx.translate(0, -y);
      ctx.fillStyle = '#fff'; ctx.fillRect(0, y, w, th);
      paint(ctx, root, o.left, o.top, y, y + th);
      var tex = gl.createTexture(); gl.bindTexture(gl.TEXTURE_2D, tex);
      gl.texImage2D(gl.TEXTURE_2D, 0, gl.RGBA, gl.RGBA, gl.UNSIGNED_BYTE, c);
      gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_MIN_FILTER, gl.LINEAR); gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_MAG_FILTER, gl.LINEAR);
      gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_WRAP_S, gl.CLAMP_TO_EDGE); gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_WRAP_T, gl.CLAMP_TO_EDGE);
      tiles.push({ y: y, h: th, tex: tex });
    }
    return { w: w, h: h, tiles: tiles };
  }

  // ---------- the sheets: the home page on the ground, a project sheet that lifts off it ----------
  var page = document.querySelector('.page'), sheets = {}, home = null, vw, vh, camZ, D;
  function measure() { vw = innerWidth; vh = innerHeight; camZ = vh * 2.2; D = camZ * 0.5; BACK = camZ * 0.35; canvas.width = Math.round(vw * DPR); canvas.height = Math.round(vh * DPR); gl.viewport(0, 0, canvas.width, canvas.height); }
  function build() {
    measure(); html.classList.add('measuring');   // the sheets are laid out (invisibly) while they are drawn and measured
    try { buildInner(); } finally { html.classList.remove('measuring'); }
  }
  function buildInner() {
    Object.keys(sheets).forEach(function (k) { sheets[k].tiles.forEach(function (t) { gl.deleteTexture(t.tex); }); });
    if (home) home.tiles.forEach(function (t) { gl.deleteTexture(t.tex); });
    home = rasterize(page); home.top = 0; home.z = 0; home.scroller = window; home.reveal = 1;
    home.bones = bones(page, 'header, .strip figure, .strip img, .strip figcaption, .grid, .grid > *');
    var po = page.getBoundingClientRect(); home.cols = Array.prototype.map.call(page.querySelectorAll('.strip img'), function (i) { var r = i.getBoundingClientRect(); return [r.left - po.left, r.right - po.left]; });
    P.forEach(function (p) {
      var el = document.getElementById(p.id), inner = el.querySelector('.sheet'), sh = rasterize(inner);
      sh.z = 0; sh.top = 0; sh.scroller = el; sh.reveal = 0; sh.bones = bones(inner, 'header, .pics img, .row'); sheets[p.id] = sh;
    });
  }

  // ---------- camera ----------
  function m4() { return new Float32Array([1,0,0,0, 0,1,0,0, 0,0,1,0, 0,0,0,1]); }
  function mul(a, b) { var o = new Float32Array(16), i, j, k; for (i = 0; i < 4; i++) for (j = 0; j < 4; j++) { var t = 0; for (k = 0; k < 4; k++) t += a[k * 4 + j] * b[i * 4 + k]; o[i * 4 + j] = t; } return o; }
  function perspective(fovy, aspect, n, f) { var t = 1 / Math.tan(fovy / 2), o = new Float32Array(16); o[0] = t / aspect; o[5] = t; o[10] = (f + n) / (n - f); o[11] = -1; o[14] = 2 * f * n / (n - f); return o; }
  function translate(x, y, z) { var o = m4(); o[12] = x; o[13] = y; o[14] = z; return o; }
  function rotateX(a) { var o = m4(), c = Math.cos(a), s = Math.sin(a); o[5] = c; o[6] = s; o[9] = -s; o[10] = c; return o; }
  var cam = { x: 0, y: 0, z: 0, pitch: 0 }, fade = 0;
  function scrollOf(sh) { return sh.scroller === window ? (window.pageYOffset || 0) : sh.scroller.scrollTop; }
  function restCam(sh) { return { x: vw / 2, y: sh.top - (scrollOf(sh) + vh / 2), z: sh.z + camZ, pitch: 0 }; }
  function render() {
    gl.clear(gl.COLOR_BUFFER_BIT | gl.DEPTH_BUFFER_BIT);
    var proj = perspective(2 * Math.atan((vh / 2) / camZ), vw / vh, camZ * 0.05, camZ * 8);
    var vp = mul(proj, mul(rotateX(-cam.pitch), translate(-cam.x, -cam.y, -cam.z)));
    gl.uniformMatrix4fv(U.uVP, false, vp);
    if (home.reveal > 0) home.tiles.forEach(function (t) { quad(t.tex, 0, t.y, home.w, t.h, home.top, home.z, fade, home.reveal, 1); });
    var id = moving ? (target === 'home' ? cur : target) : cur, sh = id !== 'home' && sheets[id];
    if (sh && sh.reveal > 0) sh.tiles.forEach(function (t) { quad(t.tex, 0, t.y, sh.w, t.h, sh.top, sh.z, 0, 1, sh.reveal); });
    if (skel > 0) {   // the bones: the home grid on the ground, the sheet's frames above, the partition walls between
      gl.disable(gl.DEPTH_TEST);
      lines(home.bones.buf, home.bones.n, home.top, 0, skel, vp);
      if (sh) {
        lines(sh.bones.buf, sh.bones.n, sh.top, sh.z, skel, vp);
        var v = [], xs = [0, sh.w], k; home.cols.forEach(function (c) { xs.push(c[0], c[1]); });
        for (k = 0; k < xs.length; k++) { v.push(xs[k], 0, 0, xs[k], 0, sh.z, xs[k], sh.h, 0, xs[k], sh.h, sh.z); }
        v.push(0, 0, 0, sh.w, 0, 0, 0, sh.h, 0, sh.w, sh.h, 0);   // the sheet's footprint on the ground
        gl.bindBuffer(gl.ARRAY_BUFFER, dynBuf); gl.bufferData(gl.ARRAY_BUFFER, new Float32Array(v), gl.DYNAMIC_DRAW);
        lines(dynBuf, v.length / 3, sh.top, 0, skel, vp);
      }
      gl.enable(gl.DEPTH_TEST);
    }
  }

  // ---------- state: home, or one project; the lift between them ----------
  var cur = 'home', target = null, moving = false, phase = '', t0 = 0, camA = null, camB = null, DUR = 1300, DISSOLVE = 320, REVEAL = 420, PITCH = 0.14, FADE = 0.55, BACK = 0, raf = 0, skel = 0;
  function eio(t) { return t < .5 ? 4 * t * t * t : 1 - Math.pow(-2 * t + 2, 3) / 2; }
  function eo(t) { return 1 - Math.pow(1 - t, 3); }
  function pose(t) {   // t: 0 on the ground, 1 arrived; sets the sheet, the fade and the camera for the lift
    // the camera leads and the sheet follows, so the sheet never comes closer than its resting distance;
    // mid-flight the camera pulls back, so the home falls away and the sheet hangs above it in space,
    // then pushes in to meet the sheet 1:1
    var sh = sheets[target === 'home' ? cur : target], up = target !== 'home', e = eio(t);
    sh.z = D * Math.pow(e, 1.6);
    fade = FADE * e;
    cam = { x: camA.x + (camB.x - camA.x) * e, y: camA.y + (camB.y - camA.y) * e, z: camA.z + (camB.z - camA.z) * e + BACK * Math.sin(Math.PI * e), pitch: (up ? 1 : -1) * PITCH * Math.sin(Math.PI * e) };
  }
  function frame(now) {
    raf = 0;
    if (moving) {
      var sh = sheets[target === 'home' ? cur : target], up = target !== 'home';
      if (phase === 'dissolve') {   // the content goes, the bones come
        var d = Math.min(1, (now - t0) / DISSOLVE); skel = eo(d); if (up) home.reveal = 1 - d; else sh.reveal = 1 - d;
        pose(up ? 0 : 1); render(); if (d < 1) { raf = requestAnimationFrame(frame); return; }
        phase = 'lift'; t0 = now; }
      if (phase === 'lift') { var t = Math.min(1, (now - t0) / DUR); pose(up ? t : 1 - t); render();
        if (t < 1) { raf = requestAnimationFrame(frame); return; }
        phase = 'reveal'; t0 = now; }
      if (phase === 'reveal') {   // the bones go, the content renders where we arrived
        var r = Math.min(1, (now - t0) / REVEAL), er = eo(r); skel = 1 - er; if (up) { sh.reveal = er; home.reveal = er; } else home.reveal = er;
        render(); if (r < 1) { raf = requestAnimationFrame(frame); return; }
        moving = false; arrive(); return; }
    } else { cam = restCam(cur === 'home' ? home : sheets[cur]); render(); }
  }
  function tick() { if (home && !raf) raf = requestAnimationFrame(frame); }
  function arrive() {
    html.classList.remove('moving');
    skel = 0; home.reveal = 1;
    if (target === 'home') { html.classList.remove('away'); fade = 0; P.forEach(function (p) { document.getElementById(p.id).classList.remove('open'); sheets[p.id].reveal = 0; sheets[p.id].z = 0; }); }
    else { html.classList.add('away'); fade = FADE; var sh = sheets[target]; sh.z = D; sh.reveal = 1; P.forEach(function (p) { document.getElementById(p.id).classList.toggle('open', p.id === target); }); }
    cur = target; target = null; phase = ''; cam = restCam(cur === 'home' ? home : sheets[cur]); render();
  }
  function go(id, instant) {
    if (moving || id === cur) return;
    if (id !== 'home') {   // the sheet appears over the viewport as it is now, then lifts
      var sh = sheets[id]; if (!sh) return; document.getElementById(id).scrollTop = 0;
      sh.top = -(window.pageYOffset || 0); sh.reveal = 0; sh.z = 0;
      camA = restCam(home); camB = { x: vw / 2, y: sh.top - vh / 2, z: D + camZ, pitch: 0 };
    } else { var cs = sheets[cur]; camA = restCam(home); camB = restCam(cs); }
    target = id;
    if (instant) { moving = false; arrive(); return; }
    html.classList.add('moving'); moving = true; phase = 'dissolve'; t0 = performance.now(); tick();
  }
  // links: #id lifts a sheet; # (the name, the ×) or the dimmed page behind flies home; the url carries the sheet
  document.addEventListener('click', function (e) {
    var a = e.target.closest && e.target.closest('a[href^="#"]');
    if (!a) { var pc = e.target.closest && e.target.closest('.p'); if (pc && pc.classList.contains('open') && !e.target.closest('.sheet')) { e.preventDefault(); if (!moving) { push(location.pathname + location.search); go('home'); } } return; }
    var id = a.getAttribute('href').slice(1); if (id && !sheets[id]) return;
    e.preventDefault(); e.stopPropagation(); if (moving) return;
    push(id ? '#' + id : location.pathname + location.search); go(id || 'home');
  });
  addEventListener('popstate', function () { var id = location.hash.slice(1); go(sheets[id] ? id : 'home'); });
  addEventListener('scroll', tick, { passive: true }); P.forEach(function (p) { document.getElementById(p.id).addEventListener('scroll', tick, { passive: true }); });
  var rt; addEventListener('resize', function () { clearTimeout(rt); rt = setTimeout(function () { var was = cur; build(); if (was !== 'home') { var sh = sheets[was]; sh.z = D; sh.reveal = 1; sh.top = -(window.pageYOffset || 0); } cam = restCam(cur === 'home' ? home : sheets[cur]); render(); }, 200); });

  var imgs = Array.prototype.slice.call(document.images), ready = imgs.map(function (i) { return i.complete ? Promise.resolve() : new Promise(function (r) { i.onload = i.onerror = r; }); });
  var buildMs = 0;
  Promise.all(ready).then(function () {
    var t = performance.now();
    try { build(); } catch (err) { home = null; canvas.remove(); return; }   // e.g. pictures the canvas may not read: the plain page stays
    buildMs = Math.round(performance.now() - t);
    var id = location.hash.slice(1); if (sheets[id]) { sheets[id].top = 0; go(id, true); } else { cam = restCam(home); render(); }
    html.classList.add('gl');
  });
  function push(url) { try { history.pushState(null, '', url); } catch (e) {} }
  // for tests: fly, or hold one moment of the lift
  window.__kgl = { go: go, state: function () { var s = cur !== 'home' && sheets[cur]; return { cur: cur, moving: moving, phase: phase, cam: cam, fade: fade, skel: skel, homeReveal: home && home.reveal, buildMs: buildMs, sheet: s && { z: s.z, top: s.top, reveal: s.reveal, w: s.w, h: s.h, tiles: s.tiles.length } }; },
    hold: function (id, t) { var sh = sheets[id]; document.getElementById(id).scrollTop = 0; sh.top = -(window.pageYOffset || 0); target = id; camA = restCam(home); camB = { x: vw / 2, y: sh.top - vh / 2, z: D + camZ, pitch: 0 }; moving = true; phase = 'lift';
      if (t >= 1) { pose(1); skel = 0; sh.reveal = 1; home.reveal = 1; } else { pose(Math.max(0, t)); skel = 1; home.reveal = 0; sh.reveal = 0; }
      render(); moving = false; target = null; phase = ''; skel = 0; home.reveal = 1; sh.reveal = 0; sh.z = 0; fade = 0; } };
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
                 f'    <header><h1><a href="#">kes inkersole</a></h1><p><a class="x" href="#" aria-label="close">×</a></p></header>\n'
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
h = h.replace('</main>\n\n</body>', '</main>\n</div>\n<script>' + JS.replace('__P__', str([{'id': p['id']} for p in P]).replace("'", '"')) + '</script>\n</body>', 1)
# the sheet header line sits in the same grid as the page header
h = h.replace('header { display: grid; grid-template-columns: minmax(0, 1fr); padding: 12px 0 11px; }',
              'header { display: grid; grid-template-columns: minmax(0, 1fr); padding: 12px 0 11px; }\n.sheet > header p { text-align: right; }', 1)
h = h.replace('</style>\n</head>', '</style>\n<style>' + CSS + '</style>\n</head>', 1)
os.makedirs(f'{S}/gl/out/01', exist_ok=True)
open(f'{S}/gl/out/01/index.html', 'w', encoding='utf-8').write(h)
print('written', len(h))
