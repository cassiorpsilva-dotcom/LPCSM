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

def ob(x, y, r, visao=0):
    OBST.append([round(x), round(y), round(r), visao])

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
    ob(hx, base - 20, 150, 1)
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
    ob(x, y - 10, 100, 1)
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
.status{display:grid;grid-template-columns:1fr 1fr;gap:8px;margin-top:10px}
.st{position:relative;height:16px;border-radius:8px;background:rgba(241,230,208,.14);overflow:hidden}
.st i{position:absolute;left:0;top:0;bottom:0;width:100%;background:#d8404c;transition:width .15s}
#mp i{background:#4f8fd8}
.st span{position:relative;display:block;text-align:center;font-size:11px;line-height:16px;font-weight:700;font-variant-numeric:tabular-nums;letter-spacing:.04em}
.runas{pointer-events:auto;position:absolute;left:50%;transform:translateX(-50%);bottom:calc(14px + env(safe-area-inset-bottom,0px));display:flex;gap:8px;
  flex-wrap:wrap;justify-content:center;max-width:calc(100% - 32px)}
.runas button{position:relative;overflow:hidden;display:grid;justify-items:center;gap:1px;min-width:86px;padding:8px 10px 7px;cursor:pointer;
  font:500 14px var(--texto);color:var(--pergaminho);background:rgba(18,14,28,.78);border:1px solid rgba(241,230,208,.25);border-radius:12px}
.runas button span{font-family:var(--display);font-size:17px}
.runas small{font-size:11px;opacity:.7}
.runas kbd{font:700 11px var(--texto);background:rgba(241,230,208,.16);border-radius:5px;padding:1px 6px}
.runa::after{content:"";position:absolute;left:0;right:0;bottom:0;height:var(--cd,0%);background:rgba(5,3,10,.62);pointer-events:none}
#r-raio{border-color:rgba(139,224,74,.6)}#r-explosao{border-color:rgba(255,138,58,.6)}#r-gfb{border-color:rgba(255,90,42,.7)}#r-cura{border-color:rgba(127,224,255,.6)}
.runa[aria-pressed="true"]{background:rgba(217,164,58,.9);color:var(--tinta);border-color:var(--ouro)}
.mirando{position:absolute;left:50%;transform:translateX(-50%);bottom:calc(96px + env(safe-area-inset-bottom,0px));background:rgba(18,14,28,.8);border:1px solid var(--ouro);border-radius:999px;padding:6px 14px;font-size:15px;white-space:nowrap}.mirando b{font-family:var(--display);font-weight:400;color:var(--ouro);font-size:18px}
.runa.sem{opacity:.45}.runa.longe span{text-decoration:line-through;text-decoration-color:rgba(232,80,91,.8)}
.util[aria-pressed="true"]{background:var(--ouro);color:var(--tinta)}
.runas button:focus-visible{outline:2px solid var(--veneno);outline-offset:2px}
.msg{position:absolute;left:50%;bottom:calc(136px + env(safe-area-inset-bottom,0px));transform:translateX(-50%);font-family:var(--display);font-size:22px;
  text-shadow:0 2px 10px #000;color:#ffb3a8;opacity:0;transition:opacity .2s;white-space:nowrap}
.msg.on{opacity:1}
.morte{position:absolute;inset:0;display:grid;place-content:center;text-align:center;gap:6px;background:rgba(60,0,10,.35);pointer-events:none}
.morte strong{font-family:var(--display);font-weight:400;font-size:clamp(40px,7vw,80px);color:#ff8a7a;text-shadow:0 2px 20px #000}
.dica{bottom:calc(96px + env(safe-area-inset-bottom,0px));max-width:calc(50% - 260px)}
.aviso{bottom:calc(150px + env(safe-area-inset-bottom,0px))}
@media (max-width:640px){.dica{display:none}.trilha{flex-basis:100%}.escolha{justify-content:flex-start}.runas button{min-width:64px;padding:6px 8px}.runas small{display:none}}
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
const NS='http://www.w3.org/2000/svg';
const $=s=>document.querySelector(s);
const svg=$('#mundo'), cena=$('#objetos'), efx=$('#efeitos'), falas=$('#falas'), jogo=$('#jogo');
const sin=Math.sin, PI=Math.PI, rand=(a,b)=>a+Math.random()*(b-a), agora=()=>performance.now()/1000;
const mk=(tag,attrs,pai)=>{const e=document.createElementNS(NS,tag);for(const k in attrs)e.setAttribute(k,attrs[k]);if(pai)pai.appendChild(e);return e;};

// ================= poses (as mesmas de tools/animar_svg.js)
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
const ease=t=>t<0?0:t>1?1:t*t*(3-2*t);
function keys(tab,f){let i=0;while(i<tab.length-2&&f>=tab[i+1][0])i++;const [f0,a]=tab[i],[f1,b]=tab[i+1];const t=ease((f-f0)/(f1-f0||1)),o={};
  for(const k of new Set([...Object.keys(a),...Object.keys(b)]))o[k]=(a[k]||0)+((b[k]||0)-(a[k]||0))*t;return o;}
const CONJURAR={fps:24,n:14,tab:[[0,{glow:1}],[3,{bsf:12,abf:12,mbf:-6,tl:-3,hd:-3,glow:0.9,bst:6}],[6,{bsf:-42,abf:-12,mbf:80,tl:7,hd:4,glow:1.8,bst:-45,abt:-25,mbt:-20}],
  [9,{bsf:-40,abf:-14,mbf:84,tl:6,hd:3,glow:1.6,bst:-42,abt:-28,mbt:-25}],[13,{glow:1}],[14,{glow:1}]]};
const CROUCH={dx:-4,dy:4,tl:4,hd:14,jaw:8,tail:-12,diant_perto_s:16,diant_perto_i:-12,diant_longe_s:16,diant_longe_i:-12,tras_perto_s:-6,tras_perto_i:16,tras_perto_p:-8,tras_longe_s:-6,tras_longe_i:16,tras_longe_p:-8};
const MORDER={fps:22,n:13,tab:[[0,{jaw:4}],[3,CROUCH],[6,{dx:14,dy:-5,tl:-8,hd:-16,jaw:40,tail:18,diant_perto_s:-34,diant_perto_p:26,diant_longe_s:-26,diant_longe_p:26,tras_perto_s:22,tras_longe_s:20}],
  [8,{dx:16,tl:-2,hd:10,jaw:0,tail:10,diant_perto_s:-12,diant_perto_p:12,diant_longe_s:-8,diant_longe_p:8,tras_perto_s:8,tras_longe_s:6}],[12,{jaw:4}],[13,{jaw:4}]]};

// ================= grade lógica invisível (meio-termo: movimento livre na tela, ocupação por células)
const CW=24, CH=17, GY0=FACH, GX=Math.ceil(WW/CW), GY=Math.ceil((BASE-FACH)/CH);
const bloq=new Uint8Array(GX*GY), parede=new Uint8Array(GX*GY);
const cx_=x=>Math.floor(x/CW), cy_=y=>Math.floor((y-GY0)/CH);
const maxY=x=>(x>2160&&x<3220)?1370:1640;
for(let j=0;j<GY;j++)for(let i=0;i<GX;i++){const wx=(i+.5)*CW,wy=GY0+(j+.5)*CH;
  let b=wy<FACH+105||wy>maxY(wx)||wx<40||wx>WW-40;
  let v=wy<FACH+105;
  for(const [ox,oy,r,vis] of OBST){if(Math.hypot(wx-ox,(wy-oy)*1.6)<r+4){b=true;if(vis)v=true;}}
  bloq[j*GX+i]=b?1:0; parede[j*GX+i]=v?1:0;}
const ocup=new Map();
function celulas(a,x,y){const c=cx_(x),r=cy_(y),w=a.rig==='quad'?2:1,o=[];for(let j=r-1;j<=r;j++)for(let i=c-w;i<=c+w;i++)o.push([i,j]);return o;}
function livre(a,x,y){for(const [i,j] of celulas(a,x,y)){if(i<0||j<0||i>=GX||j>=GY||bloq[j*GX+i])return false;const o=ocup.get(j*GX+i);if(o&&o!==a&&o.vivo)return false;}return true;}
function ocupar(a){if(a.cel)for(const k of a.cel)if(ocup.get(k)===a)ocup.delete(k);a.cel=[];if(!a.vivo)return;for(const [i,j] of celulas(a,a.x,a.y)){const k=j*GX+i;ocup.set(k,a);a.cel.push(k);}}
function mover(a,dx,dy){let ok=false;
  if(livre(a,a.x+dx,a.y+dy)){a.x+=dx;a.y+=dy;ok=true;}
  else if(Math.abs(dx)>0.01&&livre(a,a.x+dx,a.y)){a.x+=dx;ok=true;}
  else if(Math.abs(dy)>0.01&&livre(a,a.x,a.y+dy)){a.y+=dy;ok=true;}
  if(ok)ocupar(a);return ok;}
function lugarLivre(a,x,y){for(let r=0;r<40;r++)for(let k=0;k<16;k++){const ang=k*PI/8,px=x+Math.cos(ang)*r*CW,py=y+Math.sin(ang)*r*CH;if(livre(a,px,py))return{x:px,y:py};}return{x,y};}
const dist=(a,b)=>Math.hypot(a.x-b.x,(a.y-b.y)/0.72);
function visao(a,b){const n=Math.ceil(dist(a,b)/10);for(let k=1;k<n;k++){const x=a.x+(b.x-a.x)*k/n,y=a.y+(b.y-a.y)*k/n,i=cx_(x),j=cy_(y);if(i>=0&&j>=0&&i<GX&&j<GY&&parede[j*GX+i]&&y>FACH+110)return false;}return true;}

// ================= atores
let atores=[], jogador=null, idSeq=0;
function criarAtor(tipo,x,y,dir,papel){
  const [arq,rig,altura,nome]=PERS[tipo];
  const el=mk('g',{'data-ator':++idSeq},cena);
  const sombra=mk('ellipse',{rx:rig==='quad'?70:52,ry:10,cy:2,fill:'#000',opacity:0.32},el);
  const anel=mk('ellipse',{rx:rig==='quad'?86:64,ry:16,cy:2,fill:'none',stroke:'#e8505b','stroke-width':4,'stroke-dasharray':'14 8',opacity:0},el);
  const corpo=document.getElementById('tpl_'+tipo).cloneNode(true);corpo.removeAttribute('id');el.appendChild(corpo);
  const cab=mk('g',{transform:`translate(0 ${-(altura+(rig==='quad'?40:62))})`},el);
  const rotulo=mk('text',{y:-8,'text-anchor':'middle','font-family':'Alegreya Sans, sans-serif','font-size':17,'font-weight':700,fill:'#f1e6d0',stroke:'#1a1422','stroke-width':4,'paint-order':'stroke'},cab);
  mk('rect',{x:-40,y:0,width:80,height:9,rx:4,fill:'#1a1422'},cab);
  const vida=mk('rect',{x:-38,y:2,width:76,height:5,rx:2.5,fill:'#e8505b'},cab);
  const partes={};
  corpo.querySelectorAll('[data-part]').forEach(g=>{const [px,py]=g.dataset.pivot.split(',').map(Number);partes[g.dataset.part]={el:g,px,py};});
  const brilhos=[...corpo.querySelectorAll('[data-part="arma"] circle')].filter(c=>+c.getAttribute('r')>8).map(c=>[c,+c.getAttribute('r')]);
  const p=lugarLivre({rig},x,y);
  const a={id:idSeq,tipo,rig,nome,papel,el,corpo,sombra,anel,cab,rotulo,vida,partes,brilhos,altura,x:p.x,y:p.y,casa:{x:p.x,y:p.y},dir:dir||1,
    s:altura/(rig==='quad'?183:180),t:Math.random()*6,fase:0,andar:0,vel:0,hpMax:papel==='monstro'?160:200,hp:0,mp:100,vivo:true,acao:null,exausto:0,aggro:null,proxAtaque:0,morto:0};
  a.hp=a.hpMax; rotulo.textContent=papel==='pvp'?nome+' · PvP':papel==='monstro'?nome:'';
  if(papel==='jogador')cab.style.display='none';
  ocupar(a); atores.push(a); return a;
}
function R(a,p,ang){const q=a.partes[p];return q&&ang?`rotate(${ang.toFixed(2)} ${q.px} ${q.py})`:'';}
function por(a,p,tr){const q=a.partes[p];if(q)q.el.setAttribute('transform',tr);}
function posar(a,P){
  const v=k=>P[k]||0;
  if(a.rig==='quad'){
    const body=`translate(${v('dx').toFixed(2)} ${v('dy').toFixed(2)}) `+R(a,'tronco',v('tl'));
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
function animar(a,dt,t){
  a.t+=dt*(2*PI/1.4);
  a.andar+=((a.vel>5?1:0)-a.andar)*Math.min(1,dt*8);
  a.fase+=dt*2*PI*(a.vel/(a.rig==='quad'?230:250));
  let P=mix(a.rig==='quad'?qParado(a.t):bParado(a.t),a.rig==='quad'?qAndando(a.fase):bAndando(a.fase),a.andar);
  if(a.acao){const f=(t-a.acao.t0)*a.acao.anim.fps;if(f>=a.acao.anim.n)a.acao=null;else Object.assign(P,keys(a.acao.anim.tab,f));}
  if(a.vivo||!a.morto)posar(a,P);
  const cx=a.rig==='quad'?138:128;
  a.corpo.setAttribute('transform',`scale(${a.dir*a.s} ${a.s}) translate(${-cx} -240)`);
  a.el.setAttribute('transform',`translate(${a.x.toFixed(1)} ${a.y.toFixed(1)})`);
  a.vida.setAttribute('width',Math.max(0,76*a.hp/a.hpMax).toFixed(1));
  a.el.dataset.y=a.y;
  let n;
  while((n=a.el.previousElementSibling)&&+n.dataset.y>a.y) cena.insertBefore(a.el,n);
  while((n=a.el.nextElementSibling)&&+n.dataset.y<a.y) cena.insertBefore(n,a.el);
}

// ================= runas
const TW=72, TH=34; // 1 "sqm" de runa = 3x2 células da grade lógica
const FORMAS={um:[[0,0]],cruz:[[0,0],[1,0],[-1,0],[0,1],[0,-1]],
  gfb:(()=>{const o=[];[3,5,7,7,7,5,3].forEach((n,r)=>{for(let k=0;k<n;k++)o.push([k-(n-1)/2,r-3]);});return o;})()};
const RUNAS=[
  {id:'raio',nome:'Raio',tecla:'1',mana:18,alcance:620,dano:[40,55],forma:'um',cor:'#8be04a'},
  {id:'explosao',nome:'Explosão',tecla:'2',mana:30,alcance:560,dano:[28,40],forma:'cruz',cor:'#ff8a3a'},
  {id:'gfb',nome:'Bola de fogo',tecla:'3',mana:40,alcance:560,dano:[20,32],forma:'gfb',cor:'#ff5a2a'},
  {id:'cura',nome:'Cura',tecla:'4',mana:24,cura:[42,60],forma:null,cor:'#7fe0ff'}];
const EXAUSTO=1.0;
const tileDe=(x,y)=>[Math.floor(x/TW),Math.floor((y-FACH)/TH)];
const centro=(ti,tj)=>({x:(ti+.5)*TW,y:FACH+(tj+.5)*TH});
function areaTiles(runa,ti,tj){return FORMAS[runa.forma].map(([a,b])=>[ti+a,tj+b]).filter(([i,j])=>{
  if(i<0||j<0||i*TW>=WW||FACH+j*TH>=BASE)return false;const c=centro(i,j),ci=cx_(c.x),cj=cy_(c.y);return !(ci>=0&&cj>=0&&ci<GX&&cj<GY&&parede[cj*GX+ci]);});}
function atingidos(tiles,exceto){const k=new Set();for(const [ti,tj] of tiles)for(let j=tj*2;j<tj*2+2;j++)for(let i=ti*3;i<ti*3+3;i++)k.add(j*GX+i);
  return atores.filter(a=>a!==exceto&&a.vivo&&a.cel&&a.cel.some(c=>k.has(c)));}
function validar(c,runa,ti,tj){const p=centro(ti,tj);if(dist(c,p)>runa.alcance)return 'Fora de alcance';if(!visao(c,p))return 'Sem linha de visão';return '';}
let projeteis=[];
const peito=a=>({x:a.x,y:a.y-a.altura*0.55});
const mao=a=>({x:a.x+a.dir*a.altura*0.35,y:a.y-a.altura*0.72});
function aviso(txt){const e=$('.msg');e.textContent=txt;e.classList.add('on');clearTimeout(aviso.t);aviso.t=setTimeout(()=>e.classList.remove('on'),1100);}
function usarRuna(c,runa,pt,silencioso){
  const t=agora(), falha=m=>{if(!silencioso)aviso(m);return false;};
  if(!c.vivo)return false;
  if(t<c.exausto)return falha('Exausto');
  if(c.mp<runa.mana)return falha('Mana insuficiente');
  let ti,tj;
  if(runa.forma){[ti,tj]=tileDe(pt.x,pt.y);const erro=validar(c,runa,ti,tj);if(erro)return falha(erro);c.dir=centro(ti,tj).x>c.x?1:-1;}
  c.mp-=runa.mana; c.exausto=t+EXAUSTO;
  if(c.rig!=='quad')c.acao={anim:CONJURAR,t0:t};
  if(!runa.forma){curar(c,Math.round(rand(...runa.cura)));brilhoCura(c);return true;}
  setTimeout(()=>lancar(c,runa,ti,tj),180);
  return true;
}
function lancar(c,runa,ti,tj){
  if(!c.vivo)return;
  const o=mao(c), d=centro(ti,tj), g=mk('g',{},efx), big=runa.forma!=='um';
  mk('circle',{r:big?34:26,fill:`url(#${big?'luz':'luzverde'})`},g);
  mk('circle',{r:big?13:9,fill:runa.cor,stroke:'#1a1422','stroke-width':3},g);
  mk('circle',{r:big?5:3.5,fill:'#fffbe8'},g);
  projeteis.push({g,x:o.x,y:o.y,tx:d.x,ty:d.y-(big?20:30),c,runa,tiles:areaTiles(runa,ti,tj),rastro:0});
}
function atingir(p){
  const {c,runa,tiles}=p;
  for(const [ti,tj] of tiles){const q=centro(ti,tj);runa.forma==='um'?faisca({x:q.x,y:q.y-30},runa.cor):chama(q.x,q.y,runa.cor);}
  const alvos=atingidos(tiles,c);
  if(!alvos.length&&runa.forma==='um'&&c===jogador)aviso('Errou: ninguém naquele ponto');
  for(const a of alvos)dano(a,Math.round(rand(...runa.dano)),c);
}
function chama(x,y,cor){const g=mk('g',{transform:`translate(${x} ${y})`},efx);
  mk('rect',{x:-TW/2+3,y:-TH/2+2,width:TW-6,height:TH-4,rx:8,fill:cor,opacity:0.45},g);
  for(let k=0;k<3;k++){const fx=rand(-22,22),h=rand(34,60);
    mk('path',{d:`M${fx-9},0 C${fx-11},${-h*0.5} ${fx-2},${-h*0.7} ${fx},${-h} C${fx+3},${-h*0.6} ${fx+11},${-h*0.45} ${fx+9},0 Z`,fill:k%2?'#ffd98a':cor,stroke:'#1a1422','stroke-width':2.2},g);}
  mk('circle',{r:40,cy:-20,fill:'url(#luz)'},g);
  efeitos.push({g,t0:agora(),dur:0.6,escala:true});}
function dano(a,v,de){
  if(!a.vivo)return; a.hp-=v; numero(a,'-'+v,'#ff6a5a');
  if(a!==jogador&&de)a.aggro=de;
  if(a.hp<=0){a.hp=0;morrer(a);}
}
function curar(a,v){a.hp=Math.min(a.hpMax,a.hp+v);numero(a,'+'+v,'#7fe0a0');}
function morrer(a){
  a.vivo=false;a.morto=agora();a.aggro=null;ocupar(a);a.el.style.opacity=0.35;a.el.style.transition='opacity .6s';
  for(const o of atores)if(o.aggro===a)o.aggro=null;
  if(a===jogador){$('.morte').hidden=false;}
}
function renascer(a){
  const p=a===jogador?INICIO:a.casa, q=lugarLivre(a,p.x,p.y);
  a.x=q.x;a.y=q.y;a.hp=a.hpMax;a.mp=100;a.vivo=true;a.morto=0;a.el.style.opacity=1;ocupar(a);
  if(a===jogador){$('.morte').hidden=true;cam.x=a.x;cam.y=a.y;}
}
function numero(a,txt,cor){const g=mk('text',{x:a.x+rand(-16,16),y:a.y-a.altura-20,'text-anchor':'middle','font-family':'IM Fell English SC, Georgia, serif','font-size':34,fill:cor,stroke:'#1a1422','stroke-width':5,'paint-order':'stroke'},efx);
  g.textContent=txt;efeitos.push({g,t0:agora(),dur:0.9,sobe:true,y0:+g.getAttribute('y')});}
function faisca(p,cor){const g=mk('g',{transform:`translate(${p.x} ${p.y})`},efx);
  for(let i=0;i<10;i++){const ang=i*PI/5;mk('path',{d:`M${Math.cos(ang)*10},${Math.sin(ang)*10} L${Math.cos(ang)*34},${Math.sin(ang)*34}`,stroke:cor,'stroke-width':5,'stroke-linecap':'round'},g);}
  mk('circle',{r:30,fill:'url(#luzverde)'},g);efeitos.push({g,t0:agora(),dur:0.35,escala:true});}
function explosao(x,y,r){const g=mk('g',{transform:`translate(${x} ${y})`},efx);
  mk('ellipse',{rx:r,ry:r*0.72,fill:'#ff8a3a',opacity:0.35,stroke:'#ffd98a','stroke-width':6},g);
  mk('ellipse',{rx:r*0.6,ry:r*0.43,fill:'#ffd98a',opacity:0.5},g);
  for(let i=0;i<14;i++){const ang=rand(0,2*PI),d=rand(10,r*0.9);mk('circle',{cx:Math.cos(ang)*d,cy:Math.sin(ang)*d*0.72-rand(10,90),r:rand(6,16),fill:i%2?'#ffb860':'#e8505b',stroke:'#1a1422','stroke-width':2},g);}
  efeitos.push({g,t0:agora(),dur:0.55,escala:true});}
function brilhoCura(a){const g=mk('g',{},efx);for(let i=0;i<12;i++)mk('circle',{cx:a.x+rand(-50,50),cy:a.y-rand(0,a.altura),r:rand(3,7),fill:'#7fe0ff',stroke:'#1a1422','stroke-width':1.5},g);
  mk('ellipse',{cx:a.x,cy:a.y,rx:70,ry:20,fill:'none',stroke:'#7fe0ff','stroke-width':5},g);efeitos.push({g,t0:agora(),dur:0.8,sobe:true,y0:0});}
let efeitos=[];
function atualizarEfeitos(dt,t){
  for(const p of projeteis){const dx=p.tx-p.x,dy=p.ty-p.y,d=Math.hypot(dx,dy),v=1050*dt;
    if(d<=v+8){p.feito=true;p.g.remove();atingir(p);continue;}
    p.x+=dx/d*v;p.y+=dy/d*v;p.g.setAttribute('transform',`translate(${p.x.toFixed(1)} ${p.y.toFixed(1)})`);
    p.rastro+=dt;if(p.rastro>0.03){p.rastro=0;const r=mk('circle',{cx:p.x,cy:p.y,r:7,fill:p.runa.cor,opacity:0.6},efx);efeitos.push({g:r,t0:t,dur:0.25});}}
  projeteis=projeteis.filter(p=>!p.feito);
  for(const e of efeitos){const k=(t-e.t0)/e.dur;if(k>=1){e.g.remove();e.feito=true;continue;}
    e.g.setAttribute('opacity',(1-k).toFixed(2));
    if(e.sobe&&e.g.tagName==='text')e.g.setAttribute('y',(e.y0-60*k).toFixed(1));
    if(e.sobe&&e.g.tagName==='g')e.g.setAttribute('transform',`translate(0 ${(-40*k).toFixed(1)})`);
    if(e.escala){const tr=e.g.getAttribute('transform').split(' scale')[0];e.g.setAttribute('transform',`${tr} scale(${(0.6+0.6*k).toFixed(2)})`);}}
  efeitos=efeitos.filter(e=>!e.feito);
}

// ================= IA
function ia(n,dt,t){
  if(!n.vivo){if(t-n.morto>6)renascer(n);return;}
  n.mp=Math.min(100,n.mp+8*dt);
  const ox=n.x,oy=n.y;
  if(n.papel==='monstro'){
    if(!n.aggro&&jogador.vivo&&dist(n,jogador)<300)n.aggro=jogador;
    const alvo=n.aggro;
    if(alvo&&(!alvo.vivo||dist(n,n.casa)>1300)){n.aggro=null;}
    if(n.aggro){const d=dist(n,alvo);
      if(d>105){const dx=alvo.x-n.x,dy=alvo.y-n.y,m=Math.hypot(dx,dy);mover(n,dx/m*230*dt,dy/m*230*0.72*dt);}
      n.dir=alvo.x>n.x?1:-1;
      if(d<=130&&t>n.proxAtaque){n.proxAtaque=t+1.4;n.acao={anim:MORDER,t0:t};setTimeout(()=>{if(n.vivo&&alvo.vivo&&dist(n,alvo)<150)dano(alvo,Math.round(rand(8,14)),n);},260);}
    }else{const alvoX=n.casa.x+Math.sin(t/2.6)*260,dx=alvoX-n.x;if(Math.abs(dx)>4)mover(n,Math.sign(dx)*Math.min(Math.abs(dx),150*dt),(n.casa.y-n.y)*Math.min(1,dt*2));}
  }else{
    const alvo=n.aggro;
    if(alvo&&!alvo.vivo)n.aggro=null;
    if(n.aggro){const d=dist(n,alvo),dx=alvo.x-n.x,dy=alvo.y-n.y,m=Math.hypot(dx,dy)||1;
      if(d>430)mover(n,dx/m*220*dt,dy/m*220*0.72*dt);else if(d<230)mover(n,-dx/m*180*dt,-dy/m*180*0.72*dt);
      n.dir=alvo.x>n.x?1:-1;
      if(t>n.proxAtaque){n.proxAtaque=t+rand(1.8,2.6);
        const r=Math.random();
        if(n.hp<n.hpMax*0.4&&n.mp>=RUNAS[3].mana)usarRuna(n,RUNAS[3],null,true);
        else usarRuna(n,r<0.5?RUNAS[0]:r<0.75?RUNAS[1]:RUNAS[2],{x:alvo.x,y:alvo.y},true);}
    }else if(jogador.vivo&&Math.hypot(n.x-jogador.x,n.y-jogador.y)<420)n.dir=jogador.x>n.x?1:-1;
  }
  n.vel=Math.hypot(n.x-ox,(n.y-oy)/0.72)/Math.max(dt,1e-4);
  if(Math.abs(n.x-ox)>0.3&&!n.aggro)n.dir=n.x>ox?1:-1;
}

// ================= estado / jogo
const FALAS={ninja:'Cuidado: aqui tem trap. Me ataque para testar o PvP.',medusa:'Não olhe nos meus olhos, viajante.',necromante:'O Cavalo Babão nunca para de babar. Nem depois da morte.'};
const LUGARES={ninja:[1180,960,-1],medusa:[3470,930,1],necromante:[3700,1180,1],cachorro:[2500,1200,1]};
let atual='necromante', regiaoAtual='', chegou=false;
function iniciar(tipo,salvo){
  atores.forEach(a=>a.el.remove()); atores=[]; ocup.clear(); projeteis=[]; efeitos.forEach(e=>e.g.remove()); efeitos=[];
  chegou=false; $('.aviso').hidden=true; $('.morte').hidden=true;
  const pos=salvo||INICIO;
  jogador=criarAtor(tipo,pos.x,pos.y,1,'jogador');
  for(const k of Object.keys(PERS)) if(k!==tipo){const [x,y,d]=LUGARES[k];const n=criarAtor(k,x,y,d,k==='cachorro'?'monstro':'pvp');n.fala=FALAS[k]||'';}
  if(tipo==='cachorro'){const [x,y,d]=LUGARES.cachorro;}
  document.querySelectorAll('.escolha button').forEach(b=>b.setAttribute('aria-pressed',b.dataset.p===tipo));
  atual=tipo; regiaoAtual=''; cam.x=jogador.x; cam.y=jogador.y; desenharGrade();
}

// ================= entrada
const teclas=new Set(); let destino=null, joy=null, mostrarGrade=false, mira=null, ponteiro=null;
addEventListener('keydown',e=>{const k=e.key.toLowerCase();
  if(['arrowup','arrowdown','arrowleft','arrowright','w','a','s','d','shift'].includes(k)){teclas.add(k);destino=null;e.preventDefault();}
  const r=RUNAS.find(r=>r.tecla===k);if(r){escolherRuna(r);e.preventDefault();}
  if(k==='escape')mira=null;
  if(k==='g'){mostrarGrade=!mostrarGrade;desenharGrade();}
});
addEventListener('keyup',e=>teclas.delete(e.key.toLowerCase()));
addEventListener('blur',()=>teclas.clear());
const joyEl=$('.joy');
jogo.addEventListener('pointerdown',e=>{
  if(e.target.closest('button'))return;
  jogo.focus();
  if(mira){if(e.button===2){mira=null;return;}const pt=telaParaMundo(e.clientX,e.clientY);ponteiro=pt;if(usarRuna(jogador,mira,pt))mira=null;return;}
  if(e.pointerType==='mouse'){if(e.button===0)destino=telaParaMundo(e.clientX,e.clientY);return;}
  joy={id:e.pointerId,x0:e.clientX,y0:e.clientY,dx:0,dy:0};joyEl.hidden=false;joyEl.style.left=e.clientX+'px';joyEl.style.top=e.clientY+'px';joyEl.firstElementChild.style.transform='';
  jogo.setPointerCapture(e.pointerId);});
jogo.addEventListener('contextmenu',e=>{e.preventDefault();mira=null;});
function escolherRuna(r){if(!r.forma){usarRuna(jogador,r,null);mira=null;return;}mira=mira===r?null:r;}
jogo.addEventListener('pointermove',e=>{if(e.pointerType==='mouse'||mira)ponteiro=telaParaMundo(e.clientX,e.clientY);if(!joy||e.pointerId!==joy.id)return;let dx=e.clientX-joy.x0,dy=e.clientY-joy.y0;const d=Math.hypot(dx,dy),m=50;if(d>m){dx*=m/d;dy*=m/d;}
  joy.dx=dx/m;joy.dy=dy/m;joyEl.firstElementChild.style.transform=`translate(${dx}px,${dy}px)`;});
const soltar=e=>{if(joy&&e.pointerId===joy.id){joy=null;joyEl.hidden=true;}};
jogo.addEventListener('pointerup',soltar);jogo.addEventListener('pointercancel',soltar);
document.querySelectorAll('.runa').forEach(b=>b.addEventListener('click',()=>{escolherRuna(RUNAS[+b.dataset.r]);jogo.focus();}));
$('#btn-grade').addEventListener('click',()=>{mostrarGrade=!mostrarGrade;desenharGrade();jogo.focus();});

// ================= grade (debug)
const gradeEst=$('#grade'), gradeOcc=$('#gradeOcc');
function desenharGrade(){
  gradeEst.innerHTML='';gradeOcc.innerHTML='';$('#btn-grade').setAttribute('aria-pressed',mostrarGrade);
  if(!mostrarGrade)return;
  let d='';for(let j=0;j<GY;j++)for(let i=0;i<GX;i++)if(bloq[j*GX+i])d+=`M${i*CW},${GY0+j*CH}h${CW}v${CH}h-${CW}z`;
  mk('rect',{x:0,y:GY0,width:WW,height:BASE-GY0,fill:'url(#celulas)'},gradeEst);
  mk('path',{d,fill:'#e8505b',opacity:0.4},gradeEst);
}
function grade_ocupada(){if(!mostrarGrade)return;let d='';for(const k of ocup.keys()){const i=k%GX,j=(k-i)/GX;d+=`M${i*CW},${GY0+j*CH}h${CW}v${CH}h-${CW}z`;}
  gradeOcc.innerHTML=`<path d="${d}" fill="#8be04a" opacity="0.45"/>`;}

// ================= câmera / HUD
const cam={x:INICIO.x,y:INICIO.y,z:1,w:1920,h:1080};
function telaParaMundo(cx,cy){const r=svg.getBoundingClientRect();return{x:cam.x-cam.w/2+(cx-r.left)/cam.z,y:cam.y-cam.h/2+(cy-r.top)/cam.z};}
function atualizarCamera(dt){
  const r=svg.getBoundingClientRect();
  cam.z=Math.max(0.5,Math.min(1.25,r.height/1000)); cam.w=r.width/cam.z; cam.h=r.height/cam.z;
  const k=Math.min(1,dt*5); cam.x+=(jogador.x-cam.x)*k; cam.y+=(jogador.y-120-cam.y)*k;
  const x0=Math.max(0,Math.min(WW-cam.w,cam.x-cam.w/2)), y0=Math.max(TOPO,Math.min(BASE-cam.h,cam.y-cam.h/2));
  svg.setAttribute('viewBox',`${x0.toFixed(1)} ${y0.toFixed(1)} ${cam.w.toFixed(1)} ${cam.h.toFixed(1)}`);
}
function regiao(x){return x<1880?['Praça Tiradentes','Catedral Basílica']:x<2160?['Travessia','Atravessando a rua']:x<3260?['Rua Claudino dos Santos','Casario histórico']:['Largo da Ordem','Cavalo Babão'];}
let tituloTimer=0;
function mostrarTitulo(n,s){const e=$('.titulo');e.innerHTML=`${n}<small>${s}</small>`;e.classList.add('on');clearTimeout(tituloTimer);tituloTimer=setTimeout(()=>e.classList.remove('on'),2400);}
$('#recomecar').addEventListener('click',()=>{iniciar(atual);jogo.focus();});
document.querySelectorAll('.escolha button').forEach(b=>b.addEventListener('click',()=>{iniciar(b.dataset.p,{x:jogador.x,y:jogador.y});jogo.focus();}));
const alcanceEl=$('#alcance');
function hud(t){
  $('#hp i').style.width=(100*jogador.hp/jogador.hpMax)+'%';$('#hp span').textContent=`${Math.ceil(jogador.hp)} / ${jogador.hpMax}`;
  $('#mp i').style.width=jogador.mp+'%';$('#mp span').textContent=`${Math.floor(jogador.mp)} / 100`;
  const ex=Math.max(0,jogador.exausto-t);
  document.querySelectorAll('.runa').forEach(b=>{const r=RUNAS[+b.dataset.r];b.style.setProperty('--cd',(ex/EXAUSTO*100).toFixed(0)+'%');
    b.classList.toggle('sem',jogador.mp<r.mana);b.setAttribute('aria-pressed',mira===r);});
  const miraEl=$('#mira'), dicaMira=$('.mirando');
  if(mira&&jogador.vivo){
    alcanceEl.setAttribute('opacity',0.6);alcanceEl.setAttribute('cx',jogador.x);alcanceEl.setAttribute('cy',jogador.y);
    alcanceEl.setAttribute('rx',mira.alcance);alcanceEl.setAttribute('ry',mira.alcance*0.72);alcanceEl.setAttribute('stroke',mira.cor);
    dicaMira.hidden=false;dicaMira.querySelector('b').textContent=mira.nome;jogo.style.cursor='cell';
    if(ponteiro){const [ti,tj]=tileDe(ponteiro.x,ponteiro.y),erro=validar(jogador,mira,ti,tj),cor=erro?'#e8505b':mira.cor;let d='';
      for(const [i,j] of areaTiles(mira,ti,tj))d+=`M${i*TW+2},${FACH+j*TH+2}h${TW-4}v${TH-4}h${-(TW-4)}z`;
      miraEl.innerHTML=`<path d="${d}" fill="${cor}" fill-opacity="0.32" stroke="${cor}" stroke-width="3"/>`;}
  }else{alcanceEl.setAttribute('opacity',0);miraEl.innerHTML='';dicaMira.hidden=true;jogo.style.cursor='crosshair';}
  let html='';
  for(const n of atores){if(n===jogador||!n.vivo||n.aggro||!n.fala)continue;const d=Math.hypot(n.x-jogador.x,(n.y-jogador.y)*1.4);
    if(d<230){const w=Math.max(170,n.fala.length*8.6+28),h=46,top=n.y-n.altura-96,x=n.x-w/2;
      html+=`<g><rect x="${x}" y="${top-h}" width="${w}" height="${h}" rx="14" fill="#f1e6d0" stroke="#1a1422" stroke-width="3"/>`+
        `<path d="M${n.x-10},${top-1} L${n.x+10},${top-1} L${n.x},${top+14} Z" fill="#f1e6d0" stroke="#1a1422" stroke-width="3" stroke-linejoin="round"/>`+
        `<rect x="${n.x-12}" y="${top-4}" width="24" height="6" fill="#f1e6d0"/>`+
        `<text x="${n.x}" y="${top-h/2+6}" text-anchor="middle" font-family="Alegreya Sans, sans-serif" font-size="17" font-weight="500" fill="#1a1422">${n.fala}</text></g>`;}}
  falas.innerHTML=html;
}

// ================= laço
let ultimo=performance.now();
function quadro(ms){
  const dt=Math.min(0.05,(ms-ultimo)/1000); ultimo=ms; const t=ms/1000;
  let vx=0,vy=0;
  if(jogador.vivo){
    if(teclas.has('arrowleft')||teclas.has('a'))vx-=1; if(teclas.has('arrowright')||teclas.has('d'))vx+=1;
    if(teclas.has('arrowup')||teclas.has('w'))vy-=1; if(teclas.has('arrowdown')||teclas.has('s'))vy+=1;
    if(joy){vx=joy.dx;vy=joy.dy;}
    if(destino&&!vx&&!vy){const dx=destino.x-jogador.x,dy=destino.y-jogador.y,d=Math.hypot(dx,dy);if(d<8)destino=null;else{vx=dx/d;vy=dy/d;}}
  }else if(t-jogador.morto>3)renascer(jogador);
  const mag=Math.hypot(vx,vy); if(mag>1){vx/=mag;vy/=mag;}
  const vmax=teclas.has('shift')?420:260, px=jogador.x, py=jogador.y;
  if(vx||vy){if(!mover(jogador,vx*vmax*dt,vy*vmax*0.72*dt)&&destino)destino=null;}
  jogador.vel=Math.hypot(jogador.x-px,(jogador.y-py)/0.72)/Math.max(dt,1e-4);
  if(Math.abs(vx)>0.15&&!jogador.acao)jogador.dir=vx>0?1:-1;
  jogador.mp=Math.min(100,jogador.mp+7*dt); if(jogador.vivo)jogador.hp=Math.min(jogador.hpMax,jogador.hp+1.2*dt);
  for(const n of atores)if(n!==jogador)ia(n,dt,t);
  for(const a of atores)animar(a,dt,t);
  atualizarEfeitos(dt,t); atualizarCamera(dt); hud(t); grade_ocupada();
  const [nome,sub]=regiao(jogador.x);
  if(nome!==regiaoAtual){regiaoAtual=nome;$('.local').textContent=nome;mostrarTitulo(nome,sub);}
  const f=Math.max(0,Math.min(1,(jogador.x-INICIO.x)/(FONTE.x-INICIO.x)));
  $('.barra i').style.width=(f*100)+'%'; $('.barra b').style.left=(f*100)+'%';
  if(!chegou&&jogador.vivo&&Math.hypot(jogador.x-FONTE.x,(jogador.y-FONTE.y)*1.2)<340){chegou=true;$('.aviso').hidden=false;}
  requestAnimationFrame(quadro);
}
const hot=window.claude&&window.claude.hot;
if(hot&&hot.snapshot) hot.snapshot(()=>({tipo:atual,x:jogador&&jogador.x,y:jogador&&jogador.y}));
function start(d){d=d||{};iniciar(PERS[d.tipo]?d.tipo:'necromante',d.x?{x:d.x,y:d.y}:null);requestAnimationFrame(quadro);}
if(hot&&hot.ready) hot.ready(start); else start(hot&&hot.data);
})();
</script>
"""

CELULAS = '<pattern id="celulas" width="24" height="17" patternUnits="userSpaceOnUse" y="520"><path d="M24,0 L0,0 L0,17" fill="none" stroke="#f1e6d0" stroke-width="1.2" opacity="0.55"/></pattern>'

def pagina():
    chao, objs, frente, glows = gerar_mundo()
    corpo = f"""
<div id="jogo" tabindex="0" aria-label="Protótipo: ande da Catedral até o Cavalo Babão e lance runas clicando no chão">
<svg id="mundo" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1920 1080" preserveAspectRatio="xMidYMid slice">
{DEFS.replace("</defs>", EXTRA + CELULAS + templates() + "</defs>")}
<g id="chao">{chao}</g>
<g id="grade"></g><g id="gradeOcc"></g><g id="mira"></g>
<ellipse id="alcance" cx="0" cy="0" rx="560" ry="403" fill="none" stroke="#8be04a" stroke-width="5" stroke-dasharray="18 12" opacity="0"/>
<g id="objetos">{objs}</g>
<g id="efeitos"></g>
<g id="frente">{frente}</g>
<g id="luzes" style="mix-blend-mode:screen">{glows}</g>
<g id="falas"></g>
</svg>
<div class="vinheta"></div>
<div class="hud">
 <div class="topo">
  <div class="trilha"><div class="local">Praça Tiradentes</div><div class="barra"><i></i><b></b></div>
   <div class="marcos"><span>Catedral</span><span>Cavalo Babão</span></div>
   <div class="status"><div class="st" id="hp"><i></i><span>200 / 200</span></div><div class="st" id="mp"><i></i><span>100 / 100</span></div></div></div>
  <div class="escolha" role="group" aria-label="Personagem">
   <button type="button" id="p-necromante" data-p="necromante" aria-pressed="true">Necromante</button>
   <button type="button" id="p-medusa" data-p="medusa" aria-pressed="false">Medusa</button>
   <button type="button" id="p-ninja" data-p="ninja" aria-pressed="false">Ninja</button>
   <button type="button" id="p-cachorro" data-p="cachorro" aria-pressed="false">Cachorro zumbi</button>
  </div>
 </div>
 <div class="dica">WASD ou setas andam · 1 2 3 escolhem a runa e o clique no chão lança · 4 cura · Esc ou botão direito cancela · G mostra a grade</div>
 <div class="msg" role="status"></div>
 <div class="mirando" hidden>Mirando <b></b> · clique no chão onde está o alvo</div>
 <div class="runas" role="group" aria-label="Runas">
  <button type="button" class="runa" id="r-raio" data-r="0" aria-pressed="false"><kbd>1</kbd><span>Raio</span><small>1 quadro · 18 mana</small></button>
  <button type="button" class="runa" id="r-explosao" data-r="1" aria-pressed="false"><kbd>2</kbd><span>Explosão</span><small>cruz · 30 mana</small></button>
  <button type="button" class="runa" id="r-gfb" data-r="2" aria-pressed="false"><kbd>3</kbd><span>Bola de fogo</span><small>raio 3 · 40 mana</small></button>
  <button type="button" class="runa" id="r-cura" data-r="3" aria-pressed="false"><kbd>4</kbd><span>Cura</span><small>você · 24 mana</small></button>
  <button type="button" class="util" id="btn-grade" aria-pressed="false"><kbd>G</kbd><span>Grade</span></button>
 </div>
 <div class="morte" hidden><strong>Você morreu</strong><span>Renascendo na Catedral…</span></div>
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
