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
function set(o){p.classList.toggle("open",o);b.setAttribute("aria-expanded",String(o));}
b.addEventListener("click",function(e){e.stopPropagation();set(!p.classList.contains("open"));});
document.addEventListener("click",function(e){if(p.classList.contains("open")&&!(e.composedPath?e.composedPath():[e.target]).includes(p))set(false);});
document.addEventListener("keydown",function(e){if(e.key==="Escape")set(false);});})();
</script>'''
if 'id="ipadLang"' not in s: i=s.rindex('</body>') if '</body>' in s else len(s); s=s[:i]+js+s[i:]
open(f,'w').write(s); print('ok')
