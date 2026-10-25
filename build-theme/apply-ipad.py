# iPad ekrana sığdırma: CSS + dil/tema düğmesi. Kullanım: python3 apply-ipad.py <html dosyası>
import sys, os, re
d=os.path.dirname(os.path.abspath(__file__)); f=sys.argv[1]; s=open(f).read()
css=open(os.path.join(d,'ipad-fit.css')).read()
block='/*IPAD-START*/\n'+css+'/*IPAD-END*/\n'
if '/*IPAD-START*/' in s: s=re.sub(r'/\*IPAD-START\*/.*?/\*IPAD-END\*/\n',lambda _:block,s,flags=re.S)
else: i=s.index('</style>'); s=s[:i]+block+s[i:]
btn='<button type="button" class="lang-btn" id="langBtn" aria-controls="langPanel" aria-expanded="false"><svg viewBox="0 0 24 24" aria-hidden="true" fill="none" stroke="currentColor" stroke-width="1.8"><circle cx="12" cy="12" r="9"/><path d="M3 12h18M12 3c2.8 3 2.8 15 0 18M12 3c-2.8 3-2.8 15 0 18"/></svg><span data-i18n="language"></span></button>'
if 'id="langBtn"' not in s: s=s.replace('<div class="head-btns">','<div class="head-btns">'+btn,1)
js='''<script id="ipadLang">
(function(){var b=document.getElementById("langBtn"),p=document.getElementById("langPanel");if(!b||!p)return;
function set(o){p.classList.toggle("open",o);b.setAttribute("aria-expanded",String(o));}
b.addEventListener("click",function(e){e.stopPropagation();set(!p.classList.contains("open"));});
document.addEventListener("click",function(e){if(p.classList.contains("open")&&!p.contains(e.target))set(false);});
document.addEventListener("keydown",function(e){if(e.key==="Escape")set(false);});})();
</script>'''
if 'id="ipadLang"' not in s: i=s.rindex('</body>') if '</body>' in s else len(s); s=s[:i]+js+s[i:]
open(f,'w').write(s); print('ok')
