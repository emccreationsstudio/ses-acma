# Tasarım görsellerini (assets.json) ve tema CSS'ini src/index.html'e yazar.
import json, os, re
d=os.path.dirname(os.path.abspath(__file__)); src=os.path.join(d,'..','src','index.html')
a=json.load(open(os.path.join(d,'assets.json'))); tpl=open(os.path.join(d,'theme-img.tpl.css')).read()
m={'play':'play','demo':'demo','lang-on':'lang_on','lang-off':'lang_off','seg-on':'seg_on','minus':'minus','plus':'plus','on':'on','off':'off','check':'check','e-uclu':'emb_uclu','e-besli':'emb_besli','e-staccato':'emb_staccato','e-ring':'emb_ring','kbd':'kbd','kw':'kw','kb':'kb'}
br=json.load(open(os.path.join(d,'breath.json')))
bm={'anat-in':'anat_in','anat-out':'anat_out','br-ladder':'br_ladder','br-pulse':'br_pulse','br-holdHiss':'br_holdHiss','br-pant':'br_pant','br-calm':'br_calm','br-box':'br_box','br-hiss':'br_hiss','br-r478':'br_r478','br-lip':'br_lip'}
v0=lambda p:"\n".join(f"  --i-{k}: url({a[p+'_'+n]});" for k,n in m.items())
v=lambda p: v0(p)+'\n'+'\n'.join(f"  --i-{k}: url({br[p+'_'+n]});" for k,n in bm.items())
a2=json.load(open(os.path.join(d,'assets2.json')))
def v2(p):
    L=[]
    for k,val in a2.items():
        if not k.startswith(p+'_') or not isinstance(val,str): continue
        n=k[len(p)+1:]
        if n in ('kw','kb','kbd'): n='h'+n
        L.append(f"  --i-{n.replace('_','-')}: url({val});")
    sl=a2[p+'_kbd_slice']; sc=1
    L.append(f"  --kbd-slice: {round(sl[0]*sc)} {round(sl[1]*sc)} {round(sl[2]*sc)} {round(sl[3]*sc)};")
    L.append(f"  --i-leather: url({lt[p+'_leather']});"); L.append(f"  --i-page: url({lt[p+'_page']});")
    return '\n'.join(L)
lt=json.load(open(os.path.join(d,'leather.json')))
v1=v
v=lambda p: v1(p)+'\n'+v2(p)
css=tpl.replace('@@G@@',v('g')).replace('@@S@@',v('s')).replace('@@B@@',v('b'))
s=open(src).read()
block='/*IMG-START*/\n'+css+'/*IMG-END*/\n'
if '/*IMG-START*/' in s: s=re.sub(r'/\*IMG-START\*/.*?/\*IMG-END\*/\n',lambda _:block,s,flags=re.S)
else: i=s.index('</style>'); s=s[:i]+block+s[i:]
open(src,'w').write(s); print('ok',len(s))
