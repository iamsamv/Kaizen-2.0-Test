#!/usr/bin/env python3
"""Kaizen · costruisce index.html (l'app in un solo file) dalle schermate del canvas.

Uso:
    python3 tools/build.py CARTELLA_CANVAS [material-symbols-outlined.woff2]

CARTELLA_CANVAS contiene project/*.dc.html, project/kaizen-dati.js e
artifact-type/dc-runtime.js (scaricati dal canvas di Claude Design).
DM Sans e Jost vengono ripresi dall'index.html attuale; Manrope (il carattere dell'app) da tools/fonts.

Icone: se passi il file completo di Material Symbols Outlined (pacchetto npm
"material-symbols", versione 0.47.5), il file tiene solo le icone usate nelle
schermate (circa 240 KB). Serve fontTools 4.x e brotli:
    pip install fonttools brotli
Senza il secondo argomento resta il carattere delle icone già incluso: va bene
solo se non hai aggiunto icone nuove.

Per il telefono il file:
- adatta l'app allo schermo: tiene conto della tacca e della barra di stato
  (safe area), riempie la larghezza e usa l'altezza disponibile;
- in orizzontale mostra "Gira il telefono" (su iPhone le web app non possono bloccare la rotazione).
"""
import json
import os
import re
import sys

QUI = os.path.dirname(os.path.abspath(__file__))
INDEX = os.path.join(QUI, '..', 'index.html')

SCHERMATE = ['Sfondo', 'Apertura', 'Benvenuto', 'Oggi', 'AbitudiniV2', 'Progressi',
             'Scopri', 'Profilo', 'Dettaglio', 'NuovaAbitudine']

HEAD = '''<!doctype html>
<html lang="it">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, minimum-scale=1, maximum-scale=1, user-scalable=no, viewport-fit=cover">
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="mobile-web-app-capable" content="yes">
<script>
/* Tema chiaro o scuro (scelto nel Profilo): colore della barra di stato e del fondo della pagina.
   Su iPhone lo stile della barra di stato vale dalla prossima apertura dell'app. */
(function(){
  var chiaro = false;
  try { var d = JSON.parse(localStorage.getItem('kaizen-v3') || '{}'); chiaro = !!(d.profile && d.profile.tema === 'chiaro'); } catch (e) {}
  document.write('<meta name="theme-color" content="' + (chiaro ? '#DCDCD9' : '#000000') + '">' +
    '<meta name="apple-mobile-web-app-status-bar-style" content="' + (chiaro ? 'default' : 'black') + '">');
  if (chiaro) document.documentElement.className += ' kz-pag-chiara';
})();
</script>
<meta name="apple-mobile-web-app-title" content="Kaizen">
<link rel="manifest" href="manifest.webmanifest">
<title>Kaizen</title>
<!-- Kaizen, prototipo in un solo file. Costruito con tools/build.py dalle schermate del canvas. I dati restano nel browser (localStorage). -->
<style>
html,body{margin:0;height:100%;background:#0A0A0B;overflow:hidden;overflow:clip;overscroll-behavior:none}
html.kz-pag-chiara,html.kz-pag-chiara body{background:#DCDCD9}
/* La pagina è ferma e grande quanto lo schermo: niente pezzi di altre schermate che spuntano, niente pagina che scorre o si rimpicciolisce */
/* body "absolute" e non "fixed": su iPhone, aperta dalla Home, gli elementi fixed vengono tagliati prima del fondo dello schermo */
body{position:absolute;left:0;top:0;width:100%;height:var(--kz-schermo,100%);touch-action:pan-x pan-y}
/* Lo sfondo dell'app continua dietro la barra di stato (orologio, batteria): niente fascia nera in alto */
.kz-sf-par .kz-sf{height:calc(var(--kz-h,844px) + var(--kz-su,0px)) !important}
/* anche Dettaglio e Profilo (entrano da destra) hanno il loro sfondo dietro la barra di stato */
.kz-push{overflow:visible !important}
.kz-push > div[aria-hidden="true"]:first-child{top:calc(-1 * var(--kz-su,0px)) !important;height:calc(var(--kz-h,844px) + var(--kz-su,0px)) !important}
.kz-push .kz-sf{height:calc(var(--kz-h,844px) + var(--kz-su,0px)) !important}
/* L'app è larga 390 px e alta quanto lo spazio libero dello schermo (--kz-h); poi viene ingrandita per riempire la larghezza */
#dc-root{position:absolute;left:0;top:0;width:390px;height:var(--kz-h,844px);transform-origin:0 0;transform:translate(var(--kz-x,0px),var(--kz-y,0px)) scale(var(--kz-scala,1))}
#kz-alto{position:fixed;left:0;top:0;bottom:0;width:1px;visibility:hidden;pointer-events:none}
#kz-misura{position:fixed;left:0;top:0;visibility:hidden;pointer-events:none;padding:env(safe-area-inset-top) env(safe-area-inset-right) env(safe-area-inset-bottom) env(safe-area-inset-left)}
/* In orizzontale: un avviso al posto dell'app */
#kz-gira{display:none;position:fixed;inset:0;z-index:999;background:#0A0A0B;color:#F5F5F7;font-family:"DM Sans",system-ui,sans-serif;flex-direction:column;align-items:center;justify-content:center;gap:14px;text-align:center;padding:24px;box-sizing:border-box}
#kz-gira svg{width:56px;height:56px}
#kz-gira b{font-family:Jost,"DM Sans",sans-serif;font-weight:500;font-size:22px}
#kz-gira span{font-size:14px;color:#9A9AA0}
@media (orientation: landscape) and (max-height: 600px){#kz-gira{display:flex}#dc-root{visibility:hidden}}
'''

FINE = '''<div id="kz-misura" aria-hidden="true"></div>
<div id="kz-alto" aria-hidden="true"></div>
<div id="kz-gira" role="alert">
<svg viewBox="0 0 24 24" fill="none" stroke="#EDEDED" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><rect x="7" y="2.5" width="10" height="19" rx="2.5"></rect><path d="M11 18.5h2"></path></svg>
<b>Gira il telefono</b>
<span>Kaizen funziona in verticale.</span>
</div>
<script>
(function(){
  var misura = document.getElementById('kz-misura');
  function bordi(){
    var cs = misura ? getComputedStyle(misura) : null;
    function n(v){ v = parseFloat(v); return isFinite(v) ? v : 0; }
    return cs ? { t: n(cs.paddingTop), b: n(cs.paddingBottom) } : { t: 0, b: 0 };
  }
  var alto = document.getElementById('kz-alto');
  function altezza(){
    /* l'altezza vera della finestra. Con la barra di stato opaca iPhone la comunica giusta.
       Non si usa l'altezza dello schermo: comprende la barra di stato, che non fa parte della finestra
       (con la barra "trasparente" iOS 26 accorcia la finestra in fondo: bug WebKit 301108) */
    var h = window.innerHeight || 0;
    try { h = Math.max(h, alto ? alto.getBoundingClientRect().height : 0); } catch (e) {}
    try { h = Math.max(h, document.documentElement.clientHeight || 0); } catch (e) {}
    return h || 844;
  }
  var ultima = { w: 0, h: 0 };
  function scrivendo(){
    var a = document.activeElement;
    return !!a && (a.tagName === 'INPUT' || a.tagName === 'TEXTAREA' || a.isContentEditable);
  }
  function adatta(){
    /* con la tastiera aperta lo schermo "si accorcia": l'app non cambia misura, così non salta */
    var w0 = window.innerWidth || 390, h0 = altezza();
    if (scrivendo() && w0 === ultima.w && h0 < ultima.h) return;
    ultima = { w: w0, h: h0 };
    var w = w0, h = h0;
    var sa = bordi();
    /* i contenuti partono sotto la barra di stato; lo sfondo invece arriva fino in cima e fino in fondo */
    var su = sa.t;
    var libera = Math.max(320, h - su);
    var s = w / 390, alta = libera / s;
    /* schermi bassi o tablet: l'app resta almeno alta 640 e si rimpicciolisce per starci */
    if (alta < 640) { alta = 640; s = libera / 640; }
    if (alta > 1100) { alta = 1100; s = libera / 1100; }
    var x = (w - 390 * s) / 2, y = su + (libera - alta * s) / 2;
    var r = document.documentElement.style;
    r.setProperty('--kz-scala', String(s));
    r.setProperty('--kz-h', alta.toFixed(1) + 'px');
    r.setProperty('--kz-x', x.toFixed(1) + 'px');
    r.setProperty('--kz-y', y.toFixed(1) + 'px');
    r.setProperty('--kz-su', (y / s).toFixed(1) + 'px');
    r.setProperty('--kz-schermo', h.toFixed(1) + 'px');
  }
  adatta();
  /* tema: il fondo della pagina e il colore della barra (Android) seguono la scelta del Profilo */
  function tema(){
    try {
      var chiaro = (window.KaizenDati.get().profile || {}).tema === 'chiaro';
      document.documentElement.classList.toggle('kz-pag-chiara', chiaro);
      var m = document.querySelector('meta[name="theme-color"]');
      if (m) m.setAttribute('content', chiaro ? '#DCDCD9' : '#000000');
    } catch (e) {}
  }
  if (window.KaizenDati) { tema(); window.KaizenDati.subscribe(tema); }
  window.addEventListener('resize', adatta);
  window.addEventListener('orientationchange', function(){ setTimeout(adatta, 250); });
  window.addEventListener('load', adatta);
  [150, 600, 1500, 3000].forEach(function (t) { setTimeout(adatta, t); });
  /* la pagina non deve mai scorrere (solo le schermate dentro l'app): se iPhone la sposta, la rimettiamo a posto */
  window.addEventListener('scroll', function () {
    if (!scrivendo() && (window.scrollY || window.scrollX)) { try { window.scrollTo(0, 0); } catch (e) {} }
  }, { passive: true });
  /* chiusa la tastiera, tutto torna al suo posto */
  document.addEventListener('focusout', function () {
    setTimeout(function () { if (!scrivendo()) { try { window.scrollTo(0, 0); } catch (e) {} adatta(); } }, 80);
  });
  /* niente zoom con due dita su iPhone (l'app è già a misura di schermo) */
  document.addEventListener('gesturestart', function (e) { e.preventDefault(); });
  document.addEventListener('visibilitychange', function () { if (!document.hidden) setTimeout(adatta, 100); });
  /* Android (app installata): blocca in verticale dove il browser lo permette */
  try { if (screen.orientation && screen.orientation.lock) screen.orientation.lock('portrait').catch(function(){}); } catch (e) {}
})();
</script>
</body>
</html>
'''


def adatta_altezza(nome, html):
    """Le schermate sono disegnate a 844 px: qui seguono l'altezza vera dello schermo."""
    if nome == 'Sfondo':
        # il fumo resta alto 844 e parte dal basso (la sorgente, fuori dallo schermo, resta in fondo)
        vecchio = '<canvas ref="{{canvasRef}}" style="position: absolute; left: 0; top: 0; width: {{w}}; height: 844px">'
        assert vecchio in html, 'Sfondo: canvas non trovato'
        html = html.replace(vecchio, vecchio.replace('top: 0;', 'bottom: 0;').replace('height: 844px', 'height: 844PX'))
    html = html.replace('height: 844px', 'height: var(--kz-h, 844px)')
    return html.replace('height: 844PX', 'height: 844px')


def sfondo_fino_in_cima(html):
    """Nell'app principale lo sfondo animato sale anche dietro la barra di stato."""
    sost = [
        ('<div class="kz-tema {{temaCls}}" style="position: relative; overflow: hidden; width: 390px; height: var(--kz-h, 844px); box-sizing: border-box; background: #000000;',
         '<div class="kz-tema {{temaCls}}" style="position: relative; overflow: visible; width: 390px; height: var(--kz-h, 844px); box-sizing: border-box; background: #000000;'),
        ('style="position: absolute; left: 0; top: 0; width: 390px; height: var(--kz-h, 844px); overflow: hidden; border-radius: {{layerRadius}};',
         'style="position: absolute; left: 0; top: 0; width: 390px; height: var(--kz-h, 844px); overflow: visible; border-radius: {{layerRadius}};'),
        ('style="position: absolute; left: -40px; top: 0; width: 470px; height: var(--kz-h, 844px);',
         'style="position: absolute; left: -40px; top: calc(-1 * var(--kz-su, 0px)); width: 470px; height: calc(var(--kz-h, 844px) + var(--kz-su, 0px));'),
    ]
    for a, b in sost:
        assert html.count(a) == 1, 'App: ' + a[:60]
        html = html.replace(a, b)
    return html


def manrope():
    """Manrope (carattere dell'app), incluso nel file: @fontsource-variable/manrope 5.3.0, licenza OFL."""
    import base64
    blocchi = []
    for nome, rng in [
        ('manrope-latin-ext-wght-normal.woff2', 'U+0100-02BA,U+02BD-02C5,U+02C7-02CC,U+02CE-02D7,U+02DD-02FF,U+0304,U+0308,U+0329,U+1D00-1DBF,U+1E00-1E9F,U+1EF2-1EFF,U+2020,U+20A0-20AB,U+20AD-20C0,U+2113,U+2C60-2C7F,U+A720-A7FF'),
        ('manrope-latin-wght-normal.woff2', 'U+0000-00FF,U+0131,U+0152-0153,U+02BB-02BC,U+02C6,U+02DA,U+02DC,U+0304,U+0308,U+0329,U+2000-206F,U+20AC,U+2122,U+2191,U+2193,U+2212,U+2215,U+FEFF,U+FFFD'),
    ]:
        dati = base64.b64encode(open(os.path.join(QUI, 'fonts', nome), 'rb').read()).decode('ascii')
        blocchi.append("@font-face{font-family:'Manrope';font-style:normal;font-weight:200 800;font-display:swap;"
                       "src:url(data:font/woff2;base64,%s) format('woff2');unicode-range:%s}" % (dati, rng))
    return '\n'.join(blocchi)


def senza_link_font(html):
    return re.sub(r'<link href="https://fonts\.googleapis\.com[^"]*" rel="stylesheet">\n?', '', html)


def icone_usate(testo, font_completo):
    """Tiene solo le icone (legature) che compaiono nei file. Restituisce il woff2 in base64."""
    import base64
    import io
    from fontTools.ttLib import TTFont
    from fontTools import subset
    f = TTFont(font_completo)
    rev = {g: chr(c) for c, g in f.getBestCmap().items()}
    tavole = []
    for lk in f['GSUB'].table.LookupList.Lookup:
        for st in lk.SubTable:
            if st.LookupType == 7:
                st = st.ExtSubTable
            if hasattr(st, 'ligatures'):
                tavole.append(st)
    nomi = {}
    for st in tavole:
        for primo, ligs in st.ligatures.items():
            for L in ligs:
                try:
                    nomi[rev[primo] + ''.join(rev[c] for c in L.Component)] = L.LigGlyph
                except KeyError:
                    pass
    parole = set(re.findall(r'[a-z][a-z0-9_]{1,40}', testo))
    tieni = set(nomi[p] for p in parole if p in nomi)
    for st in tavole:
        for primo in list(st.ligatures):
            st.ligatures[primo] = [L for L in st.ligatures[primo] if L.LigGlyph in tieni]
            if not st.ligatures[primo]:
                del st.ligatures[primo]
    opt = subset.Options()
    opt.flavor = 'woff2'
    opt.layout_features = ['*']
    opt.name_IDs = ['*']
    sub = subset.Subsetter(opt)
    sub.populate(text='abcdefghijklmnopqrstuvwxyz0123456789_', glyphs=sorted(tieni))
    sub.subset(f)
    f.flavor = 'woff2'
    buf = io.BytesIO()
    f.save(buf)
    print('icone tenute: %d (%d KB)' % (len(tieni), len(buf.getvalue()) // 1024))
    return base64.b64encode(buf.getvalue()).decode('ascii')


def js_string(text):
    s = json.dumps(text, ensure_ascii=False)
    return s.replace('<', '\\u003c').replace('\u2028', '\\u2028').replace('\u2029', '\\u2029')


def main():
    if len(sys.argv) not in (2, 3):
        print(__doc__)
        sys.exit(1)
    src = sys.argv[1]
    vecchio = open(INDEX, encoding='utf-8').read()
    caratteri = [c for c in re.findall(r'@font-face\{[^}]*\}', vecchio[:vecchio.find('</style>')]) if 'Manrope' not in c]
    assert len(caratteri) == 8, 'caratteri non trovati in index.html'

    def leggi(p):
        return open(os.path.join(src, p), encoding='utf-8').read()

    risorse = []
    for n in SCHERMATE:
        html = adatta_altezza(n, senza_link_font(leggi('project/%s.dc.html' % n)))
        risorse.append('"./%s.dc.html": %s' % (n, js_string(html)))
    runtime = leggi('artifact-type/dc-runtime.js')
    # dentro <script> la sequenza "<!--" confonde il browser: nel runtime sta solo in stringhe, quindi la scriviamo come <\x21--
    assert runtime.count('<!--') == runtime.count('"(<!---?>|<!--') * 2
    runtime = runtime.replace('<!--', '<\\x21--')
    dati = leggi('project/kaizen-dati.js')
    assert '<!--' not in dati and '</script' not in dati.lower()
    app = sfondo_fino_in_cima(adatta_altezza('App', senza_link_font(leggi('project/App.dc.html'))))
    corpo = app[app.find('<x-dc>'):app.rfind('</script>') + len('</script>')]

    if len(sys.argv) == 3:
        tutto = ''.join(leggi('project/%s.dc.html' % n) for n in SCHERMATE + ['App']) + dati
        nuovo = icone_usate(tutto, sys.argv[2])
        for i, c in enumerate(caratteri):
            if 'Material Symbols' in c:
                caratteri[i] = re.sub(r'base64,[A-Za-z0-9+/=]+', 'base64,' + nuovo, c)

    out = [HEAD, '\n'.join(caratteri + [manrope()]), '\n</style>\n',
           '<script>\n/* Le schermate dell\'app, incluse nel file (niente richieste in rete) */\n'
           'window.__resources = {};\nwindow.__resourceBlobs = (function(){\n  var src = {\n',
           ',\n'.join(risorse),
           '\n  };\n  var out = {};\n  for (var k in src) out[k] = new Blob([src[k]], { type: \'text/html\' });\n  return out;\n})();\n</script>\n',
           '<script>\n', runtime, '\n</script>\n',
           '<script>\n', dati, '\n</script>\n',
           '</head>\n<body>\n', corpo, '\n', FINE]
    testo = ''.join(out)
    open(INDEX, 'w', encoding='utf-8').write(testo)
    print('index.html scritto: %d KB' % (len(testo.encode('utf-8')) // 1024))


if __name__ == '__main__':
    main()
