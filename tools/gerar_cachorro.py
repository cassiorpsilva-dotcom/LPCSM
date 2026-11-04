#!/usr/bin/env python3
"""
Cachorro zumbi no estilo "dark fantasy estilizado", em SVG com rig de quadrúpede (16 partes).

Uso:  python3 tools/gerar_cachorro.py [pasta_saida]
Gera:
  cachorro_zumbi_estilizado_lado_separado.svg           vista lateral, virado para a direita
  cachorro_zumbi_estilizado_lado_esquerda_separado.svg  espelho

Partes (<g id>, data-pivot = articulação):
  cauda                      base da cauda
  perna_<par>_sup            ombro (dianteira) ou quadril (traseira)
  perna_<par>_inf            cotovelo (dianteira) ou joelho (traseira)
  pata_<par>                 punho (dianteira) ou jarrete (traseira)
     <par> = diant_perto | diant_longe | tras_perto | tras_longe   (perto = lado do observador)
  tronco                     centro do corpo
  cabeca                     base do pescoço
  mandibula                  articulação da mandíbula (abre a boca)
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from gerar_estilizado import part, ln, tube, circ, seg, band, knob, loc, poly, fmt, espelhar, OL, IW, SW

P = dict(FUR="#5d6166", FURD="#43474c", FURF="#474b50", FURFD="#33363a", WH="#d8d8d2", WHD="#aaaaa2",
         WHF="#b4b4ac", WHFD="#8e8e86", FLESH="#9a4c55", FLESHD="#6a2c36", CAV="#2c1418",
         BONE="#ece6c8", BONED="#c4bc98", NOSE="#26262c", GUM="#a8404c", TEETH="#f4f1e2",
         GLOW="#9be36a", GLOWL="#eaffd6", GLOWD="#2f4a2c", EARIN="#a8606a", EARIND="#7e4048", DROOL="#86d8e6")

J = dict(tronco=(118, 150), cabeca=(180, 122), mandibula=(206, 122), cauda=(60, 140),
         tras_perto=[(80, 158), (94, 188), (76, 211), (78, 237)],
         tras_longe=[(92, 156), (108, 186), (94, 209), (96, 237)],
         diant_perto=[(164, 160), (160, 192), (162, 216), (166, 237)],
         diant_longe=[(152, 158), (146, 190), (146, 214), (150, 237)])

ORDEM = ["perna_tras_longe_sup", "perna_tras_longe_inf", "pata_tras_longe",
         "perna_diant_longe_sup", "perna_diant_longe_inf", "pata_diant_longe",
         "cauda", "tronco",
         "perna_tras_perto_sup", "perna_tras_perto_inf", "pata_tras_perto",
         "perna_diant_perto_sup", "perna_diant_perto_inf", "pata_diant_perto",
         "mandibula", "cabeca"]

def ferida(d, d_in=None):
    o = part(d, P["FLESH"], swd=IW + 0.4)
    if d_in:
        o += part(d_in, P["FLESHD"], stroke=False)
    return o

def pata(chao, cor, sombra):
    """pata de lado (virada para a direita) com dedos e garras; chao = ponto na base"""
    o = part(loc(chao, "M-8,-7 C-7,-10 5,-10 10,-6 L14,-3 C16,0 15,2 13,2 L-9,2 C-10,-1 -10,-4 -8,-7 Z"), cor,
             loc(chao, "M-10,-1 L15,-1 C15,1 14,2 13,2 L-9,2 Z"), sombra)
    o += ln(loc(chao, "M3,-6 L3,1 M8,-5 L8,1"), OL, IW)
    for x in (6, 11, 16):
        o += part(loc(chao, f"M{x-2},0 L{x+2},1 L{x-1},2.5 Z"), OL, stroke=False)
    return o

def perna(nome, perto):
    a, b, c, chao = J[nome]
    tras = nome.startswith("tras")
    F, FD = (P["FUR"], P["FURD"]) if perto else (P["FURF"], P["FURFD"])
    W, WD = (P["WH"], P["WHD"]) if perto else (P["WHF"], P["WHFD"])
    g = {}
    if tras:
        sup = seg(a, b, 15, 7, F, FD)
        if perto:  # fêmur exposto
            sup += ferida(f"M{a[0]-7},{a[1]+2} C{a[0]-4},{a[1]-6} {a[0]+10},{a[1]-6} {a[0]+12},{a[1]+4} C{a[0]+10},{a[1]+10} {a[0]-4},{a[1]+10} {a[0]-7},{a[1]+2} Z",
                          f"M{a[0]-3},{a[1]+2} C{a[0]-1},{a[1]-2} {a[0]+7},{a[1]-2} {a[0]+8},{a[1]+3} C{a[0]+6},{a[1]+6} {a[0]-1},{a[1]+6} {a[0]-3},{a[1]+2} Z")
            sup += seg((a[0] + 2, a[1] + 3), (b[0] - 2, b[1] - 3), 3, 2.6, P["BONE"], P["BONED"])
            sup += knob((a[0] + 2, a[1] + 2), 3.4, P["BONE"]) + knob((b[0] - 2, b[1] - 3), 3.2, P["BONE"])
        g["sup"] = sup
        g["inf"] = seg(b, c, 7, 5, F, FD) + ln(f"M{b[0]-3},{b[1]+6} L{b[0]-6},{b[1]+10}", FD, IW)
        pt = seg(c, (chao[0], chao[1] - 6), 5, 4.5, W if perto else F, WD if perto else FD)
        if perto:
            pt += band(c, (chao[0], chao[1] - 6), 0.0, 0.22, 5.6, P["FLESH"], P["FLESHD"])
        g["pata"] = pt + pata(chao, W if perto else F, WD if perto else FD)
    else:
        sup = seg(a, b, 12, 7, F, FD)
        if perto:  # úmero exposto
            sup += ferida(f"M{a[0]-8},{a[1]} C{a[0]-6},{a[1]-8} {a[0]+6},{a[1]-8} {a[0]+8},{a[1]} C{a[0]+6},{a[1]+8} {a[0]-6},{a[1]+8} {a[0]-8},{a[1]} Z",
                          f"M{a[0]-4},{a[1]} C{a[0]-3},{a[1]-4} {a[0]+3},{a[1]-4} {a[0]+4},{a[1]} C{a[0]+3},{a[1]+4} {a[0]-3},{a[1]+4} {a[0]-4},{a[1]} Z")
            sup += seg((a[0], a[1] + 4), (b[0], b[1] - 2), 3.2, 2.8, P["BONE"], P["BONED"])
            sup += knob((a[0] - 1, a[1] + 3), 3.6, P["BONE"]) + knob((b[0], b[1] - 2), 3.2, P["BONE"])
        else:
            sup += ferida(f"M{a[0]-6},{a[1]+14} C{a[0]-4},{a[1]+8} {a[0]+4},{a[1]+8} {a[0]+5},{a[1]+14} C{a[0]+4},{a[1]+20} {a[0]-4},{a[1]+22} {a[0]-6},{a[1]+14} Z",
                          f"M{a[0]-3},{a[1]+14} C{a[0]-2},{a[1]+11} {a[0]+2},{a[1]+11} {a[0]+2},{a[1]+14} C{a[0]+2},{a[1]+17} {a[0]-2},{a[1]+18} {a[0]-3},{a[1]+14} Z")
        g["sup"] = sup
        inf = seg(b, c, 6, 5, W, WD)
        if perto:
            inf += band(b, c, 0.0, 0.2, 6.6, P["FLESH"], P["FLESHD"]) + ln(f"M{b[0]+2},{b[1]+10} L{b[0]+3},{b[1]+20}", WD, IW)
        g["inf"] = inf
        g["pata"] = seg(c, (chao[0], chao[1] - 6), 5, 4.5, W, WD) + pata(chao, W, WD)
    return g

def cachorro_lado():
    g = {}
    for nome in ("tras_longe", "diant_longe", "tras_perto", "diant_perto"):
        p = perna(nome, nome.endswith("perto"))
        g[f"perna_{nome}_sup"], g[f"perna_{nome}_inf"], g[f"pata_{nome}"] = p["sup"], p["inf"], p["pata"]
    # ---- cauda
    g["cauda"] = (part("M64,134 C50,138 40,150 34,168 L28,182 L35,178 L33,191 L41,180 L44,184 C48,168 54,154 66,146 Z", P["FUR"],
                       "M66,146 C54,154 48,168 44,184 L41,180 C42,166 48,152 60,142 Z", P["FURD"])
                  + part("M28,182 L35,178 L33,191 L41,180 C40,175 36,172 31,174 Z", P["WH"], swd=IW + 0.4))
    # ---- tronco (com pescoço)
    t = part("M62,136 C80,126 120,127 150,124 C160,122 166,114 172,102 L194,110 C195,124 192,138 186,150 L180,156 L184,162 L174,168 "
             "L176,176 L166,180 L162,186 L152,184 C140,186 124,182 110,176 L104,180 L100,174 C92,174 82,176 74,176 C62,172 54,160 54,148 C54,142 58,138 62,136 Z", P["FUR"],
             "M54,148 C56,162 64,172 74,176 C82,176 92,174 100,174 L104,180 L110,176 C124,182 140,186 152,184 L162,186 L166,180 C150,176 130,172 110,168 C92,166 74,164 62,152 Z", P["FURD"])
    t += part("M172,102 L194,110 C195,124 192,138 186,150 L180,156 L184,162 L174,168 L176,176 L166,180 C160,168 158,152 160,138 C162,124 166,112 172,102 Z", P["WH"],
              "M160,146 C163,158 168,166 174,168 L176,176 L166,180 C161,170 159,158 160,146 Z", P["WHD"], swd=IW + 0.6)
    t += ln("M120,138 L126,145 M133,134 L137,142 M96,138 L100,146 M146,136 L150,143 M80,142 L84,149 M168,124 L172,132 M176,136 L180,142", P["FURD"], IW)
    t += ferida("M84,131 C92,126 106,126 113,131 C109,138 94,140 85,136 Z", "M90,132 C96,129 104,129 108,132 C104,135 96,136 90,134 Z")
    t += ferida("M102,150 C108,142 132,140 143,147 C147,156 143,167 132,171 C119,173 106,169 102,160 Z")
    t += part("M107,152 C113,147 130,146 138,150 C141,157 138,164 130,167 C119,169 110,165 107,158 Z", P["CAV"], stroke=False)
    for d in ["M111,150 C112,156 115,162 119,167", "M117,148.5 C119,155 122,161 126,167", "M124,148 C127,154 130,160 133,165", "M131,148.5 C134,153 137,158 139,161"]:
        t += tube(d, 2.6, P["BONE"])
    t += ferida("M60,150 C62,145 70,145 72,150 C72,155 64,157 60,154 Z")
    g["tronco"] = t
    # ---- mandíbula (abre girando no pivô)
    m = part("M204,104 L238,108 L238,124 L204,124 Z", P["CAV"], stroke=False)
    m += part("M203,121 L238,123.5 C239,128 235,132 228,134 L212,136 C206,134 201,128 203,121 Z", P["WH"],
              "M204,129 C210,131 220,131 236,129 C233,132 230,133.5 228,134 L212,136 C207,134.5 205,132 204,129 Z", P["WHD"])
    m += part("M207,122 L237,124 L236.5,127 L208,125.5 Z", P["GUM"], swd=IW)
    m += part("M210,124.5 L212.5,120.5 L215,124.8 L217.5,120.7 L220,125 L222.5,121 L225,125.2 L228,121 L231,125.4 L234,121.5 L236,125.5 Z", P["TEETH"], swd=IW * 0.9)
    m += part("M226,124.5 L230.5,124.8 L228.5,115.5 Z", P["TEETH"], swd=IW)
    m += part("M231,133 C231.5,137 232.5,141 231.8,146 C231.3,149 228.5,149 228.6,146 C228.8,141 229.5,137 229.2,133.5 Z", P["DROOL"], swd=IW)
    m += part("M222,134.5 C222.3,137 222.8,139 222.3,141 C222,142.5 220.4,142.5 220.4,141 C220.4,139 220.7,137 220.6,135 Z", P["DROOL"], swd=IW * 0.9)
    g["mandibula"] = m
    # ---- cabeça
    c = part("M184,98 L186,64 L203,90 Z", P["FURF"], "M187,92 L188,70 L199,89 Z", P["EARIND"], swd=IW + 0.6)
    c += part("M182,96 C184,84 196,78 208,80 C216,82 222,88 226,96 L240,103 C244,105 246,109 245,113 L243,120 C234,122 222,122 212,122 "
              "L198,124 L192,122 L186,124 L184,118 L178,118 L182,112 L176,108 L182,104 Z", P["FUR"],
              "M182,104 L176,108 L182,112 L178,118 L184,118 L186,124 L192,122 L198,124 L212,122 C204,118 197,112 193,104 C191,98 189,92 187,88 C184,92 182,98 182,104 Z", P["FURD"])
    c += part("M214,90 C222,93 230,99 240,103 C244,105 246,109 245,113 L243,120 C234,122 224,121.5 214,121 C215,112 213,100 214,90 Z", P["WH"],
              "M214,114 C224,116 234,117 244,116 L243,120 C234,122 224,121.5 214,121 Z", P["WHD"], swd=IW + 0.4)
    c += part("M208,80 C211,84 213,88 214,92 C211,92 208,90 206,86 C205,84 206,81 208,80 Z", P["WH"], stroke=False)
    c += part("M191,92 L195,56 L215,86 Z", P["FUR"], "M195,86 L196.5,64 L209,84 Z", P["EARIN"], swd=IW + 0.8)
    c += part("M195,86 L196.5,64 L203,74 L200,77 L203,79 Z", P["EARIND"], stroke=False)
    c += ferida("M184,103 C188,98 196,100 197,107 C197,114 190,117 185,113 Z", "M187,105 C189,102 193,103 194,107 C194,110 190,112 188,110 Z")
    c += circ(205, 98, 7.6, P["GLOWD"], True, IW + 0.6) + circ(205, 98, 5.6, P["GLOW"]) + circ(205, 98, 3.4, P["GLOWL"]) + circ(205, 98, 3.4, "none", True, 0.9) + circ(205, 98, 1.1, P["GLOWD"])
    c += part("M193,88.5 L217,94 L216,98 L194,92.5 Z", OL, stroke=False)
    c += ln("M218,95 C220,93 223,93 225,95.5 M222,99 C224,97 227,97 229,99.5 M226,102 C228,100.5 230,100.5 232,102.5", P["FURD"], IW + 0.2)
    c += ln("M211,108 C213,110 213,113 211,115", P["FURD"], IW)
    c += part("M238,102 C242,100 248,102 248,107 C248,111 245,113 241,112 C238,111 235.5,106 238,102 Z", P["NOSE"], swd=IW + 0.4) + circ(242.5, 104, 1.3, "#6a6a74")
    c += part("M209,119.5 L243,117.5 L243,121.5 L210,123.5 Z", P["GUM"], swd=IW)
    c += part("M212,123 L214.5,127.5 L217,122.8 L219.5,127.5 L222,122.6 L224.5,127.5 L227,122.4 L229.5,127.3 L232,122.2 L234.5,127 L237,122 L239.5,126.5 L242,121.6 Z", P["TEETH"], swd=IW * 0.9)
    c += part("M228,121.5 L234,121 L231.5,135 Z", P["TEETH"], swd=IW + 0.2)
    c += ln("M203,117 C205,121 207,123 210,123.5", OL, IW + 0.4)
    c += circ(222, 112, 0.8, P["FURD"]) + circ(226, 113, 0.8, P["FURD"]) + circ(224, 115.5, 0.8, P["FURD"])
    g["cabeca"] = c
    return g

def pivots():
    pv = {"tronco": J["tronco"], "cabeca": J["cabeca"], "mandibula": J["mandibula"], "cauda": J["cauda"]}
    for nome in ("tras_perto", "tras_longe", "diant_perto", "diant_longe"):
        a, b, c, _ = J[nome]
        pv[f"perna_{nome}_sup"], pv[f"perna_{nome}_inf"], pv[f"pata_{nome}"] = a, b, c
    return pv

def main():
    D = sys.argv[1] if len(sys.argv) > 1 else "."
    g, pv = cachorro_lado(), pivots()
    out = ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 256 256" width="256" height="256">\n'
           '<!-- Cachorro zumbi - estilo dark fantasy estilizado. Vista lateral, virado para a direita. Patas em y=239.\n'
           '     Rig de quadrúpede (16 partes); data-pivot = articulação (ombro/quadril, cotovelo/joelho, punho/jarrete,\n'
           '     base do pescoço, articulação da mandíbula, base da cauda, centro do corpo). -->\n')
    for k in ORDEM:
        out += f'<g id="{k}" data-pivot="{fmt(pv[k][0])},{fmt(pv[k][1])}">\n{g[k]}</g>\n'
    out += "</svg>\n"
    open(os.path.join(D, "cachorro_zumbi_estilizado_lado_separado.svg"), "w").write(out)
    open(os.path.join(D, "cachorro_zumbi_estilizado_lado_esquerda_separado.svg"), "w").write(espelhar(out))
    print("cachorro ok")

if __name__ == "__main__":
    main()
