import base64, os, sys

APP = sys.argv[1]      # Prototyp.dc.html (phone app)
WEB = sys.argv[2]      # Web.dc.html (desktop web view)
FONTS = sys.argv[3]    # node_modules/@fontsource
OUT = sys.argv[4]      # output html

def parts(path):
    src = open(path, encoding="utf-8").read()
    markup = src.split("<x-dc>", 1)[1].split("</x-dc>", 1)[0].split("</helmet>", 1)[1]
    logic = src.split("data-dc-script", 1)[1].split(">", 1)[1].split("</script>", 1)[0]
    return markup, logic

app_markup, app_logic = parts(APP)
web_markup, web_logic = parts(WEB)
app_markup = app_markup.replace("width: 390px; height: 844px; position: relative;", "width: 390px; height: 100%; position: relative;", 1)
web_markup = web_markup.replace("height: 100vh; min-height: 640px;", "height: 100%; min-height: 0;", 1)

def b64(path):
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode()

faces = [
    ("Atkinson Hyperlegible", 400, "atkinson-hyperlegible/files/atkinson-hyperlegible-latin-400-normal.woff2"),
    ("Atkinson Hyperlegible", 700, "atkinson-hyperlegible/files/atkinson-hyperlegible-latin-700-normal.woff2"),
    ("Fraunces", 600, "fraunces/files/fraunces-latin-600-normal.woff2"),
    ("Fraunces", 700, "fraunces/files/fraunces-latin-700-normal.woff2"),
]
font_css = "\n".join(
    f"@font-face{{font-family:'{fam}';font-weight:{w};font-display:block;src:url(data:font/woff2;base64,{b64(os.path.join(FONTS, p))}) format('woff2');}}"
    for fam, w, p in faces
)

ENGINE = r"""
var SVG_NS = 'http://www.w3.org/2000/svg';
var WHOLE = /^\s*\{\{([^}]+)\}\}\s*$/;
function lookup(path, scope) {
  path = path.trim();
  if (path === 'true') return true;
  if (path === 'false') return false;
  if (/^-?\d+(\.\d+)?$/.test(path)) return Number(path);
  var parts = path.split('.');
  var v = scope[parts[0]];
  for (var i = 1; i < parts.length; i++) { if (v == null) return undefined; v = v[parts[i]]; }
  return v;
}
function interp(str, scope) {
  return str.replace(/\{\{([^}]+)\}\}/g, function (m, p) { var v = lookup(p, scope); return v == null ? '' : String(v); });
}
function renderNodes(nodes, scope, inSvg, out) {
  for (var i = 0; i < nodes.length; i++) renderNode(nodes[i], scope, inSvg, out);
  return out;
}
function renderNode(n, scope, inSvg, out) {
  if (n.nodeType === 3) { out.push(document.createTextNode(interp(n.nodeValue, scope))); return; }
  if (n.nodeType !== 1) return;
  var tag = n.localName;
  if (tag === 'sc-if') {
    var mi = WHOLE.exec(n.getAttribute('value') || '');
    if (mi && lookup(mi[1], scope)) renderNodes(n.childNodes, scope, inSvg, out);
    return;
  }
  if (tag === 'sc-for') {
    var ml = WHOLE.exec(n.getAttribute('list') || '');
    var list = (ml ? lookup(ml[1], scope) : null) || [];
    var as = n.getAttribute('as') || 'item';
    list.forEach(function (item, idx) {
      var sc = Object.create(scope); sc[as] = item; sc.$index = idx;
      renderNodes(n.childNodes, sc, inSvg, out);
    });
    return;
  }
  var svg = inSvg || tag === 'svg';
  var el = svg ? document.createElementNS(SVG_NS, tag) : document.createElement(tag);
  for (var a = 0; a < n.attributes.length; a++) {
    var attr = n.attributes[a];
    var name = attr.name;
    if (name.indexOf('hint-') === 0) continue;
    var m = WHOLE.exec(attr.value);
    if (name.indexOf('on') === 0) {
      var fn = m ? lookup(m[1], scope) : null;
      if (typeof fn === 'function') el.addEventListener(name.slice(2).toLowerCase(), (function (f) { return function (e) { f(e); }; })(fn));
      continue;
    }
    var val = m ? lookup(m[1], scope) : interp(attr.value, scope);
    if (val == null || val === false) { if (name.indexOf('aria-') === 0) val = 'false'; else continue; }
    el.setAttribute(name, String(val));
  }
  renderNodes(n.childNodes, scope, svg, []).forEach(function (c) { el.appendChild(c); });
  out.push(el);
}
var __pending = false;
function __schedule() { if (!__pending) { __pending = true; requestAnimationFrame(__render); } }
class DCLogic {
  constructor(props) { this.props = props || {}; this.state = {}; }
  setState(u) {
    var p = typeof u === 'function' ? u(this.state) : u;
    if (p) { this.state = Object.assign({}, this.state, p); __schedule(); }
  }
  forceUpdate() { __schedule(); }
}
"""

BOOT = r"""
var __device = document.getElementById('device');
var __web = document.getElementById('web');
var __tplApp = document.getElementById('tpl-app');
var __tplWeb = document.getElementById('tpl-web');
var __forceApp = /[?&]app\b/.test(location.search);
var __mode = null, __lastKey = {};
function __wide() { return window.innerWidth > 900; }
function __container() { return __mode === 'web' ? __web : __device; }
function __comp() { return __mode === 'web' ? __webComp : __appComp; }
function __screenKey() { var s = __comp().state; return __mode === 'web' ? [s.page, s.tab, s.detail, s.world].join('|') : [s.screen, s.step, s.world].join('|'); }
function __scrollEls() { return Array.prototype.filter.call(__container().querySelectorAll('div, main'), function (e) { return e.style.overflowY === 'auto'; }); }
function __render() {
  __pending = false;
  var box = __container();
  var tops = __scrollEls().map(function (e) { return e.scrollTop; });
  var key = __screenKey();
  var same = __lastKey[__mode] === key;
  var vals = __comp().renderVals();
  var nodes = renderNodes((__mode === 'web' ? __tplWeb : __tplApp).content.childNodes, vals, false, []);
  while (box.firstChild) box.removeChild(box.firstChild);
  nodes.forEach(function (n) { box.appendChild(n); });
  __lastKey[__mode] = key;
  if (same) __scrollEls().forEach(function (e, i) { if (tops[i] != null) e.scrollTop = tops[i]; });
  document.body.style.background = (document.body.className === 'desk') ? '' : vals.c.bg;
  document.getElementById('toWeb').style.display = (__mode === 'app' && __wide()) ? 'flex' : 'none';
}
function __layout() {
  var vw = window.innerWidth, vh = window.innerHeight, root = document.documentElement;
  __mode = (__wide() && !__forceApp) ? 'web' : 'app';
  if (__mode === 'web') {
    document.body.className = 'webmode';
  } else if (vw <= 600) {
    document.body.className = 'phone';
    var s = vw / 390;
    root.style.setProperty('--s', s);
    root.style.setProperty('--app-h', (vh / s) + 'px');
  } else {
    document.body.className = 'desk';
    root.style.setProperty('--s', Math.min(1, (vh - 40) / 844));
    root.style.setProperty('--app-h', '844px');
  }
  __schedule();
}
window.__toApp = function () { __forceApp = true; __layout(); };
document.getElementById('toWeb').addEventListener('click', function () { __forceApp = false; __layout(); });
window.addEventListener('resize', __layout);
var __q = {};
location.search.replace(/^\?/, '').split('&').forEach(function (kv) { if (!kv) return; var p = kv.split('='); __q[decodeURIComponent(p[0])] = p.length > 1 ? decodeURIComponent(p[1]) : true; });
var __props = { start: __q.screen, world: __q.world, pal: __q.pal, look: __q.look, premium: __q.premium, ds: __q.ds, level: __q.level };
var __appComp = new AppComponent(__props);
var __webComp = new WebComponent({ start: __q.web, world: __q.world, pal: __q.pal, look: __q.look, ds: __q.ds });
__layout();
__render();
try { window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', __schedule); } catch (e) {}
"""

html = f"""<!doctype html>
<html lang="de">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="mobile-web-app-capable" content="yes">
<title>Wein- &amp; Bier-App · Klick-Prototyp</title>
<style>
{font_css}
html, body {{ margin: 0; height: 100%; overflow: hidden; background: #E9E2DA; -webkit-text-size-adjust: 100%; }}
#stage {{ position: fixed; left: 0; right: 0; top: 0; bottom: 0; display: flex; align-items: center; justify-content: center; }}
#device {{ flex: none; width: 390px; height: var(--app-h, 844px); overflow: hidden; transform: scale(var(--s, 1)); -webkit-user-select: none; user-select: none; }}
#web {{ position: fixed; left: 0; right: 0; top: 0; bottom: 0; display: none; }}
.webmode #stage {{ display: none; }}
.webmode #web {{ display: block; }}
.desk #device {{ border-radius: 44px; box-shadow: 0 24px 64px rgba(0, 0, 0, 0.28); }}
.phone #stage {{ display: block; }}
.phone #device {{ position: absolute; left: 0; top: 0; transform-origin: 0 0; }}
#toWeb {{ position: fixed; right: 20px; top: 20px; display: none; align-items: center; gap: 8px; height: 44px; padding: 0 16px; border: 0; border-radius: 22px; background: #2B1519; color: #FFFFFF; font: 700 15px 'Atkinson Hyperlegible', sans-serif; cursor: pointer; box-shadow: 0 6px 20px rgba(0, 0, 0, 0.2); }}
button {{ -webkit-appearance: none; appearance: none; margin: 0; -webkit-tap-highlight-color: transparent; }}
</style>
</head>
<body>
<div id="stage"><div id="device"></div></div>
<div id="web"></div>
<button type="button" id="toWeb"><svg aria-hidden="true" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#FFFFFF" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="2" y="4" width="20" height="13" rx="2"></rect><path d="M8 21h8"></path><path d="M12 17v4"></path></svg>Zur Web-Ansicht</button>
<template id="tpl-app">{app_markup}</template>
<template id="tpl-web">{web_markup}</template>
<script>
{ENGINE}
var AppComponent = (function () {{
{app_logic}
return Component;
}})();
var WebComponent = (function () {{
{web_logic}
return Component;
}})();
{BOOT}
</script>
</body>
</html>
"""
open(OUT, "w", encoding="utf-8").write(html)
print("written", OUT, round(len(html) / 1024), "KB")
