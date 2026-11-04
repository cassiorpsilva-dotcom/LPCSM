#!/usr/bin/env python3
"""
Três "câmeras" de conceito (1920x1080) para comparar estilos de mapa, com os personagens na escala:
  1. lateral com paralaxe        previews/conceitos/camera_1_lateral.png
  2. diorama isométrico          previews/conceitos/camera_2_isometrica.png
  3. 3/4 com personagens de lado previews/conceitos/camera_3_tres_quartos.png
Uso: python3 tools/conceitos_camera.py
"""
import os, re, math, random, subprocess
from gerar_mapa_tiradentes import DEFS, R, Pth, L, C, E, TX, copa, araucaria_copa, OL, canteiro, banco, pombo

AQUI = os.path.dirname(os.path.abspath(__file__))
RAIZ = os.path.join(AQUI, "..")
OUT = os.path.join(RAIZ, "previews", "conceitos")
WD, HD = 1920, 1080

def personagem(arquivo, x, pe_y, altura, sombra=True):
    """insere um SVG de personagem (viewBox 256, pés em y=240) com o corpo medindo ~altura px"""
    svg = open(os.path.join(RAIZ, arquivo)).read()
    inner = svg[svg.index(">", svg.index("<svg")) + 1: svg.rindex("</svg>")]
    s = altura / 180
    o = E(x, pe_y, 62 * s, 9 * s, "#000000", 0, 0.32) if sombra else ""
    return o + (f'<svg x="{x - 128 * s:.1f}" y="{pe_y - 240 * s:.1f}" width="{256 * s:.1f}" height="{256 * s:.1f}" '
                f'viewBox="0 0 256 256" overflow="visible">{inner}</svg>\n')

def brilho(cx, cy, r, op=0.55, id_="luz"):
    return f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="url(#{id_})" opacity="{op}"/>\n'

EXTRA = """
<linearGradient id="ceu" x1="0" y1="0" x2="0" y2="1">
 <stop offset="0" stop-color="#161229"/><stop offset="0.45" stop-color="#3d2a5c"/><stop offset="0.75" stop-color="#9a5468"/><stop offset="1" stop-color="#e59a6c"/></linearGradient>
<linearGradient id="nevoa" x1="0" y1="0" x2="0" y2="1">
 <stop offset="0" stop-color="#e8d8f0" stop-opacity="0"/><stop offset="0.5" stop-color="#e8d8f0" stop-opacity="0.22"/><stop offset="1" stop-color="#e8d8f0" stop-opacity="0"/></linearGradient>
<radialGradient id="luz"><stop offset="0" stop-color="#ffd98a" stop-opacity="0.9"/><stop offset="0.35" stop-color="#ffb860" stop-opacity="0.35"/><stop offset="1" stop-color="#ff9a40" stop-opacity="0"/></radialGradient>
<radialGradient id="luzverde"><stop offset="0" stop-color="#b8ff8a" stop-opacity="0.8"/><stop offset="1" stop-color="#6ad04a" stop-opacity="0"/></radialGradient>
<radialGradient id="luzagua"><stop offset="0" stop-color="#9fe6ff" stop-opacity="0.7"/><stop offset="1" stop-color="#4ab0e0" stop-opacity="0"/></radialGradient>
<radialGradient id="vinheta" cx="0.5" cy="0.5" r="0.75"><stop offset="0.55" stop-color="#000" stop-opacity="0"/><stop offset="1" stop-color="#05030a" stop-opacity="0.85"/></radialGradient>
<radialGradient id="lua"><stop offset="0" stop-color="#fff1d8"/><stop offset="0.6" stop-color="#f6d2a0" stop-opacity="0.6"/><stop offset="1" stop-color="#f6d2a0" stop-opacity="0"/></radialGradient>
<filter id="blur8" x="-20%" y="-20%" width="140%" height="140%"><feGaussianBlur stdDeviation="8"/></filter>
<filter id="blur3"><feGaussianBlur stdDeviation="2.5"/></filter>
<linearGradient id="fundo_iso" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#2b2240"/><stop offset="1" stop-color="#120e1c"/></linearGradient>
<linearGradient id="chao_noite" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#1a1426" stop-opacity="0.55"/><stop offset="1" stop-color="#1a1426" stop-opacity="0.15"/></linearGradient>
"""

def cab():
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {WD} {HD}" width="{WD}" height="{HD}">\n'
            + DEFS.replace("</defs>", EXTRA + "</defs>"))

def hud(titulo):
    o = R(36, 32, 360, 96, "#120e1c", rx=18, sw=0, op=0.55)
    o += C(84, 80, 34, "#2a2140", 3) + C(84, 80, 26, "#e6e2c6", 0) + E(76, 78, 6, 5, "#1a1422") + E(92, 78, 6, 5, "#1a1422") + C(77, 78, 2, "#8be04a", 0) + C(91, 78, 2, "#8be04a", 0)
    o += R(132, 58, 236, 16, "#3a1a22", rx=8, sw=2) + R(134, 60, 180, 12, "#d8404c", rx=6, sw=0)
    o += R(132, 86, 236, 12, "#16301e", rx=6, sw=2) + R(134, 88, 130, 8, "#7fe05a", rx=4, sw=0)
    o += TX(WD / 2, 70, titulo, 34, "#f4e9d8") + L(f"M{WD/2-280},60 L{WD/2-170},60 M{WD/2+170},60 L{WD/2+280},60", "#f4e9d8", 2, 0.6)
    return o

# ================================================================== 1. LATERAL
def predio_silhueta(x, w, h, base, cor):
    return R(x, base - h, w, h, cor, sw=0) + Pth(f"M{x-6},{base-h} L{x+w/2},{base-h-28} L{x+w+6},{base-h} Z", cor, 0)

def araucaria_sil(x, base, h, cor, s=1.0):
    o = R(x - 3 * s, base - h, 6 * s, h, cor, sw=0)
    for i, (dy, rx) in enumerate([(0, 70), (22, 58), (42, 44), (58, 28)]):
        o += E(x, base - h + 10 * s - dy * s, rx * s, 13 * s, cor)
    return o

def lampiao(x, base, h=300, s=1.0):
    o = R(x - 6 * s, base - h, 12 * s, h, "#1c1824", rx=3, sw=2) + R(x - 16 * s, base - 14 * s, 32 * s, 16 * s, "#1c1824", rx=3, sw=2)
    y = base - h
    o += Pth(f"M{x-18*s},{y} L{x+18*s},{y} L{x+13*s},{y-38*s} L{x-13*s},{y-38*s} Z", "#ffe2a0", 2.5)
    o += Pth(f"M{x-22*s},{y-38*s} L{x+22*s},{y-38*s} L{x},{y-58*s} Z", "#1c1824", 2.5) + R(x - 20 * s, y - 4 * s, 40 * s, 8 * s, "#1c1824", sw=2)
    return o, (x, y - 20 * s)

def cena_lateral():
    o = cab() + R(0, 0, WD, HD, "url(#ceu)", sw=0)
    o += C(1460, 330, 220, "url(#lua)", 0, 0.55) + C(1460, 330, 70, "#fbe6c4", 0, 0.9)
    rnd = random.Random(3)
    for _ in range(60):
        o += C(rnd.randint(0, WD), rnd.randint(0, 420), round(rnd.random() * 1.6 + 0.4, 1), "#ffffff", 0, round(rnd.random() * 0.5 + 0.2, 2))
    far = "#3a2b52"
    base = 790
    x = -40
    while x < WD:
        w, h = rnd.randint(70, 150), rnd.randint(90, 230)
        o += predio_silhueta(x, w, h, base, "#2f2445")
        x += w + rnd.randint(-10, 20)
    o += R(250, base - 200, 300, 200, far, sw=0) + R(250, base - 290, 70, 290, far, sw=0) + R(480, base - 290, 70, 290, far, sw=0)
    o += Pth(f"M244,{base-290} L326,{base-290} L285,{base-440} Z", far, 0) + Pth(f"M474,{base-290} L556,{base-290} L515,{base-440} Z", far, 0)
    o += Pth(f"M320,{base-200} L480,{base-200} L400,{base-270} Z", far, 0)
    for ax, ah in ((700, 230), (1120, 260), (1700, 210), (110, 200)):
        o += araucaria_sil(ax, base, ah, far, 1.0)
    for wx in range(30, WD, 47):
        if rnd.random() < 0.35:
            o += R(wx, base - rnd.randint(40, 170), 6, 8, "#ffcf7a", sw=0, op=0.7)
    o += R(0, 640, WD, 220, "url(#nevoa)", sw=0)
    # casario do meio
    cores = ["#8a6e4e", "#4e5f7e", "#8a5a66", "#567a66", "#8a7f62", "#6a4e7a"]
    x, i = -30, 0
    base2 = 868
    while x < WD:
        w, h = rnd.randint(150, 230), rnd.randint(200, 300)
        cor = cores[i % len(cores)]; i += 1
        o += R(x, base2 - h, w, h, cor, sw=2.5) + R(x, base2 - h, w, 16, "#2c2236", sw=2)
        if i % 2:
            o += Pth(f"M{x-8},{base2-h} L{x+w/2},{base2-h-50} L{x+w+8},{base2-h} Z", "#6e3a30", 2.5)
        for fy in (base2 - h + 50, base2 - h + 140):
            for fx in range(x + 24, x + w - 40, 62):
                lit = rnd.random() < 0.55
                o += R(fx, fy, 34, 52, "#ffcf7a" if lit else "#2a2440", rx=3, sw=2)
                if lit:
                    o += R(fx, fy, 34, 52, "#ffffff", rx=3, sw=0, op=0.15) + L(f"M{fx+17},{fy} L{fx+17},{fy+52}", "#8a6440", 2)
        x += w
    o += R(0, 560, WD, 320, "#2a1f40", sw=0, op=0.38)
    o += R(0, 700, WD, 200, "url(#nevoa)", sw=0, op=0.8)
    # chão jogável
    o += R(0, 866, WD, 44, "url(#calcada)", sw=0) + R(0, 866, WD, 44, "#2a1f40", sw=0, op=0.35) + R(0, 906, WD, 10, "#6b6474", sw=2)
    o += R(0, 914, WD, 170, "url(#pedra)", sw=0) + R(0, 914, WD, 170, "url(#chao_noite)", sw=0)
    # Igreja da Ordem
    ig = "#d8d0cc"; igs = "#a99fae"; tri = "#c9a45a"
    o += R(70, 470, 140, 440, ig) + R(70, 470, 26, 440, igs, sw=0) + Pth("M60,474 L220,474 L140,380 Z", "#6e3a30") + L("M140,380 L140,352", OL, 5) + C(140, 350, 6, "#d9a43a", 2)
    o += Pth("M112,620 L112,560 Q112,530 140,522 Q168,530 168,560 L168,620 Z", "#2a2440") + Pth("M124,590 Q140,570 156,590 L156,606 L124,606 Z", "#d9a43a", 2)
    o += R(210, 600, 380, 310, ig) + R(210, 600, 26, 310, igs, sw=0) + R(210, 600, 380, 14, tri, sw=2) + R(210, 896, 380, 14, tri, sw=2)
    o += Pth("M250,602 L550,602 L400,500 Z", ig) + Pth("M286,598 L514,598 L400,528 Z", "#c4bcc0", 2) + L("M400,500 L400,466 M386,480 L414,480", OL, 6) + L("M400,500 L400,466 M386,480 L414,480", "#d9a43a", 3)
    for px_ in (210, 300, 500, 580):
        o += R(px_, 612, 12, 286, tri, sw=2)
    o += Pth("M354,910 L354,800 Q354,760 400,748 Q446,760 446,800 L446,910 Z", tri) + Pth("M364,910 L364,804 Q364,770 400,760 Q436,770 436,804 L436,910 Z", "#ffcf7a")
    o += Pth("M364,910 L364,804 Q364,770 400,760 L400,910 Z", "#ffe7b0", 0, 0.6) + brilho(400, 860, 140, 0.4)
    for wx in (246, 520):
        o += Pth(f"M{wx},{770} L{wx},{700} Q{wx},{676} {wx+22},{670} Q{wx+44},{676} {wx+44},{700} L{wx+44},{770} Z", "#ffcf7a") + L(f"M{wx+22},{672} L{wx+22},{770}", "#8a6440", 2)
    # Cavalo Babão
    hx = 1690
    o += Pth(f"M{hx-120},912 L{hx-120},700 Q{hx-120},640 {hx-60},636 L{hx+60},636 Q{hx+120},640 {hx+120},700 L{hx+120},912 Z", "#8a8490") + R(hx - 120, 660, 26, 252, "#6e6876", sw=0)
    o += L(f"M{hx-112},760 L{hx+112},760 M{hx-112},840 L{hx+112},840", "#6e6876", 4)
    s = 2.2
    def H(d):
        return re.sub(r'(-?\d+(?:\.\d+)?),(-?\d+(?:\.\d+)?)', lambda m: f"{hx + float(m.group(1)) * s:.1f},{730 + float(m.group(2)) * s:.1f}", d)
    o += Pth(H("M-26,-26 C-30,-48 -14,-56 -4,-44 L6,-50 C14,-46 24,-34 22,-12 C20,8 16,30 10,44 C4,54 -12,54 -16,42 C-22,24 -24,0 -26,-26 Z"), "#8a6a3e", 3)
    o += Pth(H("M-26,-26 C-24,0 -22,24 -16,42 C-12,50 -4,52 2,50 C-6,30 -12,2 -14,-30 Z"), "#5e4628", 0)
    o += Pth(H("M-22,-34 L-28,-58 L-12,-44 Z"), "#8a6a3e", 3) + Pth(H("M2,-44 L4,-66 L14,-44 Z"), "#8a6a3e", 3)
    o += Pth(H("M-12,-18 L-1,-14 L-2,-10 L-12,-12 Z"), "#1e1a24", 0) + Pth(H("M16,-18 L5,-14 L6,-10 L16,-12 Z"), "#1e1a24", 0)
    o += C(hx - 13, 700, 3, "#b8ff8a", 0) + C(hx + 22, 700, 3, "#b8ff8a", 0)
    o += Pth(f"M{hx-6},846 C{hx-9},866 {hx-4},884 {hx-7},904 L{hx+7},904 C{hx+4},884 {hx+9},866 {hx+6},846 Z", "#9fe6ff", 2)
    o += R(hx - 150, 880, 300, 64, "#a49daa", rx=14) + R(hx - 134, 892, 268, 34, "#4aa0c8", rx=10, sw=2) + brilho(hx, 905, 170, 0.55, "luzagua")
    o += L(f"M{hx-110},908 C{hx-90},900 {hx-70},914 {hx-50},906 M{hx+30},912 C{hx+50},904 {hx+70},918 {hx+90},910", "#d8f6ff", 3)
    # postes
    for lx in (660, 1330):
        p, (gx, gy) = lampiao(lx, 912)
        o += p + brilho(gx, gy, 220, 0.6)
    # personagens (altura de corpo ~250 px)
    o += personagem("ninja_estilizado_lado_separado.svg", 780, 996, 250)
    o += personagem("medusa_estilizado_lado_separado.svg", 1010, 996, 250)
    o += personagem("cachorro_zumbi_estilizado_lado_esquerda_separado.svg", 1270, 1000, 175)
    o += personagem("necromante_estilizado_lado_esquerda_separado.svg", 1480, 996, 250)
    o += brilho(1430, 680, 120, 0.5, "luzverde")
    # primeiro plano desfocado
    fg = '<g filter="url(#blur8)">' + E(80, 1080, 260, 120, "#0c0914") + E(330, 1100, 200, 90, "#120e1c") + R(1846, 300, 40, 800, "#0c0914", sw=0) + \
         E(1866, 300, 70, 40, "#0c0914") + E(1700, 1100, 300, 90, "#0c0914") + "</g>\n"
    o += fg
    for _ in range(26):
        x, y = rnd.randint(500, 1800), rnd.randint(500, 950)
        o += C(x, y, 7, "#ffd98a", 0, 0.12) + C(x, y, 2, "#ffe7b0", 0, 0.8)
    o += R(0, 0, WD, HD, "url(#vinheta)", sw=0)
    o += hud("LARGO DA ORDEM")
    return o + "</svg>\n"

# ================================================================== 2. ISOMÉTRICA
A, OX, OY = 0.72, 960, 300
def P(x, y, z=0):
    return (OX + A * (x - y), OY + A / 2 * (x + y) - A * z)
def pts(*ps):
    return "M" + " L".join(f"{p[0]:.1f},{p[1]:.1f}" for p in ps) + " Z"

def caixa(x0, y0, x1, y1, h, topo, esq, dir_, sw=3):
    o = Pth(pts(P(x0, y1, 0), P(x1, y1, 0), P(x1, y1, h), P(x0, y1, h)), esq, sw)
    o += Pth(pts(P(x1, y0, 0), P(x1, y1, 0), P(x1, y1, h), P(x1, y0, h)), dir_, sw)
    o += Pth(pts(P(x0, y0, h), P(x1, y0, h), P(x1, y1, h), P(x0, y1, h)), topo, sw)
    return o

def face_y(y0, conteudo):
    """desenha em coordenadas (u=x, v=altura) na face de frente y=y0"""
    return f'<g transform="matrix({A},{A/2},0,{-A},{OX - A*y0},{OY + A/2*y0})">{conteudo}</g>\n'

def face_x(x0, conteudo):
    """desenha em coordenadas (u=y, v=altura) na face lateral x=x0"""
    return f'<g transform="matrix({-A},{A/2},0,{-A},{OX + A*x0},{OY + A/2*x0})">{conteudo}</g>\n'

def piramide(x0, y0, x1, y1, h, hp, c1, c2):
    ap = P((x0 + x1) / 2, (y0 + y1) / 2, h + hp)
    return Pth(pts(P(x0, y1, h), P(x1, y1, h), ap), c1) + Pth(pts(P(x1, y0, h), P(x1, y1, h), ap), c2)

def bill_arvore(x, y, kind):
    sx, sy = P(x, y)
    o = E(sx + 18, sy + 6, 70, 26, "#000000", 0, 0.28) + R(sx - 7, sy - 80, 14, 82, "#6b4a2e", rx=4)
    if kind == "araucaria":
        o += R(sx - 6, sy - 170, 12, 172, "#6b4a2e", rx=4) + araucaria_copa(sx, sy - 200)
    else:
        cor = ("#e9c23c", "#c99a22", "#f7e07a") if kind == "ipe" else ("#4f8a3e", "#33602a", "#79b05a")
        o += copa(sx, sy - 110, 52, *cor)
    return o

def bill_poste(x, y):
    sx, sy = P(x, y)
    p, (gx, gy) = lampiao(sx, sy, 150, 0.6)
    return E(sx, sy + 2, 16, 6, "#000", 0, 0.3) + p + brilho(gx, gy, 120, 0.45)

def cena_iso():
    o = cab() + R(0, 0, WD, HD, "url(#fundo_iso)", sw=0)
    rnd = random.Random(7)
    for _ in range(40):
        o += C(rnd.randint(0, WD), rnd.randint(0, HD), rnd.randint(30, 120), "#3d2a5c", 0, 0.08)
    # laje do diorama
    o += Pth(pts(P(0, 1000, 0), P(1000, 1000, 0), P(1000, 1000, -60), P(0, 1000, -60)), "#4a3b32")
    o += Pth(pts(P(1000, 0, 0), P(1000, 1000, 0), P(1000, 1000, -60), P(1000, 0, -60)), "#3a2d26")
    o += L(pts(P(0, 1000, -30), P(1000, 1000, -30), P(1000, 0, -30))[:-2], "#2e231e", 2)
    chao = R(0, 0, 1000, 1000, "url(#petit)", sw=0)
    chao += R(0, 0, 1000, 240, "url(#grama)", sw=0)
    chao += Pth("M860,0 L1000,0 L1000,1000 L860,1000 Z", "url(#pedra)", 0) + L("M860,0 L860,1000", "#5e564f", 5)
    chao += Pth("M0,240 L180,240 L180,1000 L0,1000 Z", "url(#calcada)", 0)
    chao += Pth("M260,330 C340,290 450,300 470,380 C490,460 420,520 330,520 C250,520 210,420 260,330 Z", "url(#grama)", 4)
    chao += Pth("M620,640 C700,600 820,620 830,710 C840,800 760,860 670,850 C590,840 560,700 620,640 Z", "url(#grama)", 4)
    chao += Pth("M260,700 C300,660 380,660 400,720 C420,790 360,840 300,830 C240,820 220,740 260,700 Z", "url(#grama)", 4)
    chao += C(560, 540, 70, "#a49d90", 4) + C(560, 540, 52, "#bdb6a8", 3)
    random.seed(5)
    for _ in range(90):
        fx, fy = random.choice([(360, 410, 90), (720, 740, 100), (320, 760, 60)])[:2]
        r = random.random() * 80
        a = random.random() * 6.28
        chao += C(round(fx + r * math.cos(a), 1), round(fy + r * 0.8 * math.sin(a), 1), 4, random.choice(["#e8505b", "#f4efe2", "#f2c84b", "#c26be0"]), 1.2)
    chao += R(500, 640, 160, 50, "#4e4a46", rx=6) + R(508, 646, 144, 38, "url(#pedra)", sw=0) + R(508, 646, 144, 38, "#bfe3f0", sw=2, op=0.35)
    o += f'<g transform="matrix({A},{A/2},{-A},{A/2},{OX},{OY})">{chao}</g>\n'
    objs = []
    # catedral (fundo)
    cat = caixa(300, 60, 640, 220, 170, "url(#ardosia)", "#d9d1c1", "#b8af9e")
    for tx in (300, 560):
        cat += caixa(tx, 150, tx + 80, 236, 300, "#c4bba8", "#e2dbcc", "#c4bba8") + piramide(tx, 150, tx + 80, 236, 300, 170, "#5e6472", "#4a4f5c")
    win = ""
    for cx in (340, 600):
        for v0 in (150, 230):
            win += R(cx - 12, v0, 24, 46, "#2e3c5c", rx=10, sw=2)
        win += R(cx - 14, 0, 28, 50, "#5a3b24", rx=10, sw=2)
    cat += face_y(236, win)
    door = R(440, 0, 60, 90, "#5a3b24", rx=24, sw=3) + C(470, 128, 26, "#2e3c5c", 3) + C(470, 128, 8, "#d9a43a", 2)
    cat += face_y(220, door)
    objs.append((280, cat))
    # casario (lado esquerdo, fachada virada para +x)
    cores = [("#e2b85a", "#c49a44"), ("#6a95b8", "#4f7a9c"), ("#d48a8a", "#b46e6e"), ("#7fae8a", "#62907a"), ("#e6d8b8", "#c8b994"), ("#b98ac9", "#9a6eab")]
    for k, y0 in enumerate(range(280, 1000, 120)):
        cf, cl = cores[k % len(cores)]
        h = 120 + (k * 37) % 60
        c = caixa(30, y0, 170, y0 + 116, h, "url(#telha)", cl, cf)
        det = R(y0 + 44, 0, 28, 60, "#5a3b24", rx=3, sw=2) + R(y0 + 10, 70, 24, 30, "#2e3c5c", sw=2) + R(y0 + 82, 70, 24, 30, "#2e3c5c", sw=2)
        c += face_x(170, det)
        objs.append((170 + y0 + 116, c))
    for (x, y, k) in ((760, 160, "araucaria"), (920, 120, "verde"), (360, 410, "ipe"), (720, 740, "araucaria"), (320, 760, "verde"), (950, 600, "ipe")):
        objs.append((x + y, bill_arvore(x, y, k)))
    for (x, y) in ((470, 470), (660, 470), (470, 620), (840, 860)):
        objs.append((x + y, bill_poste(x, y)))
    for (x, y) in ((420, 600), (700, 520)):
        sx, sy = P(x, y)
        objs.append((x + y, banco(sx - 40, sy - 20)))
    sx, sy = P(560, 540)
    objs.append((1100, Pth(f"M{sx-14},{sy} L{sx+14},{sy} L{sx+9},{sy-60} L{sx-9},{sy-60} Z", "#d9d1c1") + Pth(f"M{sx-12},{sy-58} L{sx+12},{sy-58} L{sx},{sy-74} Z", "#c4bba8")))
    for arq, (x, y), hgt in (("ninja_estilizado_lado_separado.svg", (520, 720), 135), ("medusa_estilizado_lado_separado.svg", (610, 760), 135),
                             ("cachorro_zumbi_estilizado_lado_esquerda_separado.svg", (780, 560), 95), ("necromante_estilizado_lado_esquerda_separado.svg", (860, 640), 135)):
        sx, sy = P(x, y)
        objs.append((x + y + 1, personagem(arq, sx, sy, hgt)))
    for _, s in sorted(objs, key=lambda t: t[0]):
        o += s
    o += f'<g filter="url(#blur3)">' + pombo(*P(600, 860)) + "</g>"
    o += R(0, 0, WD, HD, "url(#vinheta)", sw=0, op=0.8)
    o += hud("PRAÇA TIRADENTES")
    return o + "</svg>\n"

# ================================================================== 3. TRÊS QUARTOS (billboard)
def fachada(x, base, w, h, cor, cor_d, letreiro=None, rnd=None):
    o = R(x, base - h, w, h, cor) + R(x, base - h, 14, h, cor_d, sw=0) + R(x - 6, base - h - 30, w + 12, 34, "url(#telha)")
    o += R(x, base - h + 4, w, 8, "#f4efe2", sw=0, op=0.6)
    for fx in range(int(x + 22), int(x + w - 50), 70):
        lit = rnd.random() < 0.5
        o += R(fx, base - h + 30, 40, 58, "#ffcf7a" if lit else "#2e3c5c", rx=4, sw=2.5) + L(f"M{fx+20},{base-h+30} L{fx+20},{base-h+88}", "#efe6d2", 2.5)
        o += R(fx - 8, base - h + 30, 8, 58, "#3f7a52", sw=2) + R(fx + 40, base - h + 30, 8, 58, "#3f7a52", sw=2)
    o += R(x + w / 2 - 22, base - 78, 44, 78, "#5a3b24", rx=6) + C(x + w / 2 + 12, base - 38, 3, "#d9a43a", 0)
    if letreiro:
        lw = len(letreiro) * 13 + 24
        o += R(x + w / 2 - lw / 2, base - 112, lw, 26, "#3a2a20", rx=4, sw=2) + TX(x + w / 2, base - 93, letreiro, 17)
    return o

def cena_34():
    rnd = random.Random(11)
    o = cab() + R(0, 0, WD, HD, "url(#pedra)", sw=0)
    o += Pth("M0,330 L1920,330 L1920,420 L0,420 Z", "url(#calcada)", 0)
    o += Pth("M140,720 C260,640 520,620 700,700 C860,770 1040,760 1180,700 C1360,620 1600,660 1760,760 C1860,820 1920,880 1920,880 "
             "L1920,1080 L0,1080 L0,800 C40,770 90,750 140,720 Z", "url(#petit)", 4)
    o += Pth("M80,880 C160,820 300,830 340,900 C380,980 280,1040 180,1030 C80,1020 30,940 80,880 Z", "url(#grama)", 4)
    o += Pth("M1500,860 C1600,820 1760,840 1790,920 C1820,1000 1700,1060 1600,1050 C1500,1040 1440,920 1500,860 Z", "url(#grama)", 4)
    for _ in range(14):
        x, y = rnd.randint(450, 1450), rnd.randint(470, 690)
        o += E(x, y, rnd.randint(30, 70), rnd.randint(10, 18), "#3e5a72", 0, 0.35)
    for _ in range(50):
        x, y = rnd.randint(0, WD), rnd.randint(430, 1080)
        o += Pth(f"M{x},{y} l8,-4 l4,6 l-8,4 Z", rnd.choice(["#c9a43a", "#a8553a", "#7e3b28"]), 0, 0.8)
    objs = []
    cores = [("#e2b85a", "#c49a44"), ("#6a95b8", "#4f7a9c"), ("#d48a8a", "#b46e6e"), ("#7fae8a", "#62907a"), ("#e6d8b8", "#c8b994"), ("#b98ac9", "#9a6eab")]
    x, k = -40, 0
    letreiros = {1: "CAFÉ", 3: "LIVROS", 5: "BAR"}
    while x < WD:
        w = rnd.randint(220, 300)
        cf, cd = cores[k % len(cores)]
        objs.append((340, fachada(x, 340, w, 260, cf, cd, letreiros.get(k), rnd)))
        x += w; k += 1
    # chafariz do Cavalo Babão (billboard)
    hx, base = 1400, 610
    fb = E(hx, base + 8, 170, 26, "#000", 0, 0.3)
    fb += Pth(f"M{hx-90},{base-20} L{hx-90},{base-220} Q{hx-90},{base-260} {hx-46},{base-262} L{hx+46},{base-262} Q{hx+90},{base-260} {hx+90},{base-220} L{hx+90},{base-20} Z", "#9a948a")
    s = 1.6
    def H(d):
        return re.sub(r'(-?\d+(?:\.\d+)?),(-?\d+(?:\.\d+)?)', lambda m: f"{hx + float(m.group(1)) * s:.1f},{base - 170 + float(m.group(2)) * s:.1f}", d)
    fb += Pth(H("M-26,-26 C-30,-48 -14,-56 -4,-44 L6,-50 C14,-46 24,-34 22,-12 C20,8 16,30 10,44 C4,54 -12,54 -16,42 C-22,24 -24,0 -26,-26 Z"), "#8a6a3e")
    fb += Pth(H("M-26,-26 C-24,0 -22,24 -16,42 C-12,50 -4,52 2,50 C-6,30 -12,2 -14,-30 Z"), "#5e4628", 0)
    fb += Pth(H("M-22,-34 L-28,-58 L-12,-44 Z"), "#8a6a3e") + Pth(H("M2,-44 L4,-66 L14,-44 Z"), "#8a6a3e")
    fb += Pth(H("M-12,-18 L-1,-14 L-2,-10 L-12,-12 Z"), "#1e1a24", 0) + Pth(H("M16,-18 L5,-14 L6,-10 L16,-12 Z"), "#1e1a24", 0)
    fb += Pth(f"M{hx-5},{base-90} C{hx-7},{base-70} {hx-3},{base-50} {hx-5},{base-36} L{hx+5},{base-36} C{hx+3},{base-50} {hx+7},{base-70} {hx+5},{base-90} Z", "#9fe6ff", 2)
    fb += R(hx - 120, base - 56, 240, 60, "#a49d90", rx=14) + R(hx - 104, base - 46, 208, 30, "#4aa0c8", rx=10, sw=2) + brilho(hx, base - 30, 140, 0.45, "luzagua")
    fb += R(hx - 60, base - 130, 120, 22, "#3a2a20", rx=4, sw=2) + TX(hx, base - 114, "CAVALO BABÃO", 13)
    objs.append((base, fb))
    for (x, y, kk, sc) in ((300, 560, "araucaria", 1.0), (1720, 600, "ipe", 1.0), (200, 960, "verde", 1.15), (1640, 980, "ipe", 1.15), (980, 520, "verde", 0.95)):
        t = E(x + 20, y + 6, 80 * sc, 22 * sc, "#000", 0, 0.28) + R(x - 8 * sc, y - 90 * sc, 16 * sc, 92 * sc, "#6b4a2e", rx=4)
        if kk == "araucaria":
            t += R(x - 7, y - 220, 14, 222, "#6b4a2e", rx=4) + araucaria_copa(x, y - 250)
        else:
            cor = ("#e9c23c", "#c99a22", "#f7e07a") if kk == "ipe" else ("#4f8a3e", "#33602a", "#79b05a")
            t += copa(x, y - 140 * sc, 64 * sc, *cor)
        objs.append((y, t))
    for (x, y) in ((560, 520), (1180, 520), (520, 990)):
        p, (gx, gy) = lampiao(x, y, 220, 0.85)
        objs.append((y, E(x, y + 3, 20, 7, "#000", 0, 0.3) + p + brilho(gx, gy, 180, 0.5)))
    objs.append((800, banco(640, 770, 110)))
    objs.append((640, pombo(1020, 640) + pombo(1046, 650, -1)))
    for arq, x, y, hgt in (("ninja_estilizado_lado_separado.svg", 700, 700, 150), ("medusa_estilizado_lado_separado.svg", 900, 760, 155),
                           ("cachorro_zumbi_estilizado_lado_esquerda_separado.svg", 1160, 690, 108), ("necromante_estilizado_lado_esquerda_separado.svg", 1260, 820, 158)):
        objs.append((y, personagem(arq, x, y, hgt)))
    for _, s_ in sorted(objs, key=lambda t: t[0]):
        o += s_
    o += R(0, 0, WD, HD, "#1a1430", sw=0, op=0.18) + R(0, 0, WD, HD, "url(#vinheta)", sw=0, op=0.9)
    o += hud("RUA CLAUDINO DOS SANTOS")
    return o + "</svg>\n"

def main():
    os.makedirs(OUT, exist_ok=True)
    js = os.path.join(AQUI, "svg_para_png.js")
    for nome, fn in (("camera_1_lateral", cena_lateral), ("camera_2_isometrica", cena_iso), ("camera_3_tres_quartos", cena_34)):
        f = os.path.join(OUT, nome + ".svg")
        open(f, "w").write(fn())
        subprocess.run(["node", js, f, os.path.join(OUT, nome + ".png")], check=True)
        print(nome, "ok")

if __name__ == "__main__":
    main()
