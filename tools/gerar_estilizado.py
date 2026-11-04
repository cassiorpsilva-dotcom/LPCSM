#!/usr/bin/env python3
"""
Gera os personagens no estilo "dark fantasy estilizado" (cel-shading 2 tons, contorno escuro),
em SVG com o rig expandido de 16 partes, cada uma num <g id> com data-pivot na articulação.

Uso:  python3 tools/gerar_estilizado.py [pasta_saida]
Gera, para cada personagem (necromante, medusa, ninja):
  <nome>_estilizado_lado_separado.svg           vista lateral, virado para a direita
  <nome>_estilizado_lado_esquerda_separado.svg  espelho da lateral
  <nome>_estilizado_costas_separado.svg         vista de costas

Todos os personagens usam o MESMO esqueleto (mesmas articulações), então as animações de
tools/animar_svg.js servem para qualquer um deles.
"""
import re, math, sys, os

# ------------------------------------------------------------------ utilitários
def fmt(v):
    s = f"{v:.1f}"
    return s[:-2] if s.endswith(".0") else s

def tp(d, f):
    """aplica f(x,y) a todos os pares 'x,y' de um path (só comandos absolutos)"""
    return re.sub(r'(-?\d+(?:\.\d+)?),(-?\d+(?:\.\d+)?)',
                  lambda m: "%s,%s" % tuple(map(fmt, f(float(m.group(1)), float(m.group(2))))), d)

def poly(pts):
    return "M" + " L".join(f"{fmt(x)},{fmt(y)}" for x, y in pts) + " Z"

OL, SW, IW = "#1a1422", 2.5, 1.4

def part(d, fill, shade=None, shade_fill=None, stroke=True, swd=None):
    o = f'<path d="{d}" fill="{fill}"/>\n'
    if shade:
        o += f'<path d="{shade}" fill="{shade_fill}"/>\n'
    if stroke:
        o += f'<path d="{d}" fill="none" stroke="{OL}" stroke-width="{swd or SW}" stroke-linejoin="round"/>\n'
    return o

def ln(d, col, w):
    return f'<path d="{d}" fill="none" stroke="{col}" stroke-width="{w}" stroke-linecap="round" stroke-linejoin="round"/>\n'

def tube(d, w, col):
    return ln(d, OL, w + SW * 2) + ln(d, col, w)

def tube_cs(d, w, base, shade, band=None):
    """tubo com cel-shading: borda escura, faixa clara no centro e escamas opcionais"""
    o = ln(d, OL, w + SW * 2) + ln(d, shade, w) + ln(d, base, w * 0.55)
    if band:
        o += f'<path d="{d}" fill="none" stroke="{band}" stroke-width="{w}" stroke-dasharray="1.4 6"/>\n'
    return o

def circ(x, y, r, fill, stroke=False, swd=None):
    st = f' stroke="{OL}" stroke-width="{swd or IW}"' if stroke else ""
    return f'<circle cx="{fmt(x)}" cy="{fmt(y)}" r="{fmt(r)}" fill="{fill}"{st}/>\n'

def frame(p1, p2):
    dx, dy = p2[0] - p1[0], p2[1] - p1[1]
    L = math.hypot(dx, dy)
    ux, uy = dx / L, dy / L
    nx, ny = -uy, ux
    return (lambda u, v: (p1[0] + ux * u + nx * v, p1[1] + uy * u + ny * v)), L

def seg(p1, p2, w1, w2, fill, shade_fill, k=0.35, side=1):
    """membro: cápsula afunilada de p1 a p2 com sombra num dos lados (side=1 ou -1)"""
    F, L = frame(p1, p2)
    P = lambda u, v: "%s,%s" % tuple(map(fmt, F(u, v * side)))
    d = (f"M{P(0,w1)} L{P(L,w2)} Q{P(L+w2,w2)} {P(L+w2,0)} Q{P(L+w2,-w2)} {P(L,-w2)} "
         f"L{P(0,-w1)} Q{P(-w1,-w1)} {P(-w1,0)} Q{P(-w1,w1)} {P(0,w1)} Z")
    sh = f"M{P(0,w1)} L{P(L,w2)} Q{P(L+w2,w2)} {P(L+w2,0)} L{P(L,w2*k)} L{P(0,w1*k)} L{P(-w1,0)} Q{P(-w1,w1)} {P(0,w1)} Z"
    return part(d, fill, sh, shade_fill)

def band(p1, p2, u0, u1, w, fill, shade_fill=None):
    """faixa (bracelete, polaina) ao redor de um membro, entre u0 e u1 (frações do comprimento)"""
    F, L = frame(p1, p2)
    pts = [F(L * u0, -w), F(L * u1, -w), F(L * u1, w), F(L * u0, w)]
    sh = [F(L * u0, w * 0.2), F(L * u1, w * 0.2), F(L * u1, w), F(L * u0, w)] if shade_fill else None
    return part(poly(pts), fill, poly(sh) if sh else None, shade_fill, swd=IW + 0.4)

def loc(anchor, d, s=1.0, flip=False):
    fx = -1 if flip else 1
    return tp(d, lambda x, y: (anchor[0] + x * s * fx, anchor[1] + y * s))

def knob(c, r, fill):
    x, y = c
    return part(f"M{fmt(x-r)},{fmt(y)} C{fmt(x-r)},{fmt(y-r*1.33)} {fmt(x+r)},{fmt(y-r*1.33)} {fmt(x+r)},{fmt(y)} "
                f"C{fmt(x+r)},{fmt(y+r*1.33)} {fmt(x-r)},{fmt(y+r*1.33)} {fmt(x-r)},{fmt(y)} Z", fill)

# ------------------------------------------------------------------ esqueleto (mesmo para todos)
# vista lateral, virado para a direita. "frente" = lado mais próximo do observador.
J_LADO = dict(neck=(136, 114), sh_b=(126, 124), sh_f=(138, 124), el_b=(114, 146), wr_b=(103, 164),
              el_f=(156, 142), wr_f=(178, 148), grip=(188, 150), waist=(132, 165), hip=(130, 178),
              hip_b=(124, 180), hip_f=(134, 180), kn_b=(120, 206), kn_f=(138, 206), an_b=(116, 232), an_f=(142, 232))
# vista de costas. "frente" = lado DIREITO do personagem (segura a arma), que aparece à DIREITA da tela.
J_COSTAS = dict(neck=(128, 114), sh_b=(113, 124), sh_f=(143, 124), el_b=(104, 146), wr_b=(99, 166),
                el_f=(153, 146), wr_f=(159, 164), grip=(166, 168), waist=(128, 165), hip=(128, 178),
                hip_b=(121, 180), hip_f=(135, 180), kn_b=(119, 206), kn_f=(137, 206), an_b=(118, 232), an_f=(138, 232))

ORDEM_LADO = ["braco_sup_tras", "antebraco_tras", "mao_tras", "coxa_tras", "canela_tras", "pe_tras",
              "coxa_frente", "canela_frente", "pe_frente", "quadril", "tronco", "cabeca", "arma",
              "braco_sup_frente", "antebraco_frente", "mao_frente"]
ORDEM_COSTAS = ["coxa_tras", "canela_tras", "pe_tras", "coxa_frente", "canela_frente", "pe_frente",
                "quadril", "tronco", "cabeca", "braco_sup_tras", "antebraco_tras", "mao_tras", "arma",
                "braco_sup_frente", "antebraco_frente", "mao_frente"]

def pivots(J):
    return {"cabeca": J["neck"], "tronco": J["waist"], "quadril": J["hip"],
            "braco_sup_tras": J["sh_b"], "antebraco_tras": J["el_b"], "mao_tras": J["wr_b"],
            "braco_sup_frente": J["sh_f"], "antebraco_frente": J["el_f"], "mao_frente": J["wr_f"],
            "coxa_tras": J["hip_b"], "canela_tras": J["kn_b"], "pe_tras": J["an_b"],
            "coxa_frente": J["hip_f"], "canela_frente": J["kn_f"], "pe_frente": J["an_f"], "arma": J["grip"]}

def montar(g, J, ordem, comentario):
    piv = pivots(J)
    out = ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 256 256" width="256" height="256">\n'
           f'<!-- {comentario}\n     Rig de 16 partes; data-pivot = articulação (ombro, cotovelo, punho, quadril, joelho, '
           'tornozelo, pescoço, cintura, empunhadura). Pés em y=240. -->\n')
    for k in ordem:
        out += f'<g id="{k}" data-pivot="{fmt(piv[k][0])},{fmt(piv[k][1])}">\n{g[k]}</g>\n'
    return out + "</svg>\n"

def espelhar(svg):
    svg = re.sub(r' d="([^"]*)"', lambda m: f' d="{tp(m.group(1), lambda x, y: (256 - x, y))}"', svg)
    svg = re.sub(r' cx="([^"]*)"', lambda m: f' cx="{fmt(256 - float(m.group(1)))}"', svg)
    svg = re.sub(r'data-pivot="([\d.]+),([\d.]+)"', lambda m: f'data-pivot="{fmt(256 - float(m.group(1)))},{m.group(2)}"', svg)
    return svg.replace("virado para a direita", "virado para a ESQUERDA (espelho da vista lateral direita)")

# ------------------------------------------------------------------ peças comuns
def braco_manga(J, s, cor, sombra, sombra_cor, w=9, lado=True):
    """braço superior + antebraço em manga larga rasgada (necromante)"""
    g = {}
    sh, el, wr = J["sh_" + s], J["el_" + s], J["wr_" + s]
    g["braco_sup"] = seg(sh, el, w - (1 if s == "b" else 0), w - (1 if s == "b" else 0), cor, sombra_cor)
    F, L = frame(el, wr)
    k = 1 if (s == "f" or not lado) else 1
    sl = [(0, -w), (L * 0.5, -w - 1), (L + 2, -w - 3), (L - 1, -w + 2), (L + 3, -3), (L, 1), (L + 5, 5), (L, 9),
          (L + 4, 15), (L - 2, 13), (L - 4, 20), (L * 0.4, 13), (0, w)]
    shp = [(0, 4), (L * 0.5, 5), (L, 9), (L + 4, 15), (L - 2, 13), (L - 4, 20), (L * 0.4, 13), (0, w)]
    g["antebraco"] = part(poly([F(u, v) for u, v in sl]), cor, poly([F(u, v) for u, v in shp]), sombra_cor)
    return g

def cajado(x, top, P, bottom=238):
    lft = [(x - 3, top), (x - 4, top + 22), (x - 2, top + 44), (x - 5, top + 70), (x - 3, top + 100), (x - 5, top + 130), (x - 2, bottom)]
    rgt = [(x + 4, bottom), (x + 3, top + 130), (x + 5, top + 100), (x + 3, top + 70), (x + 4, top + 44), (x + 2, top + 22), (x + 3, top)]
    shp = poly(lft + [(x - 1, bottom)] + [(x - 1, p[1]) for p in reversed(lft[:-1])])
    a = part(poly(lft + rgt), P["WOOD"], shp, P["WOODD"])
    a += part(poly([(x - 5, top + 50), (x - 9, top + 44), (x - 8, top + 42), (x - 4, top + 46)]), P["WOOD"], swd=IW)
    return a

def brilho(c, s, P):
    a = circ(c[0], c[1], 17 * s, P["HALO1"]) + circ(c[0], c[1], 13 * s, P["HALO2"])
    for d in ["M-16,-14 C-20,-20 -18,-26 -12,-28", "M16,8 C22,4 24,-2 21,-8", "M-14,10 C-18,14 -18,18 -15,21"]:
        a += ln(loc(c, d, s), P["GLOW"], 2 * s)
    return a

# ================================================================== NECROMANTE
PN = dict(PU="#6a4c8c", PUD="#46306a", PUDD="#36245a", PUL="#9478b8", IN="#140f1c",
          BONE="#e6e2c6", BONED="#b9b493", BONEF="#c9c4a4", BONEFD="#9d987a", LEA="#6e4e2e", LEAD="#4e3620",
          GOLD="#c9a23a", WOOD="#6e4a2c", WOODD="#4a3020", GLOW="#8be04a", HALO1="#c4f39a", HALO2="#eaffd6",
          SKG="#b8e48a", SKGD="#86b85c", EYE="#0f1a0c")

def pernas_osso(J, g, P, costas=False):
    for side, far in (("tras", True), ("frente", False)):
        B, BD = (P["BONEF"], P["BONEFD"]) if far else (P["BONE"], P["BONED"])
        h, k, a = (J["hip_b"], J["kn_b"], J["an_b"]) if far else (J["hip_f"], J["kn_f"], J["an_f"])
        g["coxa_" + side] = seg(h, k, 4.5, 3.6, B, BD)
        g["canela_" + side] = seg(k, a, 3.6, 2.8, B, BD) + knob(k, 4.5, B)
        a2 = (a[0], 232)
        if costas:
            g["pe_" + side] = part(loc(a2, "M-5,-3 L5,-3 C6,1 7,5 7,8 L-7,8 C-7,5 -6,1 -5,-3 Z"), B,
                                   loc(a2, "M-7,5 L7,5 L7,8 L-7,8 Z"), BD) + ln(loc(a2, "M-3,4 L-3,8 M3,4 L3,8"), OL, IW)
        else:
            g["pe_" + side] = (part(loc(a2, "M-5,-3 L4,-3 C10,-1 16,2 20,5 L24,8 L-6,8 C-7,4 -6,0 -5,-3 Z"), B,
                                    loc(a2, "M-6,4 L22,6 L24,8 L-6,8 Z"), BD)
                               + ln(loc(a2, "M9,1.5 L12,8 M15,3.5 L18,8"), OL, IW))

def garra(w, P, cor, espelho=False):
    m = part(loc(w, "M-4,0 L4,0 L5,8 L-4,9 Z", flip=espelho), cor, swd=IW + 0.6)
    for d in ["M3,9 C4,15 2,20 -1,23", "M0,9 C-1,15 -3,20 -7,22", "M-3,8 C-6,13 -9,16 -13,16", "M4,2 C7,5 8,8 7,11"]:
        m += tube(loc(w, d, flip=espelho), 2.4, cor)
    return m

def punho(G, wr, P, cor, sombra, costas=False):
    m = seg(wr, (G[0] - 7, G[1]) if not costas else (G[0], G[1] - 4), 2.4, 2.4, cor, sombra)
    if costas:
        m += part(loc(G, "M-7,-6 L7,-6 L8,4 L5,8 L-5,8 L-8,4 Z"), cor, loc(G, "M-8,3 L8,3 L8,4 L5,8 L-5,8 L-8,4 Z"), sombra, swd=IW + 0.8)
        m += ln(loc(G, "M-3,-5 L-3,6 M1,-5 L1,7 M5,-5 L5,6"), OL, IW)
    else:
        m += part(loc(G, "M-8,-5 L-2,-8 L5,-7 L8,-3 L8,4 L4,7 L-3,7 L-8,4 Z"), cor, loc(G, "M-8,2 L8,2 L8,4 L4,7 L-3,7 L-8,4 Z"), sombra, swd=IW + 0.8)
        m += ln(loc(G, "M-3,-2 L8,-2 M-3,2 L8,2"), OL, IW) + tube(loc(G, "M-6,-5 L1,-9"), 2.4, cor)
    return m

def necro_lado():
    P, J = PN, J_LADO
    g = {}
    hx, hy, hs = 144, 94, 0.8
    H = lambda d: loc((hx, hy), d, hs)
    c = part(H("M-30,-4 C-34,-18 -40,-28 -50,-34 C-36,-36 -20,-42 6,-42 C22,-42 34,-30 36,-12 C38,4 34,18 24,28 L-4,34 C-22,30 -32,14 -30,-4 Z"), P["PU"],
             H("M-30,-4 C-34,-18 -40,-28 -50,-34 C-40,-30 -28,-24 -20,-12 C-14,0 -12,18 -4,34 C-22,30 -32,14 -30,-4 Z"), P["PUD"])
    c += part(H("M-10,-40 C6,-43 22,-38 30,-26 C20,-33 6,-37 -10,-40 Z"), P["PUL"], stroke=False)
    c += part(H("M8,-30 C24,-28 34,-14 34,0 C34,14 28,24 20,30 L2,32 C-2,14 -2,-14 8,-30 Z"), P["IN"], swd=IW)
    c += part(H("M6,-22 C20,-24 31,-12 31,0 C31,4 30,7 28,9 L29,14 L24,16 L22,20 L6,22 C0,16 -1,4 0,-8 C1,-15 3,-20 6,-22 Z"), P["BONE"],
              H("M0,-8 C1,-2 3,6 9,12 L22,13 L22,20 L6,22 C0,16 -1,4 0,-8 Z"), P["BONED"], swd=IW + 0.6)
    c += part(H("M8,21 L24,18 C26,23 24,27 18,28 L10,28 C8,26 7,23 8,21 Z"), P["BONE"], H("M8,24 L24,22 C24,25 22,27 18,28 L10,28 C8,27 8,25 8,24 Z"), P["BONED"], swd=IW)
    c += ln(H("M12,20.5 L12,25 M15.5,20 L15.5,24.5 M19,19.5 L19,24 M22,19 L22,23"), OL, IW)
    c += part(H("M13,-6 L27,-4 L26,3 C22,6 17,5 15,2 Z"), P["EYE"], swd=IW)
    c += circ(hx + 21.5 * hs, hy - 0.5 * hs, 2.6 * hs, P["GLOW"])
    c += ln(H("M11,-9 L29,-5.5"), OL, SW + 0.5)
    c += part(H("M28,4 L31.5,9.5 L27,9.5 Z"), P["EYE"], swd=IW)
    c += ln(H("M15,9 C19,11 23,11 27,10"), OL, IW)
    c += ln(H("M8,-30 C-2,-14 -2,14 2,32"), P["PUL"], SW)
    g["cabeca"] = c
    t = part("M120,118 C132,108 150,112 155,126 C159,140 155,156 149,168 L117,170 C113,152 113,132 120,118 Z", P["PU"],
             "M120,118 C124,132 126,150 128,169 L117,170 C113,152 113,132 120,118 Z", P["PUD"])
    t += part("M143,124 C151,124 156,133 156,143 C155,151 151,157 145,160 L141,160 C139,148 139,134 143,124 Z", P["IN"], swd=IW)
    for y in (130, 137, 144, 151):
        t += tube(f"M141,{y} C146,{y-1} 151,{y+1} 154.5,{y+3}", 2.4, P["BONE"])
    t += ln("M142,126 L142,158", P["BONE"], 2.6)
    t += part("M110,120 C122,106 150,106 162,120 L160,134 L154,128 L150,141 L144,131 L138,143 L132,131 L126,142 L120,129 L114,137 L110,130 Z", P["PU"],
              "M110,120 C116,112 124,108 132,107 C128,114 128,124 132,131 L126,142 L120,129 L114,137 L110,130 Z", P["PUD"])
    t += part("M124,110 C136,105 150,107 158,114 C148,111 136,110 124,110 Z", P["PUL"], stroke=False)
    t += part("M116,160 L151,158 L152,167 L116,169 Z", P["LEA"], "M116,165 L152,163.5 L152,167 L116,169 Z", P["LEAD"])
    t += part("M145.5,157.5 L154,157 L154,163.5 L151.5,167 L148.5,167 L146,163.5 Z", P["GOLD"], swd=IW + 0.4)
    t += circ(148.6, 161, 1, OL) + circ(151.6, 161, 1, OL)
    g["tronco"] = t
    q = part("M116,166 L151,164 C156,180 160,198 162,214 L156,210 L151,220 L145,212 L139,222 L132,212 L126,224 L119,214 L112,228 L106,215 L99,224 C101,204 108,184 116,166 Z", P["PU"],
             "M116,166 C108,184 101,204 99,224 L106,215 L112,228 L119,214 C119,198 121,182 126,166 Z", P["PUD"])
    q += ln("M134,170 C134,186 133,200 132,210", P["PUD"], IW + 0.6) + ln("M150,168 C154,182 157,198 159,210", P["PUL"], IW + 0.4)
    g["quadril"] = q
    pernas_osso(J, g, P)
    mb = braco_manga(J, "b", P["PUD"], None, P["PUDD"], w=9)
    g["braco_sup_tras"], g["antebraco_tras"] = mb["braco_sup"], mb["antebraco"]
    g["mao_tras"] = garra(J["wr_b"], P, P["BONEF"])
    x, top = J["grip"][0], 70
    a = cajado(x, top, P)
    a += part(poly([(x - 5, top + 4), (x + 5, top + 4), (x + 5, top + 11), (x - 5, top + 11)]), P["LEA"],
              poly([(x - 5, top + 8.5), (x + 5, top + 8.5), (x + 5, top + 11), (x - 5, top + 11)]), P["LEAD"], swd=IW + 0.4)
    a += part(poly([(x - 4, top + 11), (x - 1, top + 11), (x - 3, top + 26), (x - 6, top + 24)]), P["LEA"], swd=IW)
    sk = (x + 2, top - 12)
    a += brilho(sk, 1, P)
    a += part(loc(sk, "M-10,-6 C-8,-14 6,-16 10,-6 C12,0 10,4 8,6 L8,10 L3,12 L2,16 L-6,16 C-10,12 -12,2 -10,-6 Z"), P["SKG"],
              loc(sk, "M-10,-6 C-10,2 -8,10 -4,16 L-6,16 C-10,12 -12,2 -10,-6 Z"), P["SKGD"], swd=IW + 0.6)
    a += part(loc(sk, "M-2,-3 L6,-2 L5,2 C2,4 -1,3 -2,1 Z"), P["EYE"], swd=IW) + circ(sk[0] + 2.5, sk[1], 1.4, P["GLOW"])
    a += part(loc(sk, "M9,5 L11,8.5 L8,8.5 Z"), P["EYE"], swd=IW) + ln(loc(sk, "M-4,12 L-4,16 M-1,12 L-1,16 M2,12 L2,15"), OL, IW)
    g["arma"] = a
    mf = braco_manga(J, "f", P["PU"], None, P["PUD"], w=9)
    g["braco_sup_frente"], g["antebraco_frente"] = mf["braco_sup"], mf["antebraco"]
    g["mao_frente"] = punho(J["grip"], J["wr_f"], P, P["BONE"], P["BONED"])
    return g

def necro_costas():
    P, J = PN, J_COSTAS
    g = {}
    hx, hy, hs = 128, 94, 0.8
    H = lambda d: loc((hx, hy), d, hs)
    c = part(H("M-32,0 C-34,-24 -20,-40 -2,-44 C2,-50 8,-56 16,-58 C12,-52 10,-46 10,-42 C24,-36 34,-22 32,0 C32,16 24,28 12,34 L-12,34 C-24,28 -32,16 -32,0 Z"), P["PU"],
             H("M-32,0 C-34,-24 -20,-40 -2,-44 C-10,-34 -14,-18 -14,0 C-14,14 -12,26 -12,34 C-24,28 -32,16 -32,0 Z"), P["PUD"])
    c += ln(H("M0,-40 C2,-20 2,10 0,33"), P["PUD"], SW) + ln(H("M14,-34 C20,-20 22,0 18,26"), P["PUD"], IW + 0.6)
    c += part(H("M4,-42 C16,-40 26,-32 30,-18 C24,-28 14,-36 4,-42 Z"), P["PUL"], stroke=False)
    g["cabeca"] = c
    t = part("M112,118 C122,110 134,110 144,118 C150,134 148,152 146,168 L110,168 C108,152 106,134 112,118 Z", P["PU"],
             "M112,118 C118,112 124,110 128,110 C124,128 122,150 122,168 L110,168 C108,152 106,134 112,118 Z", P["PUD"])
    t += ln("M128,122 L128,160", P["PUD"], IW + 0.6)
    t += part("M100,122 C110,106 146,106 156,122 L154,136 L148,130 L144,142 L138,132 L132,144 L126,132 L120,143 L114,131 L108,140 L104,130 L101,136 Z", P["PU"],
              "M100,122 C106,112 116,108 126,107 C120,116 120,126 126,132 L120,143 L114,131 L108,140 L104,130 L101,136 Z", P["PUD"])
    t += part("M118,110 C128,106 138,106 146,112 C138,109 128,109 118,110 Z", P["PUL"], stroke=False)
    t += part("M108,159 L148,159 L148,168 L108,168 Z", P["LEA"], "M108,165 L148,165 L148,168 L108,168 Z", P["LEAD"])
    t += part("M100,160 L109,160 L109,174 L100,174 Z", P["LEAD"], swd=IW + 0.4)
    g["tronco"] = t
    q = part("M108,166 L148,166 C154,182 158,200 160,216 L154,211 L148,221 L142,212 L135,223 L128,213 L121,223 L114,212 L108,221 L102,211 L96,216 C98,200 102,182 108,166 Z", P["PU"],
             "M108,166 C102,182 98,200 96,216 L102,211 L108,221 L114,212 L121,223 C120,204 120,184 122,166 Z", P["PUD"])
    q += ln("M128,170 L128,208", P["PUD"], IW + 0.6) + ln("M140,170 C142,186 143,198 144,208", P["PUL"], IW + 0.4)
    g["quadril"] = q
    pernas_osso(J, g, P, costas=True)
    mb = braco_manga(J, "b", P["PU"], None, P["PUD"], w=9, lado=False)
    g["braco_sup_tras"] = seg(J["sh_b"], J["el_b"], 9, 9, P["PU"], P["PUD"])
    F, L = frame(J["el_b"], J["wr_b"])
    sl = [(0, -9), (L * 0.5, -11), (L + 3, -14), (L, -8), (L + 5, -4), (L + 1, 0), (L + 6, 4), (L + 1, 9), (L + 5, 13), (L - 3, 11), (L * 0.5, 10), (0, 9)]
    g["antebraco_tras"] = part(poly([F(u, v) for u, v in sl]), P["PU"], poly([F(u, v) for u, v in [(0, 3), (L * 0.5, 4), (L + 1, 9), (L + 5, 13), (L - 3, 11), (L * 0.5, 10), (0, 9)]]), P["PUD"])
    g["mao_tras"] = garra(J["wr_b"], P, P["BONE"], espelho=True)
    g["braco_sup_frente"] = seg(J["sh_f"], J["el_f"], 9, 9, P["PU"], P["PUD"], side=-1)
    F, L = frame(J["el_f"], J["wr_f"])
    sl = [(0, 9), (L * 0.5, 11), (L + 3, 14), (L, 8), (L + 5, 4), (L + 1, 0), (L + 6, -4), (L + 1, -9), (L + 5, -13), (L - 3, -11), (L * 0.5, -10), (0, -9)]
    g["antebraco_frente"] = part(poly([F(u, v) for u, v in sl]), P["PU"], poly([F(u, v) for u, v in [(0, 3), (L * 0.5, 4), (L + 1, 0), (L + 6, -4), (L + 1, -9), (L + 5, -13), (L - 3, -11), (L * 0.5, -10), (0, -9)]]), P["PUD"])
    g["mao_frente"] = punho(J["grip"], J["wr_f"], P, P["BONE"], P["BONED"], costas=True)
    x, top = J["grip"][0], 72
    a = cajado(x, top, P)
    a += part(poly([(x - 5, top + 4), (x + 5, top + 4), (x + 5, top + 11), (x - 5, top + 11)]), P["LEA"],
              poly([(x - 5, top + 8.5), (x + 5, top + 8.5), (x + 5, top + 11), (x - 5, top + 11)]), P["LEAD"], swd=IW + 0.4)
    sk = (x, top - 12)
    a += brilho(sk, 1, P)
    a += part(loc(sk, "M-8,6 L8,6 L7,15 L-7,15 Z"), P["SKGD"], swd=IW + 0.6)
    a += part(loc(sk, "M-11,0 C-11,-9 -6,-14 0,-14 C6,-14 11,-9 11,0 C11,6 7,10 0,10 C-7,10 -11,6 -11,0 Z"), P["SKG"],
              loc(sk, "M-11,0 C-11,-9 -6,-14 0,-14 C-4,-10 -6,-4 -6,2 C-6,6 -4,9 0,10 C-7,10 -11,6 -11,0 Z"), P["SKGD"], swd=IW + 0.6)
    a += ln(loc(sk, "M0,-13 C-1,-6 -1,2 0,8"), P["SKGD"], IW)
    g["arma"] = a
    return g

PERSONAGENS = {}

def registrar(nome, rotulo, lado, costas):
    PERSONAGENS[nome] = (rotulo, lado, costas)

registrar("necromante", "Necromante esqueleto", necro_lado, necro_costas)

# ================================================================== MEDUSA
PM = dict(SK="#c98b5a", SKD="#9c6a40", SKF="#b27a4e", SKFD="#8a5c36", G="#5aa844", GD="#2f6a2c", GL="#8fd06a", GB="#2a5a26",
          WH="#efe9d8", WHD="#c4bba0", GOLD="#d9a43a", GOLDD="#a5762a", PU="#6a4c8c", PUD="#46306a",
          WOOD="#6e4a2c", WOODD="#4a3020", EYEW="#f4f1e6", IRIS="#8be04a", LIP="#8e4040", RED="#d8305a", EYE="#0f1a0c")

def cobra_cabeca(c, s, P, flip=False, boca=True):
    """cabeça de cobra de perfil, ameaçadora (olho em fenda, boca aberta com presas)"""
    L = lambda d: loc(c, d, s, flip)
    o = ""
    if boca:
        o += ln(L("M10,3 L18,4 M18,4 L22,1 M18,4 L22,7"), P["RED"], 1.8 * s)
    o += part(L("M-12,-4 C-6,-10 6,-11 13,-5 L16,-1 L8,1 L15,4 C10,9 -4,9 -12,5 Z"), P["G"],
              L("M-12,1 C-4,4 6,4 15,4 C10,9 -4,9 -12,5 Z"), P["GD"], swd=IW + 0.6)
    o += part(L("M9,0.5 L12,1 L10,4 Z"), P["WH"], swd=0.8)
    o += part(L("M1,-6 L8,-5 L7,-2 C5,-1 2,-1 1,-3 Z"), "#e6e45a", swd=IW)
    o += ln(L("M4.5,-5.5 L4.5,-1.8"), P["EYE"], 1.4 * s)
    o += ln(L("M-1,-8 L9,-6"), OL, 1.8 * s)
    return o

def medusa_lado():
    P, J = PM, J_LADO
    g = {}
    hx, hy, hs = 144, 94, 0.8
    H = lambda d: loc((hx, hy), d, hs)
    c = part(H("M-34,-6 C-38,-30 -18,-44 4,-42 C22,-40 32,-28 30,-14 L20,-10 C10,-4 0,10 -6,30 C-14,40 -30,40 -38,30 C-44,18 -40,6 -34,-6 Z"), P["GD"])
    for d in ["M-30,-6 C-46,4 -50,24 -44,38 C-41,44 -34,42 -36,36", "M-20,10 C-34,26 -38,46 -30,60 C-26,66 -18,64 -20,58",
              "M-14,14 C-24,32 -24,48 -16,56 C-10,60 -4,56 -8,52"]:
        c += tube_cs(H(d), 9, P["G"], P["GD"], P["GB"])
    c += part(H("M2,-30 C18,-30 30,-18 31,-4 C32,0 34,4 35,7 C35,9 33,10 31,10 C31,14 30,18 27,22 C23,27 16,29 9,29 C-2,29 -10,22 -12,12 C-14,0 -10,-28 2,-30 Z"), P["SK"],
              H("M-12,12 C-10,22 -2,29 9,29 C4,24 0,14 -2,4 C-4,-6 -6,-14 -8,-20 C-12,-10 -13,2 -12,12 Z"), P["SKD"], swd=IW + 0.8)
    c += part(H("M-2,0 C-8,-6 -16,-12 -24,-14 C-20,-6 -12,4 -4,10 C0,10 2,4 -2,0 Z"), P["SK"], H("M-24,-14 C-18,-8 -10,0 -4,10 C-10,6 -16,0 -24,-14 Z"), P["SKD"], swd=IW + 0.6)
    c += ln(H("M-6,2 C-10,-2 -14,-6 -18,-9"), P["SKD"], IW)
    c += part(H("M-4,10 L-1,14 L-4,20 L-7,14 Z"), P["GOLD"], swd=IW)
    c += part(H("M-14,14 C-22,-10 -10,-36 10,-37 C24,-37 33,-27 34,-12 C27,-18 19,-20 12,-18 C6,-14 2,-6 -2,0 C-6,6 -8,12 -14,14 Z"), P["G"],
              H("M-14,14 C-22,-10 -14,-30 -2,-35 C-8,-26 -10,-12 -8,0 C-9,6 -11,10 -14,14 Z"), P["GD"], swd=IW + 0.8)
    for d in ["M-24,-24 C-30,-46 -6,-58 8,-50 C18,-44 14,-32 4,-34", "M4,-40 C14,-54 34,-52 38,-38 C40,-30 34,-26 30,-30",
              "M-6,-34 C10,-38 26,-30 32,-14"]:
        c += tube_cs(H(d), 9, P["G"], P["GD"], P["GB"])
    c += tube_cs(H("M8,-46 C10,-60 20,-68 30,-66"), 8, P["G"], P["GD"], P["GB"]) + cobra_cabeca((hx + 36 * hs, hy - 66 * hs), hs, P)
    c += tube_cs(H("M-34,-12 C-46,-16 -54,-10 -56,-2"), 8, P["G"], P["GD"], P["GB"]) + cobra_cabeca((hx - 62 * hs, hy - 2 * hs), hs, P, flip=True)
    c += ln(H("M10,-20 C18,-22 26,-19 31,-14"), P["GOLD"], 2.4) + part(H("M29,-18 L32,-14 L29,-10 L26,-14 Z"), P["GOLD"], swd=IW)
    c += part(H("M13,-8 C17,-11 23,-11 27,-7 C24,-3 18,-2 14,-5 Z"), P["EYEW"], swd=IW)
    c += circ(hx + 21 * hs, hy - 7 * hs, 3.1 * hs, P["IRIS"]) + part(H("M20.4,-9.5 L21.6,-9.5 L21.6,-4.5 L20.4,-4.5 Z"), P["EYE"], stroke=False)
    c += ln(H("M12,-8 C17,-12.5 24,-12.5 28,-7"), OL, 2.4) + ln(H("M12,-8 L8,-11"), OL, 1.8)
    c += ln(H("M14,-15 C19,-17.5 24,-16.5 28.5,-13"), P["GD"], 2.2)
    c += ln(H("M29,16 C30.5,15.5 32,16 33,15"), P["LIP"], 2.2) + ln(H("M27,14 L32,13.5"), OL, IW)
    g["cabeca"] = c
    t = part("M130,104 L142,104 L143,120 L129,120 Z", P["SK"], "M130,104 L135,104 L135,120 L129,120 Z", P["SKD"])
    t += part("M121,118 C130,112 142,114 148,124 C154,132 156,140 152,148 C150,156 148,162 146,168 L118,170 C114,152 114,132 121,118 Z", P["SK"],
              "M121,118 C125,132 127,150 128,169 L118,170 C114,152 114,132 121,118 Z", P["SKD"])
    t += part("M119,131 C130,127 146,127 155,135 C157,143 153,150 147,152 C136,153 126,151 118,148 Z", P["WH"],
              "M118,143 C128,146 140,147 154,144 C153,149 150,151 147,152 C136,153 126,151 118,148 Z", P["WHD"])
    t += part("M126,117 C133,122 142,122 147,117 L148,123 C141,128 132,128 126,123 Z", P["GOLD"], "M126,121 C133,125 141,125 148,121 L148,123 C141,128 132,128 126,123 Z", P["GOLDD"], swd=IW + 0.4)
    t += part("M116,160 L149,158 L150,166 L116,168 Z", P["GOLD"], "M116,164 L150,162.5 L150,166 L116,168 Z", P["GOLDD"])
    t += part("M141,157 L146,161.5 L141,166 L136,161.5 Z", "#3fbf8a", swd=IW)
    g["tronco"] = t
    q = part("M116,166 L149,164 C150,178 148,190 142,202 C136,214 132,224 128,232 L108,230 C104,210 108,186 116,166 Z", P["WH"],
             "M116,166 C110,186 106,206 108,230 L118,231 C116,208 118,186 124,166 Z", P["WHD"])
    q += ln("M108,230 L128,232", P["GOLD"], 3) + ln("M130,170 C130,190 128,208 124,226", P["WHD"], IW + 0.6)
    q += part("M140,166 L147,165 L151,192 L145,202 L139,190 Z", P["PU"], "M140,166 L143,165.5 L145,202 L139,190 Z", P["PUD"], swd=IW + 0.6)
    g["quadril"] = q
    for side, far in (("tras", True), ("frente", False)):
        B, BD = (P["SKF"], P["SKFD"]) if far else (P["SK"], P["SKD"])
        h, k, a = (J["hip_b"], J["kn_b"], J["an_b"]) if far else (J["hip_f"], J["kn_f"], J["an_f"])
        g["coxa_" + side] = seg(h, k, 5.5, 4.4, B, BD)
        g["canela_" + side] = seg(k, a, 4.4, 3, B, BD) + band(k, a, 0.62, 0.92, 4.4, P["GOLD"], P["GOLDD"])
        a2 = (a[0], 232)
        g["pe_" + side] = (part(loc(a2, "M-5,-3 L4,-3 C9,-1 15,2 19,5 L21,8 L-6,8 C-7,4 -6,0 -5,-3 Z"), B, loc(a2, "M-6,4 L19,5 L21,8 L-6,8 Z"), BD)
                           + part(loc(a2, "M-6,6 L21,6 L21,8.5 L-6,8.5 Z"), P["GOLDD"], swd=IW) + ln(loc(a2, "M2,-2 L8,4"), P["GOLD"], 1.6))
    for s, nome, far in (("b", "tras", True), ("f", "frente", False)):
        B, BD = (P["SKF"], P["SKFD"]) if far else (P["SK"], P["SKD"])
        g["braco_sup_" + nome] = seg(J["sh_" + s], J["el_" + s], 5, 4.2, B, BD) + band(J["sh_" + s], J["el_" + s], 0.3, 0.5, 5, P["GOLD"], P["GOLDD"])
        g["antebraco_" + nome] = seg(J["el_" + s], J["wr_" + s], 4, 3.2, B, BD) + band(J["el_" + s], J["wr_" + s], 0.55, 0.95, 4.2, P["GOLD"], P["GOLDD"])
    w = J["wr_b"]
    g["mao_tras"] = (part(loc(w, "M-3,-1 L4,-1 C6,3 6,8 4,11 L2,14 L-1,13 L-3,9 C-5,5 -5,2 -3,-1 Z"), P["SKF"], loc(w, "M-4,6 L5,6 C5,9 4,11 2,14 L-1,13 L-3,9 Z"), P["SKFD"], swd=IW + 0.6)
                     + ln(loc(w, "M0,8 L1,13 M3,7 L4,11"), OL, IW))
    g["mao_frente"] = punho(J["grip"], J["wr_f"], P, P["SK"], P["SKD"])
    x, top = J["grip"][0], 72
    a = cajado(x, top, P)
    a += tube_cs(f"M{x},{top+70} C{x+12},{top+64} {x+12},{top+54} {x},{top+50} C{x-12},{top+46} {x-12},{top+36} {x},{top+32} "
                 f"C{x+12},{top+26} {x+12},{top+14} {x+2},{top+8} C{x-4},{top+4} {x-4},{top-2} {x+2},{top-6}", 6, P["G"], P["GD"], P["GB"])
    a += cobra_cabeca((x + 8, top - 9), 1.15, P)
    g["arma"] = a
    return g

def medusa_costas():
    P, J = PM, J_COSTAS
    g = {}
    hx, hy, hs = 128, 94, 0.8
    H = lambda d: loc((hx, hy), d, hs)
    c = part(H("M-36,0 C-40,-28 -20,-44 0,-44 C20,-44 40,-28 36,0 C36,20 28,34 16,44 L-16,44 C-28,34 -36,20 -36,0 Z"), P["GD"])
    for sx in (1, -1):
        c += part(H(tp("M30,-2 C38,-8 46,-14 52,-18 C50,-10 44,0 32,8 Z", lambda x, y: (x * sx, y))), P["SK"],
                  H(tp("M32,4 C40,-2 46,-8 52,-18 C50,-10 44,0 32,8 Z", lambda x, y: (x * sx, y))), P["SKD"], swd=IW + 0.6)
        c += part(H(tp("M33,8 L36,12 L33,18 L30,12 Z", lambda x, y: (x * sx, y))), P["GOLD"], swd=IW)
    c += part(H("M-32,4 C-36,-24 -18,-40 0,-40 C18,-40 36,-24 32,4 C26,-6 14,-10 0,-10 C-14,-10 -26,-6 -32,4 Z"), P["G"],
              H("M-32,4 C-36,-24 -18,-40 0,-40 C-12,-32 -18,-20 -18,-8 C-24,-6 -28,-2 -32,4 Z"), P["GD"], swd=IW + 0.8)
    for d in ["M-26,0 C-34,18 -32,36 -24,50 C-20,56 -12,54 -14,48", "M-12,-6 C-16,14 -10,32 -14,52 C-16,60 -8,62 -6,56",
              "M2,-8 C0,12 6,32 2,54 C0,62 8,64 10,58", "M16,-6 C20,14 14,32 18,50 C20,58 28,56 26,50",
              "M28,0 C36,18 34,34 28,46 C25,52 18,50 20,44"]:
        c += tube_cs(H(d), 9, P["G"], P["GD"], P["GB"])
    for d in ["M-24,-24 C-30,-46 -6,-58 8,-50 C18,-44 14,-32 4,-34", "M24,-24 C30,-46 6,-58 -8,-50 C-18,-44 -14,-32 -4,-34",
              "M-12,-38 C-6,-50 6,-50 12,-38"]:
        c += tube_cs(H(d), 9, P["G"], P["GD"], P["GB"])
    c += tube_cs(H("M-30,-16 C-42,-22 -50,-18 -54,-10"), 8, P["G"], P["GD"], P["GB"]) + cobra_cabeca((hx - 60 * hs, hy - 10 * hs), hs, P, flip=True)
    c += tube_cs(H("M30,-16 C42,-22 50,-18 54,-10"), 8, P["G"], P["GD"], P["GB"]) + cobra_cabeca((hx + 60 * hs, hy - 10 * hs), hs, P)
    g["cabeca"] = c
    t = part("M122,104 L134,104 L135,120 L121,120 Z", P["SK"], "M122,104 L127,104 L127,120 L121,120 Z", P["SKD"])
    t += part("M112,118 C122,112 134,112 144,118 C149,134 148,152 145,168 L111,168 C108,152 107,134 112,118 Z", P["SK"],
              "M112,118 C117,114 122,113 126,113 C122,130 121,150 122,168 L111,168 C108,152 107,134 112,118 Z", P["SKD"])
    t += ln("M128,122 C127,134 127,146 128,158", P["SKD"], IW + 0.6)
    t += part("M110,131 L146,131 L147,143 L109,143 Z", P["WH"], "M109,139 L147,139 L147,143 L109,143 Z", P["WHD"])
    t += part("M120,117 C125,121 131,121 136,117 L137,122 C131,126 125,126 119,122 Z", P["GOLD"], swd=IW + 0.4)
    t += part("M110,159 L146,159 L146,167 L110,167 Z", P["GOLD"], "M110,164 L146,164 L146,167 L110,167 Z", P["GOLDD"])
    g["tronco"] = t
    q = part("M110,166 L146,166 C150,182 152,204 154,228 L102,228 C104,204 106,182 110,166 Z", P["WH"],
             "M110,166 C106,182 104,204 102,228 L114,228 C114,206 116,186 120,166 Z", P["WHD"])
    q += ln("M102,228 L154,228", P["GOLD"], 3) + ln("M128,170 L128,222", P["WHD"], IW + 0.6) + ln("M138,170 C140,190 142,206 143,222", P["WHD"], IW)
    q += part("M104,166 L111,166 L112,196 L107,204 L102,194 Z", P["PU"], "M104,166 L107,166 L107,204 L102,194 Z", P["PUD"], swd=IW + 0.6)
    g["quadril"] = q
    for side, far in (("tras", True), ("frente", False)):
        B, BD = (P["SKF"], P["SKFD"]) if far else (P["SK"], P["SKD"])
        h, k, a = (J["hip_b"], J["kn_b"], J["an_b"]) if far else (J["hip_f"], J["kn_f"], J["an_f"])
        g["coxa_" + side] = seg(h, k, 5.5, 4.4, B, BD)
        g["canela_" + side] = seg(k, a, 4.4, 3, B, BD) + band(k, a, 0.62, 0.92, 4.4, P["GOLD"], P["GOLDD"])
        a2 = (a[0], 232)
        g["pe_" + side] = part(loc(a2, "M-4,-3 L4,-3 C5,1 6,5 6,8 L-6,8 C-6,5 -5,1 -4,-3 Z"), B, loc(a2, "M-6,5 L6,5 L6,8 L-6,8 Z"), BD) + part(loc(a2, "M-6.5,6 L6.5,6 L6.5,8.5 L-6.5,8.5 Z"), P["GOLDD"], swd=IW)
    for s, nome, sd in (("b", "tras", 1), ("f", "frente", -1)):
        g["braco_sup_" + nome] = seg(J["sh_" + s], J["el_" + s], 5, 4.2, P["SK"], P["SKD"], side=sd) + band(J["sh_" + s], J["el_" + s], 0.3, 0.5, 5, P["GOLD"], P["GOLDD"])
        g["antebraco_" + nome] = seg(J["el_" + s], J["wr_" + s], 4, 3.2, P["SK"], P["SKD"], side=sd) + band(J["el_" + s], J["wr_" + s], 0.55, 0.95, 4.2, P["GOLD"], P["GOLDD"])
    w = J["wr_b"]
    g["mao_tras"] = part(loc(w, "M-3,-1 L4,-1 C6,3 6,8 4,11 L2,14 L-1,13 L-3,9 C-5,5 -5,2 -3,-1 Z", flip=True), P["SK"], loc(w, "M-4,6 L5,6 C5,9 4,11 2,14 L-1,13 L-3,9 Z", flip=True), P["SKD"], swd=IW + 0.6)
    g["mao_frente"] = punho(J["grip"], J["wr_f"], P, P["SK"], P["SKD"], costas=True)
    x, top = J["grip"][0], 74
    a = cajado(x, top, P)
    a += tube_cs(f"M{x},{top+70} C{x+12},{top+64} {x+12},{top+54} {x},{top+50} C{x-12},{top+46} {x-12},{top+36} {x},{top+32} "
                 f"C{x+12},{top+26} {x+12},{top+14} {x+1},{top+6} C{x-3},{top+2} {x-2},{top-4} {x},{top-6}", 6, P["G"], P["GD"], P["GB"])
    sk = (x, top - 12)
    a += part(loc(sk, "M-8,4 C-10,-4 -6,-10 0,-10 C6,-10 10,-4 8,4 C6,8 -6,8 -8,4 Z"), P["G"], loc(sk, "M-8,4 C-10,-4 -6,-10 0,-10 C-3,-6 -4,0 -2,7 C-5,7 -7,6 -8,4 Z"), P["GD"], swd=IW + 0.6)
    a += ln(loc(sk, "M-3,-6 L0,-2 L3,-6"), P["GB"], 1.4)
    g["arma"] = a
    return g

registrar("medusa", "Medusa", medusa_lado, medusa_costas)

# ================================================================== NINJA
PJ = dict(CL="#30303c", CLD="#1d1d26", CLF="#24242e", CLFD="#15151c", CLL="#50506a", MESH="#70707e", MESHD="#4a4a56",
          SK="#e2b48e", SKD="#b8865e", RED="#9a2a2e", REDD="#641a1e", STEEL="#c4c6d0", STEELD="#7e808c",
          GLOVE="#3c3c4a", GLOVED="#24242e", EYEW="#f4f1e6", IRIS="#2a2a30")

def kunai(G, ang, P, s=1.0):
    d = math.radians(ang)
    F, _ = frame(G, (G[0] + math.cos(d), G[1] + math.sin(d)))
    Q = lambda pts: poly([F(u * s, v * s) for u, v in pts])
    rc = F(-17 * s, 0)
    o = circ(rc[0], rc[1], 4.2 * s, "none") + f'<circle cx="{fmt(rc[0])}" cy="{fmt(rc[1])}" r="{fmt(4.2*s)}" fill="none" stroke="{OL}" stroke-width="{fmt(5.2*s)}"/>\n'
    o += f'<circle cx="{fmt(rc[0])}" cy="{fmt(rc[1])}" r="{fmt(4.2*s)}" fill="none" stroke="{P["STEEL"]}" stroke-width="{fmt(2.2*s)}"/>\n'
    o += part(Q([(-13, -2.6), (9, -2.6), (9, 2.6), (-13, 2.6)]), P["RED"], Q([(-13, 0.8), (9, 0.8), (9, 2.6), (-13, 2.6)]), P["REDD"], swd=IW + 0.4)
    o += ln(Q([(-9, -2.6), (-7, 2.6)])[:-2] + " " + Q([(-3, -2.6), (-1, 2.6)])[:-2] + " " + Q([(3, -2.6), (5, 2.6)])[:-2], P["REDD"], IW)
    o += part(Q([(8, -5), (11, -5), (11, 5), (8, 5)]), P["STEELD"], swd=IW + 0.4)
    o += part(Q([(11, 0), (17, -7), (44, 0), (17, 7)]), P["STEEL"], Q([(11, 0), (44, 0), (17, 7)]), P["STEELD"], swd=IW + 0.6)
    o += ln(Q([(14, 0), (40, 0)])[:-2], "#e8eaf2", IW)
    return o

def ninja_lado():
    P, J = PJ, J_LADO
    g = {}
    hx, hy, hs = 144, 96, 0.8
    H = lambda d: loc((hx, hy), d, hs)
    c = part(H("M-24,-8 C-40,-14 -52,-8 -66,-16 C-64,-8 -62,-2 -58,1 C-46,-1 -34,-1 -24,-1 Z"), P["RED"], H("M-24,-4 C-38,-4 -50,-2 -58,1 C-46,-1 -34,-1 -24,-1 Z"), P["REDD"])
    c += part(H("M-24,-3 C-36,4 -46,12 -62,14 C-58,19 -53,20 -49,20 C-38,14 -30,8 -22,2 Z"), P["REDD"])
    c += part(H("M2,-34 C20,-34 32,-20 32,-4 C32,4 31,8 33,12 C35,15 33,18 30,19 C28,26 20,32 8,32 C-8,32 -22,24 -26,8 C-30,-14 -16,-34 2,-34 Z"), P["CL"],
              H("M-26,8 C-30,-14 -16,-34 2,-34 C-10,-26 -14,-10 -12,6 C-10,18 -4,26 8,32 C-8,32 -22,24 -26,8 Z"), P["CLD"])
    c += part(H("M-6,-32 C6,-36 20,-32 28,-22 C18,-28 6,-32 -6,-32 Z"), P["CLL"], stroke=False)
    c += part(H("M10,-14 C20,-15 28,-12 32,-6 C33,-2 33,1 32,4 C24,5 16,4 10,2 C8,-3 8,-9 10,-14 Z"), P["SK"],
              H("M10,-14 C14,-14 16,-12 16,-8 C16,-3 14,1 10,2 C8,-3 8,-9 10,-14 Z"), P["SKD"], swd=IW + 0.6)
    c += part(H("M17,-8 L27,-6 L26,-2 C23,0 19,0 17,-3 Z"), P["EYEW"], swd=IW)
    c += circ(hx + 22.5 * hs, hy - 4 * hs, 2.2 * hs, P["IRIS"]) + circ(hx + 23.2 * hs, hy - 4.8 * hs, 0.7 * hs, "#ffffff")
    c += part(H("M14,-12 L29.5,-8.5 L29,-5.5 L15,-9 Z"), OL, stroke=False)
    c += ln(H("M10,2.5 C18,6 26,6 32,4"), OL, IW + 0.4)
    c += part(H("M-25,-10 C-8,-19 14,-21 32,-16 L32,-11 C14,-16 -8,-14 -25,-4 Z"), P["RED"], H("M-25,-6 C-8,-15 14,-17 32,-13 L32,-11 C14,-16 -8,-14 -25,-4 Z"), P["REDD"], swd=IW + 0.6)
    c += part(H("M-30,-6 C-30,-10 -22,-10 -22,-6 C-22,-1 -30,-1 -30,-6 Z"), P["REDD"], swd=IW + 0.4)
    g["cabeca"] = c
    t = part(poly([(98, 106), (104, 104), (110, 116), (104, 118)]), P["CLD"], swd=IW + 0.4)
    t += ln("M100,107.5 L106,116 M102.5,105.5 L108,114", P["RED"], 1.4)
    t += part(poly([(103, 117), (111, 113), (113, 116), (105, 120)]), P["STEELD"], swd=IW)
    t += part(poly([(106, 118), (111, 116), (130, 152), (125, 155)]), P["CLD"], swd=IW + 0.4) + band((108.5, 117), (127.5, 153.5), 0.35, 0.42, 3, P["RED"])
    t += part("M120,118 C132,108 150,112 155,126 C159,140 155,156 149,168 L117,170 C113,152 113,132 120,118 Z", P["CL"],
              "M120,118 C124,132 126,150 128,169 L117,170 C113,152 113,132 120,118 Z", P["CLD"])
    t += part("M139,113 L153,120 L145,134 Z", P["MESH"], "M139,113 L145,116 L145,134 Z", P["MESHD"], swd=IW)
    t += ln("M153,121 C147,136 141,148 135,160", P["CLL"], 2.4) + ln("M139,114 C137,124 136,132 135,138", P["CLD"], IW + 0.4)
    t += part("M116,160 L151,158 L152,167 L116,169 Z", P["RED"], "M116,164.5 L152,163 L152,167 L116,169 Z", P["REDD"])
    t += part("M110,160 L118,159 L119,169 L110,171 Z", P["REDD"], swd=IW + 0.4)
    t += part("M112,170 L108,186 L114,184 L117,170 Z", P["REDD"], swd=IW + 0.4)
    g["tronco"] = t
    q = part("M116,166 L151,164 C153,174 154,184 154,194 L145,190 L137,197 L127,192 L118,198 L112,190 C112,182 114,174 116,166 Z", P["CL"],
             "M116,166 C114,174 112,182 112,190 L118,198 L127,192 C124,184 123,174 124,166 Z", P["CLD"])
    q += ln("M137,168 L137,196", P["CLD"], IW + 0.4) + ln("M150,168 C151,178 152,186 152,192", P["CLL"], IW)
    g["quadril"] = q
    for side, far in (("tras", True), ("frente", False)):
        C, CD = (P["CLF"], P["CLFD"]) if far else (P["CL"], P["CLD"])
        h, k, a = (J["hip_b"], J["kn_b"], J["an_b"]) if far else (J["hip_f"], J["kn_f"], J["an_f"])
        g["coxa_" + side] = seg(h, k, 7.5, 6.5, C, CD)
        g["canela_" + side] = (seg(k, a, 6, 3.8, C, CD) + band(k, a, 0.35, 0.95, 4.8, P["MESH"] if not far else P["MESHD"], P["MESHD"] if not far else P["CLFD"])
                               + band(k, a, 0.5, 0.56, 4.9, CD) + band(k, a, 0.72, 0.78, 4.4, CD))
        a2 = (a[0], 232)
        g["pe_" + side] = (part(loc(a2, "M-5,-4 L5,-4 C10,-2 16,1 19,5 L20,8 L-6,8 C-7,4 -6,-1 -5,-4 Z"), CD, loc(a2, "M-6,5 L19.5,6 L20,8 L-6,8 Z"), P["CLFD"])
                           + ln(loc(a2, "M12,2.5 L12.5,7.5"), OL, IW))
    for s, nome, far in (("b", "tras", True), ("f", "frente", False)):
        C, CD = (P["CLF"], P["CLFD"]) if far else (P["CL"], P["CLD"])
        M, MD = (P["MESHD"], P["CLFD"]) if far else (P["MESH"], P["MESHD"])
        sh, el, wr = J["sh_" + s], J["el_" + s], J["wr_" + s]
        g["braco_sup_" + nome] = seg(sh, el, 6.5, 6, C, CD)
        g["antebraco_" + nome] = seg(el, wr, 5, 4, M, MD) + band(el, wr, 0.08, 0.2, 5.4, CD) + band(el, wr, 0.5, 0.58, 4.8, CD) + band(el, wr, 0.84, 0.94, 4.4, CD)
    w = J["wr_b"]
    g["mao_tras"] = (part(loc(w, "M-3,-1 L4,-1 C6,3 6,8 4,11 L2,14 L-1,13 L-3,9 C-5,5 -5,2 -3,-1 Z"), P["GLOVE"], loc(w, "M-4,6 L5,6 C5,9 4,11 2,14 L-1,13 L-3,9 Z"), P["GLOVED"], swd=IW + 0.6)
                     + ln(loc(w, "M0,8 L1,13 M3,7 L4,11"), OL, IW))
    g["arma"] = kunai(J["grip"], -28, P)
    g["mao_frente"] = punho(J["grip"], J["wr_f"], P, P["GLOVE"], P["GLOVED"])
    return g

def ninja_costas():
    P, J = PJ, J_COSTAS
    g = {}
    hx, hy, hs = 128, 96, 0.8
    H = lambda d: loc((hx, hy), d, hs)
    c = part(H("M0,-34 C20,-34 32,-20 32,0 C32,18 20,32 0,32 C-20,32 -32,18 -32,0 C-32,-20 -20,-34 0,-34 Z"), P["CL"],
             H("M-32,0 C-32,-20 -20,-34 0,-34 C-12,-26 -16,-12 -16,2 C-16,16 -10,26 0,32 C-20,32 -32,18 -32,0 Z"), P["CLD"])
    c += part(H("M4,-33 C16,-32 26,-24 30,-12 C22,-22 14,-28 4,-33 Z"), P["CLL"], stroke=False)
    c += ln(H("M0,-33 C-1,-16 -1,8 0,31"), P["CLD"], IW + 0.6) + ln(H("M14,-30 C20,-16 21,4 16,26"), P["CLD"], IW)
    c += part(H("M-32,-9 C-16,-15 16,-15 32,-9 L32,-3 C16,-9 -16,-9 -32,-3 Z"), P["RED"], H("M-32,-5 C-16,-11 16,-11 32,-5 L32,-3 C16,-9 -16,-9 -32,-3 Z"), P["REDD"], swd=IW + 0.6)
    c += part(H("M-2,-4 C-14,4 -28,12 -46,14 C-43,19 -39,21 -35,21 C-20,16 -8,8 2,0 Z"), P["RED"], H("M-2,-1 C-14,8 -26,14 -35,21 C-20,16 -8,8 2,0 Z"), P["REDD"])
    c += part(H("M2,-4 C-4,10 -10,24 -20,38 C-15,40 -11,40 -8,38 C0,26 4,12 6,-2 Z"), P["REDD"])
    c += part(H("M-5,-6 C-5,-11 5,-11 5,-6 C5,-1 -5,-1 -5,-6 Z"), P["REDD"], swd=IW + 0.4)
    g["cabeca"] = c
    t = part("M112,118 C122,110 134,110 144,118 C150,134 148,152 146,168 L110,168 C108,152 106,134 112,118 Z", P["CL"],
             "M112,118 C118,112 124,110 128,110 C124,128 122,150 122,168 L110,168 C108,152 106,134 112,118 Z", P["CLD"])
    t += ln("M128,120 L128,158", P["CLD"], IW + 0.6)
    t += part(poly([(140, 116), (145, 119), (122, 156), (117, 153)]), P["CLD"], swd=IW + 0.4) + band((142.5, 117.5), (119.5, 154.5), 0.32, 0.4, 3, P["RED"])
    t += part(poly([(141, 116), (149, 120), (147, 123), (139, 119)]), P["STEELD"], swd=IW)
    t += part(poly([(144, 119), (150, 108), (155, 111), (149, 121)]), P["CLD"], swd=IW + 0.4) + ln("M147,116 L152,110 M149,118 L154,112", P["RED"], 1.3)
    t += part("M108,159 L148,159 L148,168 L108,168 Z", P["RED"], "M108,164 L148,164 L148,168 L108,168 Z", P["REDD"])
    t += part("M128,163 C120,156 112,158 114,164 C116,170 122,168 128,165 C134,168 140,170 142,164 C144,158 136,156 128,163 Z", P["RED"], None, None, swd=IW + 0.4)
    t += part("M126,165 L122,182 L127,180 L129,166 Z", P["REDD"], swd=IW + 0.4) + part("M130,165 L134,181 L138,178 L132,165 Z", P["REDD"], swd=IW + 0.4)
    t += circ(128, 164, 2.6, P["REDD"], True)
    g["tronco"] = t
    q = part("M110,166 L146,166 C148,176 150,186 150,196 L140,192 L132,198 L124,192 L116,198 L106,194 C106,184 108,176 110,166 Z", P["CL"],
             "M110,166 C108,176 106,184 106,194 L116,198 L124,192 C122,184 121,176 122,166 Z", P["CLD"])
    q += ln("M128,170 L128,196", P["CLD"], IW + 0.4)
    g["quadril"] = q
    for side, far in (("tras", True), ("frente", False)):
        h, k, a = (J["hip_b"], J["kn_b"], J["an_b"]) if far else (J["hip_f"], J["kn_f"], J["an_f"])
        g["coxa_" + side] = seg(h, k, 7.5, 6.5, P["CL"], P["CLD"])
        g["canela_" + side] = (seg(k, a, 6, 3.8, P["CL"], P["CLD"]) + band(k, a, 0.35, 0.95, 4.8, P["MESH"], P["MESHD"])
                               + band(k, a, 0.5, 0.56, 4.9, P["CLD"]) + band(k, a, 0.72, 0.78, 4.4, P["CLD"]))
        a2 = (a[0], 232)
        g["pe_" + side] = part(loc(a2, "M-5,-4 L5,-4 C6,1 7,5 7,8 L-7,8 C-7,5 -6,1 -5,-4 Z"), P["CLD"], loc(a2, "M-7,5 L7,5 L7,8 L-7,8 Z"), P["CLFD"])
    for s, nome, sd in (("b", "tras", 1), ("f", "frente", -1)):
        sh, el, wr = J["sh_" + s], J["el_" + s], J["wr_" + s]
        g["braco_sup_" + nome] = seg(sh, el, 6.5, 6, P["CL"], P["CLD"], side=sd)
        g["antebraco_" + nome] = (seg(el, wr, 5, 4, P["MESH"], P["MESHD"], side=sd) + band(el, wr, 0.08, 0.2, 5.4, P["CLD"])
                                  + band(el, wr, 0.5, 0.58, 4.8, P["CLD"]) + band(el, wr, 0.84, 0.94, 4.4, P["CLD"]))
    w = J["wr_b"]
    g["mao_tras"] = part(loc(w, "M-3,-1 L4,-1 C6,3 6,8 4,11 L2,14 L-1,13 L-3,9 C-5,5 -5,2 -3,-1 Z", flip=True), P["GLOVE"],
                         loc(w, "M-4,6 L5,6 C5,9 4,11 2,14 L-1,13 L-3,9 Z", flip=True), P["GLOVED"], swd=IW + 0.6)
    g["arma"] = kunai(J["grip"], -62, P)
    g["mao_frente"] = punho(J["grip"], J["wr_f"], P, P["GLOVE"], P["GLOVED"], costas=True)
    return g

registrar("ninja", "Ninja", ninja_lado, ninja_costas)

def main():
    D = sys.argv[1] if len(sys.argv) > 1 else "."
    so = sys.argv[2:]  # opcional: nomes específicos
    for nome, (rot, fl, fc) in PERSONAGENS.items():
        if so and nome not in so:
            continue
        lado = montar(fl(), J_LADO, ORDEM_LADO, f"{rot} - estilo dark fantasy estilizado. Vista lateral, virado para a direita.")
        open(os.path.join(D, f"{nome}_estilizado_lado_separado.svg"), "w").write(lado)
        open(os.path.join(D, f"{nome}_estilizado_lado_esquerda_separado.svg"), "w").write(espelhar(lado))
        costas = montar(fc(), J_COSTAS, ORDEM_COSTAS, f"{rot} - estilo dark fantasy estilizado. Vista de COSTAS. "
                        "Partes *_frente = lado DIREITO do personagem (segura a arma), à direita da tela.")
        open(os.path.join(D, f"{nome}_estilizado_costas_separado.svg"), "w").write(costas)
        print(nome, "ok")

if __name__ == "__main__":
    main()
