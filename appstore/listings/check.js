const fs=require("fs"),path=require("path");
const L={name:30,subtitle:30,promo:170,playShort:80,keywords:100,whatsNew:4000,description:4000};
let bad=0;
for(const f of fs.readdirSync(__dirname).filter(f=>f.endsWith(".json"))){
  const j=JSON.parse(fs.readFileSync(path.join(__dirname,f),"utf8"));
  for(const k in L){ const n=[...(j[k]||"")].length; if(!n||n>L[k]){bad++;console.log(`✗ ${f} ${k} ${n}/${L[k]}`);} }
  if(/,\s/.test(j.keywords)){bad++;console.log(`✗ ${f} keywords space after comma`);}
  if(j.name!=="Ses Açma - Piano Warm Up"){bad++;console.log(`✗ ${f} name`);}
}
console.log(bad?`${bad} sorun`:"tüm metinler sınırlar içinde");process.exit(bad?1:0);
