// Renderiza um SVG em PNG do tamanho exato do SVG, com fundo transparente.
// Uso: node tools/svg_para_png.js entrada.svg saida.png [overlay_debug.json]
const {chromium} = require('playwright'); const fs = require('fs');
(async () => {
  const [src, dst] = process.argv.slice(2);
  const svg = fs.readFileSync(src, 'utf8');
  const m = /width="(\d+)" height="(\d+)"/.exec(svg);
  const w = +m[1], h = +m[2];
  const b = await chromium.launch(); const p = await b.newPage({viewport: {width: w, height: h}});
  await p.setContent(`<html><body style="margin:0;background:transparent">${svg}</body></html>`);
  await p.screenshot({path: dst, omitBackground: true, clip: {x: 0, y: 0, width: w, height: h}});
  await b.close();
})();
