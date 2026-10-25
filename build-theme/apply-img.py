# Tasarım görsellerini (assets.json) ve tema CSS'ini src/index.html'e yazar.
import json, os, re
d=os.path.dirname(os.path.abspath(__file__)); src=os.path.join(d,'..','src','index.html')
a=json.load(open(os.path.join(d,'assets.json'))); tpl=open(os.path.join(d,'theme-img.tpl.css')).read()
m={'play':'play','demo':'demo','lang-on':'lang_on','lang-off':'lang_off','seg-on':'seg_on','minus':'minus','plus':'plus','on':'on','off':'off','check':'check','e-uclu':'emb_uclu','e-besli':'emb_besli','e-staccato':'emb_staccato','e-ring':'emb_ring','kbd':'kbd','kw':'kw','kb':'kb'}
br=json.load(open(os.path.join(d,'breath.json')))
bm={'anat-in':'anat_in','anat-out':'anat_out','br-ladder':'br_ladder','br-pulse':'br_pulse','br-holdHiss':'br_holdHiss','br-pant':'br_pant'}
v0=lambda p:"\n".join(f"  --i-{k}: url({a[p+'_'+n]});" for k,n in m.items())
v=lambda p: v0(p)+'\n'+'\n'.join(f"  --i-{k}: url({br[p+'_'+n]});" for k,n in bm.items())
css=tpl.replace('@@G@@',v('g')).replace('@@S@@',v('s')).replace('@@B@@',v('b'))
s=open(src).read()
block='/*IMG-START*/\n'+css+'/*IMG-END*/\n'
if '/*IMG-START*/' in s: s=re.sub(r'/\*IMG-START\*/.*?/\*IMG-END\*/\n',lambda _:block,s,flags=re.S)
else: i=s.index('</style>'); s=s[:i]+block+s[i:]
open(src,'w').write(s); print('ok',len(s))
