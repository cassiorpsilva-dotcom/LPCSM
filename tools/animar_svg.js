// Gera quadros PNG de animações (parado, andando, conjurando) girando cada <g> no seu data-pivot.
// Uso: node tools/animar_svg.js personagem_lado_separado.svg pasta_quadros
// Depois: python3 tools/quadros_para_gif.py pasta_quadros previews/prefixo
const {chromium}=require('playwright');const fs=require('fs');
const SRC=process.argv[2]||'necromante_estilizado_lado_separado.svg';
const OUT=process.argv[3]||'previews/quadros';
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
 conjurando:{n:20,ms:70,pose:f=>keys([
   [0,{glow:1}],
   [4,{bsf:12,abf:12,mbf:-6,tl:-3,hd:-3,dy:1,glow:0.9,bst:6}],
   [8,{bsf:-42,abf:-12,mbf:80,tl:7,hd:4,dy:-1,glow:1.7,bst:-45,abt:-25,mbt:-20}],
   [14,{bsf:-40,abf:-14,mbf:84,tl:6,hd:3,dy:-1,glow:1.9,bst:-42,abt:-28,mbt:-25}],
   [19,{glow:1}],[20,{glow:1}]],f)}
};
(async()=>{
 const b=await chromium.launch();const p=await b.newPage({viewport:{width:300*S,height:256*S}});
 const svg=fs.readFileSync(SRC,'utf8').replace('width="256" height="256"',`width="${256*S}" height="${256*S}" style="overflow:visible"`);
 await p.setContent(`<body style="margin:0;background:#ebe7f0"><svg style="position:absolute;left:0;top:0" width="${256*S}" height="${256*S}" viewBox="0 0 256 256"><ellipse cx="132" cy="240" rx="42" ry="4.5" fill="#d3cddc"/></svg><div style="position:absolute;left:0;top:0">${svg}</div></body>`);
 for(const [name,A] of Object.entries(ANIMS)){
  fs.mkdirSync(`${OUT}/${name}`,{recursive:true});
  for(let f=0;f<A.n;f++){
   const P=A.pose(f);
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
    for(const [s,th,sh,pe] of [['frente','cft','cnf','pef'],['tras','ctt','cnt','pet']]){
      const L=[body,R(v(th),'coxa_'+s),R(v(sh),'canela_'+s),R(v(pe),'pe_'+s)];
      set('coxa_'+s,L.slice(0,2).join(' '));set('canela_'+s,L.slice(0,3).join(' '));set('pe_'+s,L.join(' '));}
    document.querySelectorAll('#arma circle').forEach(c=>{if(!c.dataset.r0)c.dataset.r0=c.getAttribute('r');
      const r0=+c.dataset.r0; if(r0>8) c.setAttribute('r',r0*P.glow);});
   },P);
   await p.screenshot({path:`${OUT}/${name}/${String(f).padStart(3,'0')}.png`});
  }
 }
 await b.close();})();
