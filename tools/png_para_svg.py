#!/usr/bin/env python3
"""
Converte partes de personagem em pixel art (PNGs separados) em UM SVG
com cada parte num grupo <g id="..."> e o pivô em data-pivot.

Uso:
  python3 tools/png_para_svg.py PASTA_PARTES saida.svg [--meta meta.json] [--escala 4]

PASTA_PARTES: um PNG por parte, todos com o MESMO tamanho de canvas
              (ex.: 64x64), cada parte já desenhada na sua posição final.
              O nome do arquivo vira o id do grupo (cabeca.png -> id="cabeca").
meta.json (opcional):
  {"ordem": ["braco_tras", "...", "mao_frente"],     # ordem de desenho (trás -> frente)
   "pivots": {"cabeca": [33, 25], ...},                # em pixels do canvas
   "comentario": "texto livre"}

Cada pixel opaco (alfa >= 128) vira parte de um retângulo; pixels vizinhos da
mesma cor na mesma linha são juntados, e tudo de uma mesma cor fica num único
<path>. O SVG usa shape-rendering="crispEdges" para ficar nítido em qualquer escala.
"""
import sys, os, json, argparse
from PIL import Image

def parte_para_paths(img):
    img = img.convert("RGBA")
    w, h = img.size
    px = img.load()
    por_cor = {}
    for y in range(h):
        x = 0
        while x < w:
            r, g, b, a = px[x, y]
            if a < 128:
                x += 1
                continue
            cor = f"#{r:02x}{g:02x}{b:02x}"
            x0 = x
            while x < w and px[x, y][3] >= 128 and f"#{px[x, y][0]:02x}{px[x, y][1]:02x}{px[x, y][2]:02x}" == cor:
                x += 1
            por_cor.setdefault(cor, []).append(f"M{x0},{y}h{x - x0}v1h-{x - x0}z")
    return "".join(f'<path fill="{c}" d="{"".join(runs)}"/>\n' for c, runs in por_cor.items())

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("pasta")
    ap.add_argument("saida")
    ap.add_argument("--meta")
    ap.add_argument("--escala", type=int, default=4, help="tamanho de exibição = canvas x escala")
    a = ap.parse_args()
    meta = json.load(open(a.meta)) if a.meta else {}
    nomes = sorted(f[:-4] for f in os.listdir(a.pasta) if f.lower().endswith(".png"))
    ordem = [n for n in meta.get("ordem", []) if n in nomes] + [n for n in nomes if n not in meta.get("ordem", [])]
    piv = meta.get("pivots", {})
    tam = None
    out = []
    for n in ordem:
        img = Image.open(os.path.join(a.pasta, n + ".png"))
        if tam and img.size != tam:
            sys.exit(f"{n}.png tem tamanho {img.size}, esperado {tam}")
        tam = img.size
        attr = f' data-pivot="{piv[n][0]:g},{piv[n][1]:g}"' if n in piv else ""
        out.append(f'<g id="{n}"{attr}>\n{parte_para_paths(img)}</g>\n')
    w, h = tam
    svg = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w * a.escala}" height="{h * a.escala}" shape-rendering="crispEdges">\n')
    if meta.get("comentario"):
        svg += f"<!-- {meta['comentario']} -->\n"
    svg += "".join(out) + "</svg>\n"
    open(a.saida, "w").write(svg)
    print(f"{a.saida}: {len(ordem)} partes, canvas {w}x{h}")

if __name__ == "__main__":
    main()
