#!/usr/bin/env python3
"""Monta GIFs a partir das pastas de quadros geradas por tools/animar_svg.js.
Uso: python3 tools/quadros_para_gif.py PASTA_QUADROS previews/necromante
     -> previews/necromante_parado.gif, _andando.gif, _conjurando.gif"""
import sys, glob, os
from PIL import Image
pasta, prefixo = sys.argv[1], sys.argv[2]
MS = {"parado": 90, "andando": 85, "conjurando": 70}
for nome in sorted(os.listdir(pasta)):
    fr = [Image.open(f).convert("RGB").crop((60, 24, 560, 504)) for f in sorted(glob.glob(f"{pasta}/{nome}/*.png"))]
    if not fr: continue
    big = Image.new("RGB", (fr[0].width, fr[0].height * len(fr)))
    for i, f in enumerate(fr): big.paste(f, (0, i * f.height))
    pal = big.quantize(colors=160, method=Image.Quantize.MEDIANCUT)
    q = [f.quantize(palette=pal, dither=Image.Dither.NONE) for f in fr]
    q[0].save(f"{prefixo}_{nome}.gif", save_all=True, append_images=q[1:], duration=MS.get(nome, 80), loop=0, optimize=True, disposal=2)
    print(f"{prefixo}_{nome}.gif: {len(fr)} quadros")
