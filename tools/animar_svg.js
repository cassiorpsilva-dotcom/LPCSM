// Gera quadros PNG de animações (parado, andando, ataque, conjurando) girando cada <g> no seu data-pivot.
// Quadrúpedes (SVG com 'mandibula') usam parado / andando / ataque (bote com mordida).
// 'ataque' vira estocada se a arma for comprida (cajado, lança) e golpe de cima para baixo se for curta (kunai, adaga).
// Uso: node tools/animar_svg.js personagem_lado_separado.svg pasta_quadros [parado,andando,ataque]
// Depois: python3 tools/quadros_para_gif.py pasta_quadros previews/prefixo
const {chromium}=require('playwright');const fs=require('fs');
const SRC=process.argv[2]||'necromante_estilizado_lado_separado.svg';
const OUT=process.argv[3]||'previews/quadros';
const LISTA=(process.argv[4]||'parado,andando,ataque,conjurando').split(',');
const S=2; // escala de render (256 -> 512)
const sin=Math.sin, PI=Math.PI;
const ease=t=>t<0?0:t>1?1:t*t*(3-2*t);
function keys(tab,f){ // tab: [[frame,{...}],...]
  let i=0; while(i<tab.length-2&&f>=tab[i+1][0]) i++;
  const [f0,a]=tab[i],[f1,b]=tab[i+1]; const t=ease((f-f0)/(f1-f0||1)); const o={};
  for(const k of new Set([...Object.keys(a),...Object.keys(b)])) o[k]=(a[k]||0)+((b[k]||0)-(a[k]||0))*t; return o;}
const ANIMS={
 parado:{n:16,ms:90,pose:f=>{const t=2*PI*f/16;return{dy:1.2*sin(t),tl:1.2*sin(t),hd:-2*sin(t+0.6),
   bst:4*sin(t+0.4),abt:5*sin(t+0.9),mbt:6*sin(t+1.3),bsf:-2*sin(t),abf:2*sin(t),mbf:-1*sin(t),sk:0.6*sin(t),glow:1+0.12*sin(2*t)}}},
 andando:{n:12,ms:85,pose:f=>{const t=2*PI*f/12;
   const leg=(p)=>{const th=-22*sin(p);const sh=Math.max(0,30*sin(p+PI/2))*0.9+4;return{th,sh,pe:-(th+sh)+(sin(p)<0?-6*sin(p):0)}};
   const F=leg(t),B=leg(t+PI);
   return{dy:-1.8*Math.abs(sin(t)),tl:3,hd:1.5*sin(2*t),cft:F.th,cnf:F.sh,pef:F.pe,ctt:B.th,cnt:B.sh,pet:B.pe,
     bst:16*sin(t),abt:8*sin(t-0.5),mbt:6*sin(t-1),bsf:-4*sin(t),abf:3*sin(t),mbf:2*sin(t),sk:2*sin(t),glow:1+0.08*sin(2*t)}}},
 ataque_haste:{n:24,ms:55,pose:f=>keys([
   [0,{}],
   [6,{tl:-9,hd:-3,dy:1,bsf:48,abf:-38,mbf:66,bst:25,abt:10,mbt:6,cft:4,ctt:-4,glow:1.2}],
   [9,{tl:12,hd:5,dy:2.5,bsf:-8,abf:-18,mbf:100,bst:-34,abt:-20,mbt:-15,cft:-22,cnf:14,pef:8,ctt:16,cnt:10,pet:-26,sk:4,glow:1.9}],
   [14,{tl:12,hd:5,dy:2.5,bsf:-5,abf:-16,mbf:100,bst:-30,abt:-18,mbt:-12,cft:-22,cnf:14,pef:8,ctt:16,cnt:10,pet:-26,sk:4,glow:1.4}],
   [23,{}],[24,{}]],f)},
 ataque:{n:24,ms:55,pose:f=>keys([
   [0,{}],
   [6,{tl:-7,hd:-4,dy:1.5,bsf:-105,abf:-35,mbf:88,bst:28,abt:12,mbt:8,cft:4,ctt:-4,glow:1.2}],
   [9,{tl:11,hd:5,dy:2.5,bsf:-8,abf:-18,mbf:100,bst:-34,abt:-20,mbt:-15,cft:-22,cnf:14,pef:8,ctt:16,cnt:10,pet:-26,sk:4,glow:1.8}],
   [14,{tl:12,hd:5,dy:2.5,bsf:-4,abf:-16,mbf:104,bst:-30,abt:-18,mbt:-12,cft:-22,cnf:14,pef:8,ctt:16,cnt:10,pet:-26,sk:4,glow:1.4}],
   [23,{}],[24,{}]],f)},
 conjurando:{n:20,ms:70,pose:f=>keys([
   [0,{glow:1}],
   [4,{bsf:12,abf:12,mbf:-6,tl:-3,hd:-3,dy:1,glow:0.9,bst:6}],
   [8,{bsf:-42,abf:-12,mbf:80,tl:7,hd:4,dy:-1,glow:1.7,bst:-45,abt:-25,mbt:-20}],
   [14,{bsf:-40,abf:-14,mbf:84,tl:6,hd:3,dy:-1,glow:1.9,bst:-42,abt:-28,mbt:-25}],
   [19,{glow:1}],[20,{glow:1}]],f)}
};
// ---------- quadrúpedes (rig com 'mandibula', 'cauda' e perna_<par>_sup/inf + pata_<par>)
const PERNAS_Q=['tras_perto','tras_longe','diant_perto','diant_longe'];
function passoQ(t,amp){ // ciclo de caminhada lateral: tras_perto, diant_perto, tras_longe, diant_longe
  const fase={tras_perto:0,diant_perto:PI/2,tras_longe:PI,diant_longe:3*PI/2}, o={};
  for(const L of PERNAS_Q){const p=t+fase[L], lift=Math.max(0,Math.cos(p));
    if(L.startsWith('tras')){const s=-14*amp*sin(p), i=22*amp*lift; o[L+'_s']=s;o[L+'_i']=i;o[L+'_p']=-(s+i)+14*amp*lift;}
    else{const s=-12*amp*sin(p), i=8*amp*lift; o[L+'_s']=s;o[L+'_i']=i;o[L+'_p']=-(s+i)+45*amp*lift;}}
  return o;}
const pernasQ=(o,d)=>{const r={};for(const L of PERNAS_Q)for(const k of ['s','i','p'])if(o[k]!==undefined)r[L+'_'+k]=o[k]*(L.endsWith('longe')?(d||1):1);return r;};
const ANIMS_Q={
 parado:{n:16,ms:90,pose:f=>{const t=2*PI*f/16;return{dy:0.8*sin(t),tl:0.6*sin(t),hd:2*sin(t+0.5),jaw:6+3*sin(3*t),tail:7*sin(2*t),
   tras_perto_s:sin(t),tras_longe_s:sin(t)}}},
 andando:{n:16,ms:70,pose:f=>{const t=2*PI*f/16;return Object.assign(passoQ(t,1),{dy:1.2*sin(2*t),tl:sin(2*t),hd:2*sin(2*t+1),jaw:4+2*sin(2*t),tail:10*sin(t)})}},
 ataque:{n:22,ms:60,pose:f=>keys([
   [0,{jaw:4}],
   [6,Object.assign({dx:-6,dy:5,tl:4,hd:14,jaw:8,tail:-12},pernasQ({s:16,i:-12,p:-2}),{tras_perto_s:-6,tras_perto_i:16,tras_perto_p:-8,tras_longe_s:-6,tras_longe_i:16,tras_longe_p:-8})],
   [10,{dx:20,dy:-8,tl:-8,hd:-16,jaw:40,tail:18,diant_perto_s:-40,diant_perto_i:-14,diant_perto_p:30,diant_longe_s:-30,diant_longe_i:-10,diant_longe_p:30,
        tras_perto_s:28,tras_perto_i:-10,tras_perto_p:-10,tras_longe_s:24,tras_longe_i:-8,tras_longe_p:-10}],
   [13,{dx:22,dy:-1,tl:-2,hd:10,jaw:0,tail:10,diant_perto_s:-14,diant_perto_i:-4,diant_perto_p:14,diant_longe_s:-10,diant_longe_i:-4,diant_longe_p:10,
        tras_perto_s:10,tras_perto_p:-6,tras_longe_s:8,tras_longe_p:-6}],
   [16,{dx:22,dy:-1,tl:-2,hd:12,jaw:3,tail:8,diant_perto_s:-14,diant_perto_i:-4,diant_perto_p:14,diant_longe_s:-10,diant_longe_i:-4,diant_longe_p:10,
        tras_perto_s:10,tras_perto_p:-6,tras_longe_s:8,tras_longe_p:-6}],
   [21,{jaw:4}],[22,{jaw:4}]],f)}
};
(async()=>{
 const b=await chromium.launch();const p=await b.newPage({viewport:{width:345*S,height:256*S}});
 const svg=fs.readFileSync(SRC,'utf8').replace('width="256" height="256"',`width="${256*S}" height="${256*S}" style="overflow:visible"`);
 await p.setContent(`<body style="margin:0;background:#ebe7f0"><svg style="position:absolute;left:0;top:0" width="${256*S}" height="${256*S}" viewBox="0 0 256 256"><ellipse id="sombra" cx="132" cy="240" rx="42" ry="4.5" fill="#d3cddc"/></svg><div style="position:absolute;left:0;top:0">${svg}</div></body>`);
 const quad=await p.evaluate(()=>{const b=document.querySelector('div svg').getBBox(),e=document.getElementById('sombra');
   if(document.getElementById('mandibula')){e.setAttribute('cx',b.x+b.width/2);e.setAttribute('rx',b.width*0.42);return true;}return false;});
 if(quad){
  for(const [name,A] of Object.entries(ANIMS_Q)){
   if(!LISTA.includes(name)) continue;
   fs.mkdirSync(`${OUT}/${name}`,{recursive:true});
   for(let f=0;f<A.n;f++){
    await p.evaluate(P=>{
     const g=id=>document.getElementById(id), pv=id=>g(id).dataset.pivot.split(',').map(Number);
     const R=(a,id)=>a?`rotate(${a} ${pv(id).join(' ')})`:'';
     const v=k=>P[k]||0, set=(id,tr)=>g(id).setAttribute('transform',tr);
     const body=`translate(${v('dx')} ${v('dy')}) `+R(v('tl'),'tronco');
     set('tronco',body); set('cauda',body+' '+R(v('tail'),'cauda'));
     const head=body+' '+R(v('hd'),'cabeca'); set('cabeca',head); set('mandibula',head+' '+R(v('jaw'),'mandibula'));
     for(const L of ['tras_perto','tras_longe','diant_perto','diant_longe']){
       const c=[body,R(v(L+'_s'),`perna_${L}_sup`),R(v(L+'_i'),`perna_${L}_inf`),R(v(L+'_p'),`pata_${L}`)];
       set(`perna_${L}_sup`,c.slice(0,2).join(' '));set(`perna_${L}_inf`,c.slice(0,3).join(' '));set(`pata_${L}`,c.join(' '));}
    },A.pose(f));
    await p.screenshot({path:`${OUT}/${name}/${String(f).padStart(3,'0')}.png`});
   }
  }
  await b.close(); return;
 }
 for(let [name,A] of Object.entries(ANIMS)){
  if(!LISTA.includes(name)||name==='ataque_haste') continue;
  const haste=await p.evaluate(()=>document.getElementById('arma').getBBox().height>100);
  const temArmaTras=await p.evaluate(()=>!!document.getElementById('arma_tras'));
  if(name==='ataque'&&haste) A=ANIMS.ataque_haste;
  fs.mkdirSync(`${OUT}/${name}`,{recursive:true});
  for(let f=0;f<A.n;f++){
   const P=A.pose(f);
   if(temArmaTras){ // segundo cajado na mão de trás: braço mexe menos e o punho compensa para o cajado ficar de pé
     P.bst=(P.bst||0)*0.35; P.abt=(P.abt||0)*0.35; P.mbt=-(P.bst+P.abt)-(P.tl||0); }
   await p.evaluate(P=>{
    const g=id=>document.getElementById(id), pv=id=>g(id).dataset.pivot.split(',').map(Number);
    const R=(a,id)=>a?`rotate(${a} ${pv(id).join(' ')})`:'';
    const v=k=>P[k]||0;
    const body=`translate(0 ${v('dy')})`, torso=body+' '+R(v('tl'),'tronco');
    const set=(id,tr)=>g(id).setAttribute('transform',tr);
    set('quadril',body+' '+R(v('sk'),'quadril'));
    set('tronco',torso);
    set('cabeca',torso+' '+R(v('hd'),'cabeca'));
    const armF=[torso,R(v('bsf'),'braco_sup_frente'),R(v('abf'),'antebraco_frente'),R(v('mbf'),'mao_frente')];
    set('braco_sup_frente',armF.slice(0,2).join(' '));set('antebraco_frente',armF.slice(0,3).join(' '));set('mao_frente',armF.join(' '));set('arma',armF.join(' '));
    const armT=[torso,R(v('bst'),'braco_sup_tras'),R(v('abt'),'antebraco_tras'),R(v('mbt'),'mao_tras')];
    set('braco_sup_tras',armT.slice(0,2).join(' '));set('antebraco_tras',armT.slice(0,3).join(' '));set('mao_tras',armT.join(' '));
    if(g('arma_tras')) set('arma_tras',armT.join(' '));
    for(const [s,th,sh,pe] of [['frente','cft','cnf','pef'],['tras','ctt','cnt','pet']]){
      const L=[body,R(v(th),'coxa_'+s),R(v(sh),'canela_'+s),R(v(pe),'pe_'+s)];
      set('coxa_'+s,L.slice(0,2).join(' '));set('canela_'+s,L.slice(0,3).join(' '));set('pe_'+s,L.join(' '));}
    document.querySelectorAll('#arma circle').forEach(c=>{if(!c.dataset.r0)c.dataset.r0=c.getAttribute('r');
      const r0=+c.dataset.r0; if(r0>8) c.setAttribute('r',r0*(P.glow||1));});
   },P);
   await p.screenshot({path:`${OUT}/${name}/${String(f).padStart(3,'0')}.png`});
  }
 }
 await b.close();})();
