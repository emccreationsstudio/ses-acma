# iPad ekrana sığdırma: CSS + dil/tema düğmesi. Kullanım: python3 apply-ipad.py <html dosyası>
import sys, os, re
d=os.path.dirname(os.path.abspath(__file__)); f=sys.argv[1]; s=open(f).read()
css=open(os.path.join(d,'ipad-fit.css')).read()
block='/*IPAD-START*/\n'+css+'/*IPAD-END*/\n'
if '/*IPAD-START*/' in s: s=re.sub(r'/\*IPAD-START\*/.*?/\*IPAD-END\*/\n',lambda _:block,s,flags=re.S)
else: i=s.index('</style>'); s=s[:i]+block+s[i:]
btn='<button type="button" class="icon-btn lang-btn" id="langBtn" aria-controls="langPanel" aria-expanded="false" aria-label="Dil / Tema"><svg viewBox="0 0 24 24" aria-hidden="true" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="3.2"/><path d="M19.4 15a1.7 1.7 0 0 0 .3 1.8l.1.1a2 2 0 1 1-2.8 2.8l-.1-.1a1.7 1.7 0 0 0-1.8-.3 1.7 1.7 0 0 0-1 1.5V21a2 2 0 1 1-4 0v-.1a1.7 1.7 0 0 0-1.1-1.5 1.7 1.7 0 0 0-1.8.3l-.1.1a2 2 0 1 1-2.8-2.8l.1-.1a1.7 1.7 0 0 0 .3-1.8 1.7 1.7 0 0 0-1.5-1H3a2 2 0 1 1 0-4h.1a1.7 1.7 0 0 0 1.5-1.1 1.7 1.7 0 0 0-.3-1.8l-.1-.1a2 2 0 1 1 2.8-2.8l.1.1a1.7 1.7 0 0 0 1.8.3H9a1.7 1.7 0 0 0 1-1.5V3a2 2 0 1 1 4 0v.1a1.7 1.7 0 0 0 1 1.5 1.7 1.7 0 0 0 1.8-.3l.1-.1a2 2 0 1 1 2.8 2.8l-.1.1a1.7 1.7 0 0 0-.3 1.8V9a1.7 1.7 0 0 0 1.5 1H21a2 2 0 1 1 0 4h-.1a1.7 1.7 0 0 0-1.5 1z"/></svg></button>'
s=re.sub(r'<button type="button" class="[^"]*lang-btn" id="langBtn".*?</button>','',s,flags=re.S)
if True: s=s.replace('<div class="head-btns">','<div class="head-btns">'+btn,1)
js='''<script id="ipadLang">
(function(){var b=document.getElementById("langBtn"),p=document.getElementById("langPanel");if(!b||!p)return;
function set(o){if(o&&p.parentNode!==document.body)document.body.appendChild(p);p.classList.toggle("open",o);b.setAttribute("aria-expanded",String(o));}
b.addEventListener("click",function(e){e.stopPropagation();set(!p.classList.contains("open"));});
document.addEventListener("click",function(e){if(p.classList.contains("open")&&!(e.composedPath?e.composedPath():[e.target]).includes(p))set(false);});
document.addEventListener("keydown",function(e){if(e.key==="Escape")set(false);});})();
</script>'''
s=re.sub(r'<script id="ipadLang">.*?</script>','',s,flags=re.S)
i=s.rindex('</body>') if '</body>' in s else len(s); s=s[:i]+js+s[i:]
js2='<script id="roundDots">\n(function(){function fix(svg){var vb=svg.viewBox&&svg.viewBox.baseVal;if(!vb||!vb.width)return;var r=svg.getBoundingClientRect();if(!r.width||!r.height)return;var sx=r.width/vb.width,sy=r.height/vb.height,k=Math.sqrt(sx*sy);\nsvg.querySelectorAll("circle.cdot").forEach(function(c){var cx=+c.getAttribute("cx"),cy=+c.getAttribute("cy");c.setAttribute("transform","translate("+cx+" "+cy+") scale("+(k/sx)+" "+(k/sy)+") translate("+(-cx)+" "+(-cy)+")");});}\nvar ro=new ResizeObserver(function(es){es.forEach(function(e){fix(e.target);});});var seen=new WeakSet();\nfunction scan(){document.querySelectorAll("svg.chart").forEach(function(s){if(!seen.has(s)){seen.add(s);ro.observe(s);}fix(s);});}\nnew MutationObserver(function(){scan();}).observe(document.body,{childList:true,subtree:true});scan();})();\n</script>'
s=re.sub(r'<script id="roundDots">.*?</script>','',s,flags=re.S)
i=s.rindex('</body>') if '</body>' in s else len(s); s=s[:i]+js2+s[i:]
open(f,'w').write(s); print('ok')
