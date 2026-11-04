#!/usr/bin/env python3
"""
Protótipo navegável (HTML) no estilo "3/4 com personagens de lado":
Catedral (Praça Tiradentes) -> Rua Claudino dos Santos -> Largo da Ordem (Cavalo Babão).

Uso: python3 tools/gerar_prototipo.py
Gera:
  prototipo/index.html            página completa (abre direto no navegador)
  prototipo/conteudo.html         mesmo conteúdo sem <html>/<head> (para publicar como Artifact)
"""
import os, re, json, random, math
from gerar_mapa_tiradentes import DEFS, R, Pth, L, C, E, TX, copa, araucaria_copa, OL, banco, pombo
from conceitos_camera import EXTRA, fachada, lampiao, brilho

AQUI = os.path.dirname(os.path.abspath(__file__))
RAIZ = os.path.join(AQUI, "..")
WW, TOPO, BASE_Y = 4300, -300, 1720      # mundo: x 0..4300, y -300..1720
FACH = 520                               # linha de base das fachadas
rnd = random.Random(42)

OBST = []                                # círculos de colisão (x, y, r)
GLOWS = []                               # luzes (x, y, r, cor)

def ob(x, y, r):
    OBST.append([round(x), round(y), r])

def objeto(y, svg):
    return (y, f'<g data-y="{y:.0f}">{svg}</g>\n')

# ------------------------------------------------------------------ peças do cenário
def catedral(cx, b):
    o = R(cx - 220, b - 420, 440, 100, "url(#ardosia)") + Pth(f"M{cx-220},{b-330} L{cx+220},{b-330} L{cx+160},{b-430} L{cx-160},{b-430} Z", "url(#ardosia)")
    o += R(cx - 300, b - 330, 600, 330, "#d9d1c1") + R(cx - 300, b - 330, 24, 330, "#b8af9e", sw=0)
    o += L(f"M{cx-300},{b-250} L{cx+300},{b-250} M{cx-300},{b-150} L{cx+300},{b-150}", "#b9b09c", 5)
    o += Pth(f"M{cx-210},{b-328} L{cx+210},{b-328} L{cx},{b-480} Z", "#d9d1c1") + Pth(f"M{cx-160},{b-334} L{cx+160},{b-334} L{cx},{b-450} Z", "#cbc2b0", 2.5)
    o += L(f"M{cx},{b-480} L{cx},{b-530} M{cx-16},{b-512} L{cx+16},{b-512}", OL, 8) + L(f"M{cx},{b-480} L{cx},{b-530} M{cx-16},{b-512} L{cx+16},{b-512}", "#d9a43a", 4)
    for tx in (cx - 410, cx + 240):
        tc = tx + 85
        o += R(tx, b - 560, 170, 560, "#e2dbcc") + R(tx, b - 560, 22, 560, "#c4bba8", sw=0) + R(tx, b - 560, 170, 560, "none")
        o += Pth(f"M{tx-10},{b-560} L{tx+180},{b-560} L{tc},{b-800} Z", "url(#ardosia)") + Pth(f"M{tc},{b-800} L{tx+180},{b-560} L{tc+4},{b-560} Z", "#4a4f5c", 0, 0.55)
        o += L(f"M{tc},{b-800} L{tc},{b-830}", OL, 5) + C(tc, b - 834, 6, "#d9a43a", 2.5)
        for px_ in (tx + 6, tx + 164):
            o += Pth(f"M{px_-11},{b-562} L{px_+11},{b-562} L{px_},{b-612} Z", "#cbc2b0", 2.5)
        for (wy, wh, lit) in ((b - 500, 80, False), (b - 360, 110, True)):
            o += Pth(f"M{tc-24},{wy+wh} L{tc-24},{wy+24} Q{tc-24},{wy} {tc},{wy-8} Q{tc+24},{wy} {tc+24},{wy+24} L{tc+24},{wy+wh} Z", "#ffcf7a" if lit else "#2e3c5c")
            o += L(f"M{tc},{wy} L{tc},{wy+wh} M{tc-24},{wy+wh*0.55:.0f} L{tc+24},{wy+wh*0.55:.0f}", "#8a6440" if lit else "#7f93c4", 2.5)
        o += Pth(f"M{tc-28},{b} L{tc-28},{b-70} Q{tc-28},{b-104} {tc},{b-112} Q{tc+28},{b-104} {tc+28},{b-70} L{tc+28},{b} Z", "#5a3b24")
    o += C(cx, b - 250, 64, "#c4bba8") + C(cx, b - 250, 50, "#2e3c5c", 2.5)
    for i in range(10):
        a = i * math.pi / 5
        o += L(f"M{cx},{b-250} L{cx+46*math.cos(a):.1f},{b-250+46*math.sin(a):.1f}", "#c8a8e8", 4)
    o += C(cx, b - 250, 13, "#d9a43a", 2.5)
    o += Pth(f"M{cx-86},{b} L{cx-86},{b-120} Q{cx-86},{b-190} {cx},{b-214} Q{cx+86},{b-190} {cx+86},{b-120} L{cx+86},{b} Z", "#c4bba8")
    o += Pth(f"M{cx-70},{b} L{cx-70},{b-122} Q{cx-70},{b-176} {cx},{b-196} Q{cx+70},{b-176} {cx+70},{b-122} L{cx+70},{b} Z", "#ffcf7a")
    o += Pth(f"M{cx-70},{b} L{cx-70},{b-122} Q{cx-70},{b-160} {cx-40},{b-180} L{cx-40},{b} Z", "#5a3b24") + Pth(f"M{cx+70},{b} L{cx+70},{b-122} Q{cx+70},{b-160} {cx+40},{b-180} L{cx+40},{b} Z", "#5a3b24")
    o += R(cx - 130, b, 260, 18, "#b4ad9e", sw=2.5) + R(cx - 150, b + 18, 300, 16, "#a49d90", sw=2.5)
    GLOWS.append((cx, b - 80, 260, "luz"))
    return o

def igreja_ordem(x0, b):
    dx, dy = x0 - 70, b - 910
    ig, igs, tri = "#e4ddd6", "#b4aab4", "#c9a45a"
    o = R(70, 470, 140, 440, ig) + R(70, 470, 26, 440, igs, sw=0) + Pth("M60,474 L220,474 L140,380 Z", "url(#telha)") + L("M140,380 L140,352", OL, 5) + C(140, 350, 6, "#d9a43a", 2)
    o += Pth("M112,620 L112,560 Q112,530 140,522 Q168,530 168,560 L168,620 Z", "#2a2440") + Pth("M124,590 Q140,570 156,590 L156,606 L124,606 Z", "#d9a43a", 2)
    o += C(140, 700, 26, "#f4efe2", 3) + L("M140,700 L140,684 M140,700 L152,706", OL, 3)
    o += R(210, 600, 380, 310, ig) + R(210, 600, 26, 310, igs, sw=0) + R(210, 600, 380, 14, tri, sw=2) + R(210, 896, 380, 14, tri, sw=2)
    o += Pth("M250,602 L550,602 L400,500 Z", ig) + Pth("M286,598 L514,598 L400,528 Z", "#d6cfc8", 2) + L("M400,500 L400,466 M386,480 L414,480", OL, 6) + L("M400,500 L400,466 M386,480 L414,480", "#d9a43a", 3)
    for px_ in (210, 300, 500, 580):
        o += R(px_, 612, 12, 286, tri, sw=2)
    o += Pth("M354,910 L354,800 Q354,760 400,748 Q446,760 446,800 L446,910 Z", tri) + Pth("M364,910 L364,804 Q364,770 400,760 Q436,770 436,804 L436,910 Z", "#ffcf7a")
    for wx in (246, 520):
        o += Pth(f"M{wx},770 L{wx},700 Q{wx},676 {wx+22},670 Q{wx+44},676 {wx+44},700 L{wx+44},770 Z", "#ffcf7a") + L(f"M{wx+22},672 L{wx+22},770", "#8a6440", 2)
    GLOWS.append((x0 + 330, b - 60, 200, "luz"))
    return f'<g transform="translate({dx},{dy})">{o}</g>\n'

def cavalo_babao(hx, base):
    fb = E(hx, base + 8, 190, 30, "#000", 0, 0.3)
    fb += Pth(f"M{hx-100},{base-20} L{hx-100},{base-240} Q{hx-100},{base-284} {hx-50},{base-286} L{hx+50},{base-286} Q{hx+100},{base-284} {hx+100},{base-240} L{hx+100},{base-20} Z", "#9a948a")
    fb += R(hx - 100, base - 262, 22, 242, "#827c72", sw=0) + L(f"M{hx-94},{base-150} L{hx+94},{base-150}", "#827c72", 4)
    s = 1.8
    def H(d):
        return re.sub(r'(-?\d+(?:\.\d+)?),(-?\d+(?:\.\d+)?)', lambda m: f"{hx + float(m.group(1)) * s:.1f},{base - 190 + float(m.group(2)) * s:.1f}", d)
    fb += Pth(H("M-26,-26 C-30,-48 -14,-56 -4,-44 L6,-50 C14,-46 24,-34 22,-12 C20,8 16,30 10,44 C4,54 -12,54 -16,42 C-22,24 -24,0 -26,-26 Z"), "#8a6a3e")
    fb += Pth(H("M-26,-26 C-24,0 -22,24 -16,42 C-12,50 -4,52 2,50 C-6,30 -12,2 -14,-30 Z"), "#5e4628", 0)
    fb += Pth(H("M-22,-34 L-28,-58 L-12,-44 Z"), "#8a6a3e") + Pth(H("M2,-44 L4,-66 L14,-44 Z"), "#8a6a3e")
    fb += L(H("M-26,-22 C-34,-8 -34,10 -30,26"), "#5e4628", 6)
    fb += Pth(H("M-12,-18 L-1,-14 L-2,-10 L-12,-12 Z"), "#1e1a24", 0) + Pth(H("M16,-18 L5,-14 L6,-10 L16,-12 Z"), "#1e1a24", 0)
    fb += Pth(f"M{hx-6},{base-98} C{hx-8},{base-76} {hx-3},{base-56} {hx-6},{base-40} L{hx+6},{base-40} C{hx+3},{base-56} {hx+8},{base-76} {hx+6},{base-98} Z", "#9fe6ff", 2)
    fb += R(hx - 140, base - 62, 280, 66, "#a49d90", rx=16) + R(hx - 122, base - 50, 244, 32, "#4aa0c8", rx=10, sw=2)
    fb += L(f"M{hx-100},{base-34} C{hx-80},{base-42} {hx-60},{base-28} {hx-40},{base-36} M{hx+30},{base-30} C{hx+50},{base-38} {hx+70},{base-24} {hx+90},{base-32}", "#d8f6ff", 3)
    fb += R(hx - 70, base - 140, 140, 24, "#3a2a20", rx=4, sw=2) + TX(hx, base - 123, "CAVALO BABÃO", 14)
    GLOWS.append((hx, base - 30, 170, "luzagua"))
    ob(hx, base - 20, 150)
    return fb

def arvore(x, y, kind, sc=1.0):
    t = E(x + 20, y + 6, 80 * sc, 22 * sc, "#000", 0, 0.28) + R(x - 8 * sc, y - 90 * sc, 16 * sc, 92 * sc, "#6b4a2e", rx=4)
    if kind == "araucaria":
        t += R(x - 7, y - 230, 14, 232, "#6b4a2e", rx=4) + L(f"M{x},{y-150} L{x-26},{y-168} M{x},{y-180} L{x+24},{y-196}", "#6b4a2e", 6) + araucaria_copa(x, y - 260)
    else:
        cor = ("#e9c23c", "#c99a22", "#f7e07a") if kind == "ipe" else ("#4f8a3e", "#33602a", "#79b05a")
        t += copa(x, y - 140 * sc, 64 * sc, *cor)
    ob(x, y, 30 * sc)
    return t

def poste(x, y):
    p, (gx, gy) = lampiao(x, y, 230, 0.85)
    GLOWS.append((gx, gy, 230, "luz"))
    ob(x, y, 16)
    return E(x, y + 3, 20, 7, "#000", 0, 0.3) + p

def barraca(x, y, c1, c2):
    o = E(x, y + 6, 110, 18, "#000", 0, 0.28)
    o += R(x - 90, y - 150, 8, 150, "#5a3b24", sw=2) + R(x + 82, y - 150, 8, 150, "#5a3b24", sw=2)
    o += R(x - 100, y - 70, 200, 56, "#8a5a34") + R(x - 100, y - 70, 200, 12, "#9e6a40", sw=2)
    for i, cor in enumerate(["#e8505b", "#f2c84b", "#7fae8a", "#6a95b8", "#c26be0", "#e8505b", "#f2c84b"]):
        o += C(x - 78 + i * 26, y - 76, 10, cor, 2)
    for i in range(8):
        o += Pth(f"M{x-110+i*28},{y-150} L{x-82+i*28},{y-150} L{x-82+i*28},{y-124} Q{x-96+i*28},{y-112} {x-110+i*28},{y-124} Z", c1 if i % 2 else c2, 2.5)
    ob(x, y - 10, 100)
    return o

# ------------------------------------------------------------------ mundo
def gerar_mundo():
    chao = ""
    # céu e silhuetas acima das fachadas
    chao += R(0, TOPO, WW, FACH - TOPO + 40, "url(#ceu)", sw=0)
    for _ in range(140):
        chao += C(rnd.randint(0, WW), rnd.randint(TOPO, 120), round(rnd.random() * 1.8 + 0.5, 1), "#ffffff", 0, round(rnd.random() * 0.5 + 0.25, 2))
    chao += C(3000, -120, 230, "url(#lua)", 0, 0.5) + C(3000, -120, 70, "#fbe6c4", 0, 0.85)
    for ax in range(80, WW, 330):
        h = rnd.randint(260, 380)
        chao += R(ax - 4, FACH - h, 8, h, "#2f2445", sw=0)
        for dy, rx in ((0, 90), (26, 74), (50, 56), (70, 36)):
            chao += E(ax, FACH - h + 14 - dy, rx, 16, "#2f2445")
    # chão
    chao += R(0, FACH, WW, BASE_Y - FACH, "url(#pedra)", sw=0)
    chao += R(0, FACH, WW, 84, "url(#calcada)", sw=0) + L(f"M0,{FACH+84} L{WW},{FACH+84}", "#8a8478", 6)
    chao += Pth("M0,640 C200,610 500,630 800,620 C1100,610 1400,640 1880,630 L1880,1720 L0,1720 Z", "url(#petit)", 4)
    for (gx, gy, rx, ry) in ((330, 900, 230, 130), (1560, 880, 220, 120), (420, 1440, 300, 150), (1480, 1460, 280, 140)):
        d = f"M{gx-rx},{gy} C{gx-rx},{gy-ry*1.1} {gx+rx*0.2},{gy-ry*1.2} {gx+rx},{gy-ry*0.4} C{gx+rx*1.2},{gy+ry*0.3} {gx+rx*0.4},{gy+ry*1.1} {gx-rx*0.3},{gy+ry} C{gx-rx*1.1},{gy+ry*0.9} {gx-rx*1.05},{gy+ry*0.4} {gx-rx},{gy} Z"
        chao += Pth(d, "url(#grama)", 4)
        for _ in range(int(rx * ry / 900)):
            a, r_ = rnd.random() * 6.28, rnd.random() * 0.85
            chao += C(round(gx + rx * r_ * math.cos(a), 1), round(gy + ry * r_ * math.sin(a), 1), 4, rnd.choice(["#e8505b", "#f4efe2", "#f2c84b", "#c26be0"]), 1.4)
    chao += R(860, 1040, 180, 56, "#4e4a46", rx=6) + R(868, 1046, 164, 44, "url(#pedra)", sw=0) + R(868, 1046, 164, 44, "#bfe3f0", sw=2, op=0.35)
    chao += L("M880,1052 L910,1084 M950,1052 L980,1084", "#ffffff", 3, 0.5)
    ob(950, 1068, 70); ob(880, 1068, 40); ob(1020, 1068, 40)
    # avenida
    chao += R(1880, FACH, 280, BASE_Y - FACH, "#47474e", sw=0) + L(f"M1884,{FACH} L1884,{BASE_Y} M2156,{FACH} L2156,{BASE_Y}", "#9a948a", 8)
    for y in range(FACH + 30, BASE_Y, 90):
        if 900 < y < 1240:
            continue
        chao += R(2016, y, 8, 46, "#e8e4d8", sw=0)
    for y in range(920, 1220, 44):
        chao += R(1904, y, 232, 24, "#ecebe4", sw=0)
    # rua claudino: calçada inferior
    chao += R(2160, 1380, 1060, 60, "url(#calcada)", sw=0) + L("M2160,1380 L3220,1380", "#8a8478", 6)
    # largo: anel de pedras ao redor do chafariz
    chao += E(3900, 1000, 380, 160, "#9a9187", 0, 0.35) + E(3900, 1000, 320, 130, "none", 4)
    # poças e folhas
    for _ in range(40):
        x, y = rnd.randint(200, WW - 200), rnd.randint(700, 1650)
        chao += E(x, y, rnd.randint(30, 80), rnd.randint(10, 20), "#3e5a72", 0, 0.3)
    for _ in range(220):
        x, y = rnd.randint(0, WW), rnd.randint(620, 1700)
        chao += Pth(f"M{x},{y} l9,-4 l4,6 l-9,4 Z", rnd.choice(["#c9a43a", "#a8553a", "#7e3b28"]), 0, 0.8)

    objs = []
    # fachadas (fundo)
    cores = [("#e2b85a", "#c49a44"), ("#6a95b8", "#4f7a9c"), ("#d48a8a", "#b46e6e"), ("#7fae8a", "#62907a"), ("#e6d8b8", "#c8b994"), ("#b98ac9", "#9a6eab")]
    fach = ""
    def fileira(x0, x1, letreiros, alt=(240, 300)):
        nonlocal fach
        x, k = x0, 0
        while x < x1:
            w = min(rnd.randint(220, 300), x1 - x)
            if w < 120:
                break
            cf, cd = cores[(k + x0 // 100) % len(cores)]
            fach += fachada(x, FACH, w, rnd.randint(*alt), cf, cd, letreiros.get(k), rnd)
            x += w; k += 1
    fileira(-30, 520, {})
    fach += catedral(970, FACH)
    fileira(1430, 1880, {0: "PALACETE"})
    fileira(2160, 3260, {0: "CAFÉ", 1: "LIVROS", 2: "BAR", 3: "ANTIQUÁRIO", 4: "ARTE"})
    fach += igreja_ordem(3290, FACH)
    fileira(3830, 4330, {0: "MEMORIAL"})
    objs.append((FACH, f'<g data-y="{FACH}">{fach}</g>\n'))
    # objetos com profundidade
    for (x, y, k, sc) in ((300, 900, "araucaria", 1), (1600, 870, "ipe", 1), (430, 1430, "verde", 1.15), (1480, 1450, "ipe", 1.15), (720, 1330, "verde", 1),
                          (2400, 1360, "ipe", 0.95), (2900, 1360, "verde", 0.95), (3420, 1580, "verde", 1.1), (4230, 1260, "araucaria", 1), (4150, 1500, "ipe", 1.1)):
        objs.append(objeto(y, arvore(x, y, k, sc)))
    for (x, y) in ((660, 700), (1280, 700), (560, 1180), (1380, 1180), (2300, 700), (2700, 1360), (3100, 700), (3600, 820), (4120, 1180)):
        objs.append(objeto(y, poste(x, y)))
    for (x, y) in ((760, 830), (1060, 830), (900, 1300)):
        objs.append(objeto(y + 30, banco(x - 55, y, 110)))
        ob(x, y + 20, 52)
    sx, sy = 950, 930
    mz = E(sx, sy + 4, 90, 24, "#000", 0, 0.3) + E(sx, sy - 4, 80, 28, "#a49d90", 4) + E(sx, sy - 10, 60, 20, "#bdb6a8", 3)
    mz += Pth(f"M{sx-24},{sy-10} L{sx+24},{sy-10} L{sx+16},{sy-120} L{sx-16},{sy-120} Z", "#d9d1c1") + Pth(f"M{sx-20},{sy-118} L{sx+20},{sy-118} L{sx},{sy-146} Z", "#c4bba8")
    mz += R(sx - 18, sy - 84, 36, 26, "#8a6a3e", sw=2) + TX(sx, sy - 65, "0", 18)
    objs.append(objeto(sy, mz)); ob(sx, sy - 6, 66)
    objs.append(objeto(1000, pombo(1100, 1000) + pombo(1126, 1010, -1) + pombo(1080, 1020)))
    objs.append(objeto(1000, cavalo_babao(3900, 1000)))
    objs.append(objeto(1330, barraca(3560, 1330, "#e8505b", "#f4efe2")))
    objs.append(objeto(1420, barraca(3820, 1420, "#3f7a52", "#f4efe2")))
    # primeiro plano (sempre na frente): telhados do outro lado da rua e cerca viva
    frente = R(2160, 1440, 1060, 300, "url(#telha)", sw=4) + R(2160, 1440, 1060, 300, "#1a1430", sw=0, op=0.35)
    for x in range(2160, 3220, 212):
        frente += L(f"M{x},1440 L{x},1740", "#5e2a1e", 6) + R(x + 90, 1470, 34, 50, "#7e3b28", sw=3)
    for x in list(range(-40, 1880, 120)) + list(range(3220, 4340, 120)):
        frente += C(x, 1735, 70, "#2f5228", 4) + C(x - 20, 1715, 30, "#3f6b35", 0)
    objs.sort(key=lambda t: t[0])
    glows = "".join(f'<circle cx="{x:.0f}" cy="{y:.0f}" r="{r}" fill="url(#{g})" opacity="0.55"/>' for x, y, r, g in GLOWS)
    return chao, "".join(s for _, s in objs), frente, glows

# ------------------------------------------------------------------ personagens
PERS = {
    "ninja": ("ninja_estilizado_lado_separado.svg", "bipede", 150, "Ninja"),
    "medusa": ("medusa_estilizado_lado_separado.svg", "bipede", 152, "Medusa"),
    "necromante": ("necromante_estilizado_lado_separado.svg", "bipede", 156, "Necromante"),
    "cachorro": ("cachorro_zumbi_estilizado_lado_separado.svg", "quad", 108, "Cachorro zumbi"),
}

def templates():
    o = ""
    for k, (arq, tipo, h, _) in PERS.items():
        svg = open(os.path.join(RAIZ, arq)).read()
        inner = svg[svg.index(">", svg.index("<svg")) + 1: svg.rindex("</svg>")]
        inner = re.sub(r"<!--.*?-->", "", inner, flags=re.S)
        inner = re.sub(r'<g id="([a-z_]+)"', r'<g data-part="\1"', inner)
        o += f'<g id="tpl_{k}">{inner}</g>\n'
    return o

# ------------------------------------------------------------------ página
CSS = r"""
<title>Rumo ao Cavalo Babão</title>
<meta name="claude:viewport-fit-sides" content="cover">
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=IM+Fell+English+SC&family=Alegreya+Sans:wght@400;500;700&display=swap">
<style>
/* Layout: o jogo ocupa a tela; HUD flutua nas bordas respeitando as áreas seguras. */
:root{
  --noite:#120e1c; --nevoa:#2a2140; --pergaminho:#f1e6d0; --ouro:#d9a43a; --veneno:#8be04a; --tinta:#1a1422;
  --display:"IM Fell English SC", "Iowan Old Style", Georgia, serif;
  --texto:"Alegreya Sans", "Segoe UI", system-ui, sans-serif;
  color-scheme:dark;
}
html,body{height:100%;}
body{background:var(--noite);color:var(--pergaminho);font-family:var(--texto);overflow:hidden;
  padding-left:max(0px, env(safe-area-inset-left, 0px));padding-right:max(0px, env(safe-area-inset-right, 0px));}
#jogo{position:relative;width:100%;height:100%;overflow:hidden;touch-action:none;outline:none;cursor:crosshair}
#mundo{display:block;width:100%;height:100%}
.vinheta{position:absolute;inset:0;pointer-events:none;
  background:radial-gradient(ellipse at 50% 55%, transparent 55%, rgba(5,3,10,.82) 100%), linear-gradient(rgba(26,20,48,.16), rgba(26,20,48,.16));}
.hud{position:absolute;pointer-events:none;inset:0;
  padding:calc(14px + env(safe-area-inset-top,0px)) max(16px, env(safe-area-inset-right,0px)) calc(14px + env(safe-area-inset-bottom,0px)) max(16px, env(safe-area-inset-left,0px));}
.topo{display:flex;gap:12px;align-items:flex-start;justify-content:space-between;flex-wrap:wrap}
.trilha{pointer-events:none;flex:1 1 320px;max-width:520px;min-width:0;background:rgba(18,14,28,.62);border:1px solid rgba(241,230,208,.18);
  border-radius:14px;padding:10px 16px 12px;backdrop-filter:blur(6px)}
.local{font-family:var(--display);font-size:clamp(20px,2.6vw,30px);letter-spacing:.04em;line-height:1.1;text-wrap:balance}
.barra{position:relative;height:6px;border-radius:3px;background:rgba(241,230,208,.16);margin-top:10px}
.barra i{position:absolute;left:0;top:0;bottom:0;border-radius:3px;background:linear-gradient(90deg,var(--ouro),var(--veneno));width:0}
.barra b{position:absolute;top:50%;width:14px;height:14px;margin:-7px 0 0 -7px;border-radius:50%;background:var(--pergaminho);box-shadow:0 0 10px var(--ouro)}
.marcos{display:flex;justify-content:space-between;font-size:12px;letter-spacing:.08em;text-transform:uppercase;opacity:.7;margin-top:6px}
.escolha{pointer-events:auto;display:flex;gap:6px;flex-wrap:wrap;justify-content:flex-end}
.escolha button{font:500 14px var(--texto);color:var(--pergaminho);background:rgba(18,14,28,.62);border:1px solid rgba(241,230,208,.22);
  border-radius:999px;padding:7px 14px;cursor:pointer;backdrop-filter:blur(6px)}
.escolha button[aria-pressed="true"]{background:var(--ouro);color:var(--tinta);border-color:var(--ouro)}
.escolha button:focus-visible,.aviso button:focus-visible{outline:2px solid var(--veneno);outline-offset:2px}
.dica{position:absolute;left:max(16px, env(safe-area-inset-left,0px));bottom:calc(14px + env(safe-area-inset-bottom,0px));font-size:14px;opacity:.78;
  background:rgba(18,14,28,.55);padding:6px 12px;border-radius:10px}
.titulo{position:absolute;left:0;right:0;top:30%;text-align:center;font-family:var(--display);font-size:clamp(34px,6vw,72px);
  letter-spacing:.06em;text-shadow:0 2px 24px rgba(0,0,0,.8);opacity:0;transition:opacity .8s ease;pointer-events:none}
.titulo.on{opacity:1}
.titulo small{display:block;font:500 clamp(13px,1.6vw,18px) var(--texto);letter-spacing:.22em;text-transform:uppercase;opacity:.75;margin-top:6px}
.aviso{pointer-events:auto;position:absolute;left:50%;bottom:calc(28px + env(safe-area-inset-bottom,0px));transform:translateX(-50%);
  background:rgba(18,14,28,.86);border:1px solid var(--veneno);border-radius:16px;padding:14px 18px;display:flex;gap:14px;align-items:center;
  max-width:calc(100% - 32px);box-shadow:0 0 30px rgba(139,224,74,.25)}
.aviso p{margin:0;font-size:16px}.aviso strong{font-family:var(--display);font-weight:400;font-size:20px;color:var(--veneno)}
.aviso button{font:700 14px var(--texto);background:var(--veneno);color:var(--tinta);border:0;border-radius:999px;padding:8px 14px;cursor:pointer;white-space:nowrap}
.joy{position:absolute;width:120px;height:120px;margin:-60px 0 0 -60px;border-radius:50%;border:2px solid rgba(241,230,208,.35);background:rgba(18,14,28,.35);pointer-events:none}
.joy i{position:absolute;left:50%;top:50%;width:46px;height:46px;margin:-23px 0 0 -23px;border-radius:50%;background:rgba(241,230,208,.55)}
@media (max-width:640px){.dica{display:none}.trilha{flex-basis:100%}.escolha{justify-content:flex-start}}
@media (prefers-reduced-motion:reduce){.titulo{transition:none}}
</style>
"""

JS = r"""
<script>
(() => {
const WW=__WW__, TOPO=__TOPO__, BASE=__BASE__, FACH=__FACH__;
const OBST=__OBST__;
const PERS=__PERS__;
const INICIO={x:970,y:660}, FONTE={x:3900,y:1060};
const svg=document.getElementById('mundo'), cena=document.getElementById('objetos'), falas=document.getElementById('falas');
const jogo=document.getElementById('jogo');
const sin=Math.sin, PI=Math.PI;

// ---------- poses (mesmas do tools/animar_svg.js)
const bParado=t=>({dy:1.2*sin(t),tl:1.2*sin(t),hd:-2*sin(t+0.6),bst:4*sin(t+0.4),abt:5*sin(t+0.9),mbt:6*sin(t+1.3),bsf:-2*sin(t),abf:2*sin(t),mbf:-sin(t),sk:0.6*sin(t),glow:1+0.12*sin(2*t)});
function bAndando(t){const leg=p=>{const th=-22*sin(p),sh=Math.max(0,30*sin(p+PI/2))*0.9+4;return{th,sh,pe:-(th+sh)+(sin(p)<0?-6*sin(p):0)}};
  const F=leg(t),B=leg(t+PI);
  return{dy:-1.8*Math.abs(sin(t)),tl:3,hd:1.5*sin(2*t),cft:F.th,cnf:F.sh,pef:F.pe,ctt:B.th,cnt:B.sh,pet:B.pe,bst:16*sin(t),abt:8*sin(t-0.5),mbt:6*sin(t-1),bsf:-4*sin(t),abf:3*sin(t),mbf:2*sin(t),sk:2*sin(t),glow:1+0.08*sin(2*t)};}
const PQ=['tras_perto','tras_longe','diant_perto','diant_longe'];
const qParado=t=>({dy:0.8*sin(t),tl:0.6*sin(t),hd:2*sin(t+0.5),jaw:6+3*sin(3*t),tail:7*sin(2*t),tras_perto_s:sin(t),tras_longe_s:sin(t)});
function qAndando(t){const fase={tras_perto:0,diant_perto:PI/2,tras_longe:PI,diant_longe:3*PI/2},o={dy:1.2*sin(2*t),tl:sin(2*t),hd:2*sin(2*t+1),jaw:4+2*sin(2*t),tail:10*sin(t)};
  for(const L of PQ){const p=t+fase[L],lift=Math.max(0,Math.cos(p));
    if(L.startsWith('tras')){const s=-14*sin(p),i=22*lift;o[L+'_s']=s;o[L+'_i']=i;o[L+'_p']=-(s+i)+14*lift;}
    else{const s=-12*sin(p),i=8*lift;o[L+'_s']=s;o[L+'_i']=i;o[L+'_p']=-(s+i)+45*lift;}}
  return o;}
const mix=(a,b,w)=>{const o={};for(const k of new Set([...Object.keys(a),...Object.keys(b)]))o[k]=(a[k]||0)*(1-w)+(b[k]||0)*w;return o;};

// ---------- atores
function criarAtor(tipo,x,y,dir){
  const [arq,rig,altura,nome]=PERS[tipo];
  const el=document.createElementNS('http://www.w3.org/2000/svg','g');
  const corpo=document.getElementById('tpl_'+tipo).cloneNode(true); corpo.removeAttribute('id');
  const sombra=document.createElementNS('http://www.w3.org/2000/svg','ellipse');
  sombra.setAttribute('rx',rig==='quad'?70:52);sombra.setAttribute('ry',10);sombra.setAttribute('fill','#000');sombra.setAttribute('opacity','0.32');
  el.appendChild(sombra); el.appendChild(corpo);
  const partes={};
  corpo.querySelectorAll('[data-part]').forEach(g=>{const [px,py]=g.dataset.pivot.split(',').map(Number);partes[g.dataset.part]={el:g,px,py};});
  const brilhos=[...corpo.querySelectorAll('[data-part="arma"] circle')].filter(c=>+c.getAttribute('r')>8).map(c=>[c,+c.getAttribute('r')]);
  const a={tipo,rig,nome,el,corpo,sombra,partes,brilhos,x,y,dir:dir||1,s:altura/(rig==='quad'?183:180),t:Math.random()*6,fase:0,andar:0,vel:0};
  cena.appendChild(el); return a;
}
function R(a,p,ang){const q=a.partes[p];return ang?`rotate(${ang.toFixed(2)} ${q.px} ${q.py})`:'';}
function por(a,p,tr){const q=a.partes[p];if(q)q.el.setAttribute('transform',tr);}
function posar(a,P){
  const v=k=>P[k]||0;
  if(a.rig==='quad'){
    const body=`translate(0 ${v('dy').toFixed(2)}) `+R(a,'tronco',v('tl'));
    por(a,'tronco',body);por(a,'cauda',body+' '+R(a,'cauda',v('tail')));
    const head=body+' '+R(a,'cabeca',v('hd'));por(a,'cabeca',head);por(a,'mandibula',head+' '+R(a,'mandibula',v('jaw')));
    for(const L of PQ){const c=[body,R(a,`perna_${L}_sup`,v(L+'_s')),R(a,`perna_${L}_inf`,v(L+'_i')),R(a,`pata_${L}`,v(L+'_p'))];
      por(a,`perna_${L}_sup`,c.slice(0,2).join(' '));por(a,`perna_${L}_inf`,c.slice(0,3).join(' '));por(a,`pata_${L}`,c.join(' '));}
    return;}
  if(a.partes.arma_tras){P.bst=v('bst')*0.35;P.abt=v('abt')*0.35;P.mbt=-(P.bst+P.abt)-v('tl');}
  const body=`translate(0 ${v('dy').toFixed(2)})`, torso=body+' '+R(a,'tronco',v('tl'));
  por(a,'quadril',body+' '+R(a,'quadril',v('sk')));por(a,'tronco',torso);por(a,'cabeca',torso+' '+R(a,'cabeca',v('hd')));
  const F=[torso,R(a,'braco_sup_frente',v('bsf')),R(a,'antebraco_frente',v('abf')),R(a,'mao_frente',v('mbf'))];
  por(a,'braco_sup_frente',F.slice(0,2).join(' '));por(a,'antebraco_frente',F.slice(0,3).join(' '));por(a,'mao_frente',F.join(' '));por(a,'arma',F.join(' '));
  const T=[torso,R(a,'braco_sup_tras',v('bst')),R(a,'antebraco_tras',v('abt')),R(a,'mao_tras',v('mbt'))];
  por(a,'braco_sup_tras',T.slice(0,2).join(' '));por(a,'antebraco_tras',T.slice(0,3).join(' '));por(a,'mao_tras',T.join(' '));por(a,'arma_tras',T.join(' '));
  for(const [s,th,sh,pe] of [['frente','cft','cnf','pef'],['tras','ctt','cnt','pet']]){
    const L=[body,R(a,'coxa_'+s,v(th)),R(a,'canela_'+s,v(sh)),R(a,'pe_'+s,v(pe))];
    por(a,'coxa_'+s,L.slice(0,2).join(' '));por(a,'canela_'+s,L.slice(0,3).join(' '));por(a,'pe_'+s,L.join(' '));}
  for(const [c,r0] of a.brilhos) c.setAttribute('r',(r0*(P.glow||1)).toFixed(1));
}
function animar(a,dt){
  a.t+=dt*(2*PI/1.4);
  a.andar+=((a.vel>5?1:0)-a.andar)*Math.min(1,dt*8);
  a.fase+=dt*2*PI*(a.vel/(a.rig==='quad'?230:250));
  const idle=a.rig==='quad'?qParado(a.t):bParado(a.t), walk=a.rig==='quad'?qAndando(a.fase):bAndando(a.fase);
  posar(a,mix(idle,walk,a.andar));
  const cx=a.rig==='quad'?138:128;
  a.corpo.setAttribute('transform',`scale(${a.dir*a.s} ${a.s}) translate(${-cx} -240)`);
  a.sombra.setAttribute('cy',2);
  a.el.setAttribute('transform',`translate(${a.x.toFixed(1)} ${a.y.toFixed(1)})`);
  a.el.dataset.y=a.y;
  // ordenação por profundidade: desliza entre os vizinhos
  let n;
  while((n=a.el.previousElementSibling)&&+n.dataset.y>a.y) cena.insertBefore(a.el,n);
  while((n=a.el.nextElementSibling)&&+n.dataset.y<a.y) cena.insertBefore(n,a.el);
}

// ---------- mundo: limites e colisão
function limitar(p){
  p.x=Math.max(50,Math.min(WW-50,p.x));
  const maxY=(p.x>2160&&p.x<3220)?1370:1640;
  p.y=Math.max(FACH+110,Math.min(maxY,p.y));
  for(const [ox,oy,r] of OBST){const dx=p.x-ox,dy=(p.y-oy)*1.6,d=Math.hypot(dx,dy),m=r+22;
    if(d<m&&d>0.01){p.x=ox+dx/d*m;p.y=oy+dy/d*m/1.6;}}
}
function regiao(x){return x<1880?['Praça Tiradentes','Catedral Basílica']:x<2160?['Travessia','Atravessando a rua']:x<3260?['Rua Claudino dos Santos','Casario histórico']:['Largo da Ordem','Cavalo Babão'];}

// ---------- estado
let atores=[], jogador=null, npcs=[], chegou=false;
const FALAS={ninja:'As sombras do Largo escondem muita coisa...',medusa:'Não olhe nos meus olhos, viajante.',necromante:'O Cavalo Babão nunca para de babar. Nem depois da morte.',cachorro:'Grrrr...'};
function iniciar(tipo,salvo){
  atores.forEach(a=>a.el.remove()); atores=[]; npcs=[]; chegou=false; esconderAviso();
  const pos=salvo||INICIO;
  jogador=criarAtor(tipo,pos.x,pos.y,1); atores.push(jogador);
  const lugares={ninja:[1180,960,-1],medusa:[3470,930,1],necromante:[3700,1180,1],cachorro:[2500,1200,1]};
  for(const k of Object.keys(PERS)) if(k!==tipo){const [x,y,d]=lugares[k];const n=criarAtor(k,x,y,d);n.casa={x,y};n.fala=FALAS[k];atores.push(n);npcs.push(n);}
  document.querySelectorAll('.escolha button').forEach(b=>b.setAttribute('aria-pressed',b.dataset.p===tipo));
  atual=tipo; regiaoAtual=''; cam.x=jogador.x; cam.y=jogador.y;
}
let atual='necromante', regiaoAtual='';

// ---------- entrada
const teclas=new Set(); let alvo=null, joy=null;
addEventListener('keydown',e=>{const k=e.key.toLowerCase();if(['arrowup','arrowdown','arrowleft','arrowright','w','a','s','d','shift'].includes(k)){teclas.add(k);alvo=null;e.preventDefault();}});
addEventListener('keyup',e=>teclas.delete(e.key.toLowerCase()));
addEventListener('blur',()=>teclas.clear());
const joyEl=document.querySelector('.joy');
jogo.addEventListener('pointerdown',e=>{
  if(e.target.closest('button'))return;
  jogo.focus();
  if(e.pointerType==='mouse'){const p=telaParaMundo(e.clientX,e.clientY);alvo=p;return;}
  joy={id:e.pointerId,x0:e.clientX,y0:e.clientY,dx:0,dy:0};joyEl.hidden=false;joyEl.style.left=e.clientX+'px';joyEl.style.top=e.clientY+'px';joyEl.firstElementChild.style.transform='';
  jogo.setPointerCapture(e.pointerId);});
jogo.addEventListener('pointermove',e=>{if(!joy||e.pointerId!==joy.id)return;let dx=e.clientX-joy.x0,dy=e.clientY-joy.y0;const d=Math.hypot(dx,dy),m=50;if(d>m){dx*=m/d;dy*=m/d;}
  joy.dx=dx/m;joy.dy=dy/m;joyEl.firstElementChild.style.transform=`translate(${dx}px,${dy}px)`;});
const soltar=e=>{if(joy&&e.pointerId===joy.id){joy=null;joyEl.hidden=true;}};
jogo.addEventListener('pointerup',soltar);jogo.addEventListener('pointercancel',soltar);

// ---------- câmera
const cam={x:INICIO.x,y:INICIO.y,z:1,w:1920,h:1080};
function telaParaMundo(cx,cy){const r=svg.getBoundingClientRect();return{x:cam.x-cam.w/2+(cx-r.left)/cam.z,y:cam.y-cam.h/2+(cy-r.top)/cam.z};}
function atualizarCamera(dt){
  const r=svg.getBoundingClientRect();
  cam.z=Math.max(0.5,Math.min(1.25,r.height/1000)); cam.w=r.width/cam.z; cam.h=r.height/cam.z;
  const k=Math.min(1,dt*5); cam.x+=(jogador.x-cam.x)*k; cam.y+=(jogador.y-120-cam.y)*k;
  const x0=Math.max(0,Math.min(WW-cam.w,cam.x-cam.w/2)), y0=Math.max(TOPO,Math.min(BASE-cam.h,cam.y-cam.h/2));
  svg.setAttribute('viewBox',`${x0.toFixed(1)} ${y0.toFixed(1)} ${cam.w.toFixed(1)} ${cam.h.toFixed(1)}`);
}

// ---------- HUD
const elLocal=document.querySelector('.local'), elFill=document.querySelector('.barra i'), elDot=document.querySelector('.barra b');
const elTitulo=document.querySelector('.titulo'), elAviso=document.querySelector('.aviso');
let tituloTimer=0;
function mostrarTitulo(n,s){elTitulo.innerHTML=`${n}<small>${s}</small>`;elTitulo.classList.add('on');clearTimeout(tituloTimer);tituloTimer=setTimeout(()=>elTitulo.classList.remove('on'),2600);}
function esconderAviso(){elAviso.hidden=true;}
document.querySelector('.aviso button').addEventListener('click',()=>{iniciar(atual);jogo.focus();});
document.querySelectorAll('.escolha button').forEach(b=>b.addEventListener('click',()=>{iniciar(b.dataset.p,{x:jogador.x,y:jogador.y});jogo.focus();}));
function falar(){
  let html='';
  for(const n of npcs){const d=Math.hypot(n.x-jogador.x,(n.y-jogador.y)*1.4);
    if(d<230){const w=Math.max(170,n.fala.length*8.6+28),h=46,top=n.y-(n.rig==='quad'?170:225),x=n.x-w/2;
      html+=`<g><rect x="${x}" y="${top-h}" width="${w}" height="${h}" rx="14" fill="#f1e6d0" stroke="#1a1422" stroke-width="3"/>`+
        `<path d="M${n.x-10},${top-1} L${n.x+10},${top-1} L${n.x},${top+14} Z" fill="#f1e6d0" stroke="#1a1422" stroke-width="3" stroke-linejoin="round"/>`+
        `<rect x="${n.x-12}" y="${top-4}" width="24" height="6" fill="#f1e6d0"/>`+
        `<text x="${n.x}" y="${top-h/2+6}" text-anchor="middle" font-family="Alegreya Sans, sans-serif" font-size="17" font-weight="500" fill="#1a1422">${n.fala}</text></g>`;}}
  falas.innerHTML=html;
}

// ---------- laço
let ultimo=performance.now();
function quadro(agora){
  const dt=Math.min(0.05,(agora-ultimo)/1000); ultimo=agora;
  let vx=0,vy=0;
  if(teclas.has('arrowleft')||teclas.has('a'))vx-=1; if(teclas.has('arrowright')||teclas.has('d'))vx+=1;
  if(teclas.has('arrowup')||teclas.has('w'))vy-=1; if(teclas.has('arrowdown')||teclas.has('s'))vy+=1;
  if(joy){vx=joy.dx;vy=joy.dy;}
  if(alvo&&!vx&&!vy){const dx=alvo.x-jogador.x,dy=alvo.y-jogador.y,d=Math.hypot(dx,dy);if(d<8)alvo=null;else{vx=dx/d;vy=dy/d;}}
  const mag=Math.hypot(vx,vy); if(mag>1){vx/=mag;vy/=mag;}
  const vmax=teclas.has('shift')?420:260;
  const px=jogador.x,py=jogador.y;
  jogador.x+=vx*vmax*dt; jogador.y+=vy*vmax*0.72*dt; limitar(jogador);
  jogador.vel=Math.hypot(jogador.x-px,(jogador.y-py)/0.72)/Math.max(dt,1e-4);
  if(Math.abs(vx)>0.15)jogador.dir=vx>0?1:-1;
  for(const n of npcs){
    if(n.tipo==='cachorro'){const alvoX=n.casa.x+Math.sin(agora/2600)*280; const ox=n.x; n.x+=(alvoX-n.x)*Math.min(1,dt*2); n.vel=Math.abs(n.x-ox)/Math.max(dt,1e-4); if(Math.abs(n.x-ox)>0.05)n.dir=n.x>ox?1:-1;}
    else{n.vel=0; if(Math.hypot(n.x-jogador.x,n.y-jogador.y)<420)n.dir=jogador.x>n.x?1:-1;}
  }
  for(const a of atores) animar(a,dt);
  atualizarCamera(dt); falar();
  const [nome,sub]=regiao(jogador.x);
  if(nome!==regiaoAtual){regiaoAtual=nome;elLocal.textContent=nome;mostrarTitulo(nome,sub);}
  const f=Math.max(0,Math.min(1,(jogador.x-INICIO.x)/(FONTE.x-INICIO.x)));
  elFill.style.width=(f*100)+'%'; elDot.style.left=(f*100)+'%';
  if(!chegou&&Math.hypot(jogador.x-FONTE.x,(jogador.y-FONTE.y)*1.2)<340){chegou=true;elAviso.hidden=false;}
  requestAnimationFrame(quadro);
}
const hot=window.claude&&window.claude.hot;
if(hot&&hot.snapshot) hot.snapshot(()=>({tipo:atual,x:jogador&&jogador.x,y:jogador&&jogador.y}));
function start(d){d=d||{};iniciar(PERS[d.tipo]?d.tipo:'necromante',d.x?{x:d.x,y:d.y}:null);requestAnimationFrame(quadro);}
if(hot&&hot.ready) hot.ready(start); else start(hot&&hot.data);
})();
</script>
"""

def pagina():
    chao, objs, frente, glows = gerar_mundo()
    corpo = f"""
<div id="jogo" tabindex="0" aria-label="Protótipo: ande da Catedral até o Cavalo Babão">
<svg id="mundo" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1920 1080" preserveAspectRatio="xMidYMid slice">
{DEFS.replace("</defs>", EXTRA + templates() + "</defs>")}
<g id="chao">{chao}</g>
<g id="objetos">{objs}</g>
<g id="frente">{frente}</g>
<g id="luzes" style="mix-blend-mode:screen">{glows}</g>
<g id="falas"></g>
</svg>
<div class="vinheta"></div>
<div class="hud">
 <div class="topo">
  <div class="trilha"><div class="local">Praça Tiradentes</div><div class="barra"><i></i><b></b></div>
   <div class="marcos"><span>Catedral</span><span>Cavalo Babão</span></div></div>
  <div class="escolha" role="group" aria-label="Personagem">
   <button type="button" id="p-necromante" data-p="necromante" aria-pressed="true">Necromante</button>
   <button type="button" id="p-medusa" data-p="medusa" aria-pressed="false">Medusa</button>
   <button type="button" id="p-ninja" data-p="ninja" aria-pressed="false">Ninja</button>
   <button type="button" id="p-cachorro" data-p="cachorro" aria-pressed="false">Cachorro zumbi</button>
  </div>
 </div>
 <div class="dica">Setas ou WASD para andar · Shift corre · clique no chão para ir até lá</div>
 <div class="titulo"></div>
 <div class="aviso" hidden><p><strong>Você chegou ao Cavalo Babão!</strong><br>Fim do trajeto de teste.</p><button type="button" id="recomecar">Recomeçar</button></div>
</div>
<div class="joy" hidden><i></i></div>
</div>
"""
    pers = {k: [v[0], v[1], v[2], v[3]] for k, v in PERS.items()}
    js = (JS.replace("__WW__", str(WW)).replace("__TOPO__", str(TOPO)).replace("__BASE__", str(BASE_Y)).replace("__FACH__", str(FACH))
          .replace("__OBST__", json.dumps(OBST)).replace("__PERS__", json.dumps(pers, ensure_ascii=False)))
    return CSS + corpo + js

def main():
    os.makedirs(os.path.join(RAIZ, "prototipo"), exist_ok=True)
    conteudo = pagina()
    open(os.path.join(RAIZ, "prototipo", "conteudo.html"), "w").write(conteudo)
    completo = ('<!doctype html>\n<html lang="pt-BR"><head><meta charset="utf-8">'
                '<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">'
                '<style>body{margin:0}[hidden]{display:none!important}</style>' + conteudo.split("<style>", 1)[0] +
                "<style>" + conteudo.split("<style>", 1)[1].split("</style>", 1)[0] + "</style></head><body>" +
                conteudo.split("</style>", 1)[1] + "</body></html>\n")
    open(os.path.join(RAIZ, "prototipo", "index.html"), "w").write(completo)
    print("prototipo ok", len(conteudo) // 1024, "KB")

if __name__ == "__main__":
    main()
