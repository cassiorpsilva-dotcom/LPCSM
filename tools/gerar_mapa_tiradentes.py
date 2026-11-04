#!/usr/bin/env python3
"""
Mapa parallax de teste para RPG Maker MZ: Praça Tiradentes (Curitiba) -> Largo da Ordem (Cavalo Babão).
Inspirado no trajeto real, com layout simplificado para jogo (não é uma planta exata).

Uso: python3 tools/gerar_mapa_tiradentes.py
Gera em rpgmaker/praca_tiradentes/:
  fonte/praca_tiradentes.svg, fonte/praca_tiradentes_topo.svg   arte (chão e camada acima do personagem)
  img/parallaxes/!praca_tiradentes.png, !praca_tiradentes_topo.png  (renderizado com tools/svg_para_png.js)
  data/Map002.json                                               mapa 25x40 com colisão (região 1) e eventos
  js/plugins/MapaParalaxe.js                                     plugin (colisão por região + camada superior)
"""
import os, json, subprocess

T = 48               # tamanho do tile no MZ
W, H = 25, 40        # mapa em tiles
PW, PH = W * T, H * T
OL = "#1e1a24"
RAIZ = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "rpgmaker", "praca_tiradentes")

# ------------------------------------------------------------------ primitivas SVG
def R(x, y, w, h, fill, rx=0, sw=3, op=None):
    o = f' opacity="{op}"' if op else ""
    st = f' stroke="{OL}" stroke-width="{sw}"' if sw else ""
    return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" fill="{fill}"{st}{o}/>\n'

def Pth(d, fill, sw=3, op=None, extra=""):
    o = f' opacity="{op}"' if op else ""
    st = f' stroke="{OL}" stroke-width="{sw}" stroke-linejoin="round"' if sw else ""
    return f'<path d="{d}" fill="{fill}"{st}{o}{extra}/>\n'

def L(d, col, w, op=None, cap="round"):
    o = f' opacity="{op}"' if op else ""
    return f'<path d="{d}" fill="none" stroke="{col}" stroke-width="{w}" stroke-linecap="{cap}" stroke-linejoin="round"{o}/>\n'

def C(cx, cy, r, fill, sw=3, op=None):
    o = f' opacity="{op}"' if op else ""
    st = f' stroke="{OL}" stroke-width="{sw}"' if sw else ""
    return f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="{fill}"{st}{o}/>\n'

def E(cx, cy, rx, ry, fill, sw=0, op=None):
    o = f' opacity="{op}"' if op else ""
    st = f' stroke="{OL}" stroke-width="{sw}"' if sw else ""
    return f'<ellipse cx="{cx}" cy="{cy}" rx="{rx}" ry="{ry}" fill="{fill}"{st}{o}/>\n'

def TX(x, y, s, size=14, fill="#f4efe2", anchor="middle"):
    return (f'<text x="{x}" y="{y}" font-family="Georgia, serif" font-weight="bold" font-size="{size}" '
            f'fill="{fill}" text-anchor="{anchor}">{s}</text>\n')

def sombra(cx, cy, rx, ry):
    return E(cx, cy, rx, ry, "#000000", 0, 0.22)

DEFS = """<defs>
<pattern id="petit" width="96" height="96" patternUnits="userSpaceOnUse">
 <rect width="96" height="96" fill="#e2dccd"/>
 <path d="M0,10 L96,10 M0,34 L96,34 M0,58 L96,58 M0,82 L96,82 M12,0 L12,96 M36,0 L36,96 M60,0 L60,96 M84,0 L84,96" stroke="#cfc8b6" stroke-width="1.2"/>
 <path d="M24,14 C34,22 34,36 24,44 C14,36 14,22 24,14 Z" fill="#3c3b42"/>
 <path d="M72,62 C82,70 82,84 72,92 C62,84 62,70 72,62 Z" fill="#3c3b42"/>
 <path d="M24,20 L24,40 M18,27 L30,27 M18,34 L30,34" stroke="#e2dccd" stroke-width="1.6"/>
 <path d="M72,68 L72,88 M66,75 L78,75 M66,82 L78,82" stroke="#e2dccd" stroke-width="1.6"/>
 <circle cx="72" cy="22" r="3" fill="#7d7a80"/><circle cx="24" cy="72" r="3" fill="#7d7a80"/>
</pattern>
<pattern id="pedra" width="32" height="24" patternUnits="userSpaceOnUse">
 <rect width="32" height="24" fill="#6f6861"/>
 <rect x="1.5" y="1.5" width="13" height="9" rx="3" fill="#958c82"/><rect x="17.5" y="1.5" width="13" height="9" rx="3" fill="#8b8279"/>
 <rect x="-6.5" y="13.5" width="13" height="9" rx="3" fill="#8b8279"/><rect x="9.5" y="13.5" width="13" height="9" rx="3" fill="#9a9187"/>
 <rect x="25.5" y="13.5" width="13" height="9" rx="3" fill="#8b8279"/>
</pattern>
<pattern id="calcada" width="24" height="24" patternUnits="userSpaceOnUse">
 <rect width="24" height="24" fill="#bdb6a8"/><path d="M0,12 L24,12 M12,0 L12,12 M0,0 L0,24" stroke="#a49d90" stroke-width="1.5"/>
</pattern>
<pattern id="grama" width="40" height="40" patternUnits="userSpaceOnUse">
 <rect width="40" height="40" fill="#5f8a3e"/>
 <path d="M6,12 L8,6 L10,12 M26,30 L28,24 L30,30 M30,8 L32,3 L34,8 M12,32 L14,27 L16,32" stroke="#4a6e30" stroke-width="2" fill="none"/>
</pattern>
<pattern id="telha" width="20" height="14" patternUnits="userSpaceOnUse">
 <rect width="20" height="14" fill="#a8553a"/><path d="M0,14 C0,6 10,6 10,14 M10,14 C10,6 20,6 20,14 M-10,7 C-10,-1 0,-1 0,7 M0,7 C0,-1 10,-1 10,7 M10,7 C10,-1 20,-1 20,7" stroke="#7e3b28" stroke-width="1.6" fill="none"/>
</pattern>
<pattern id="ardosia" width="16" height="12" patternUnits="userSpaceOnUse">
 <rect width="16" height="12" fill="#5e6472"/><path d="M0,12 L16,12 M8,0 L8,6 M0,6 L16,6 M0,0 L0,6" stroke="#4a4f5c" stroke-width="1.4"/>
</pattern>
</defs>
"""

# ------------------------------------------------------------------ elementos
def canteiro(x, y, w, h, flores=True):
    o = R(x, y, w, h, "url(#grama)", rx=28, sw=4)
    o += R(x + 6, y + 6, w - 12, h - 12, "none", rx=24, sw=0)
    if flores:
        import random
        rnd = random.Random(x * 7 + y)
        for _ in range(int(w * h / 900)):
            fx, fy = x + 14 + rnd.random() * (w - 28), y + 14 + rnd.random() * (h - 28)
            col = rnd.choice(["#e8505b", "#f4efe2", "#f2c84b", "#c26be0"])
            o += C(round(fx, 1), round(fy, 1), 3.2, col, 1.2)
    return o

def arbusto(cx, cy, r, cor="#3f6b35", corL="#5d8c45"):
    return C(cx, cy, r, cor, 3) + C(cx - r * 0.3, cy - r * 0.3, r * 0.45, corL, 0)

def tronco(cx, base):
    return sombra(cx, base, 30, 10) + R(cx - 8, base - 44, 16, 46, "#6b4a2e", rx=4) + L(f"M{cx-2},{base-38} L{cx-2},{base-6}", "#4e3520", 3)

def copa(cx, cy, r, cor, corD, corL):
    pts = [(0, 0, 1), (-0.6, 0.15, 0.7), (0.6, 0.15, 0.7), (-0.3, -0.45, 0.65), (0.35, -0.4, 0.65), (0, 0.45, 0.6)]
    o = "".join(C(round(cx + dx * r, 1), round(cy + dy * r, 1), round(s * r + 3, 1), OL, 0) for dx, dy, s in pts)
    o += "".join(C(round(cx + dx * r, 1), round(cy + dy * r, 1), round(s * r, 1), corD, 0) for dx, dy, s in pts)
    o += "".join(C(round(cx + dx * r - r * 0.12, 1), round(cy + dy * r - r * 0.14, 1), round(s * r * 0.72, 1), cor, 0) for dx, dy, s in pts)
    o += "".join(C(round(cx + dx * r - r * 0.25, 1), round(cy + dy * r - r * 0.3, 1), round(s * r * 0.3, 1), corL, 0) for dx, dy, s in pts[:4])
    return o

def araucaria_copa(cx, cy):
    o = ""
    for i, (dy, rx, ry) in enumerate([(26, 70, 18), (8, 62, 18), (-10, 52, 16), (-26, 38, 13)]):
        o += E(cx, cy + dy, rx + 3, ry + 3, OL) + E(cx, cy + dy, rx, ry, "#2f5228") + E(cx - 6, cy + dy - 5, rx * 0.8, ry * 0.55, "#3f6b35")
        o += L(f"M{cx-rx*0.7:.0f},{cy+dy-2} L{cx+rx*0.7:.0f},{cy+dy-2}", "#5d8c45", 2.4, 0.7)
    return o

def araucaria_tronco(cx, base):
    return sombra(cx, base, 34, 10) + R(cx - 7, base - 110, 14, 112, "#6b4a2e", rx=4) + L(f"M{cx-2},{base-100} L{cx-2},{base-6}", "#4e3520", 3) + \
        L(f"M{cx},{base-70} L{cx-22},{base-84} M{cx},{base-90} L{cx+20},{base-102}", "#6b4a2e", 5)

def poste(cx, base):
    return sombra(cx, base, 14, 5) + R(cx - 4, base - 64, 8, 66, "#24242c", rx=2, sw=2) + R(cx - 9, base - 6, 18, 8, "#24242c", rx=2, sw=2)

def poste_topo(cx, base):
    y = base - 64
    return (C(cx, y - 14, 30, "#ffd98a", 0, 0.28) + Pth(f"M{cx-11},{y-4} L{cx+11},{y-4} L{cx+8},{y-26} L{cx-8},{y-26} Z", "#ffe7a8", 2.5)
            + Pth(f"M{cx-13},{y-26} L{cx+13},{y-26} L{cx},{y-38} Z", "#24242c", 2.5) + R(cx - 12, y - 6, 24, 6, "#24242c", sw=2))

def banco(x, y, w=80):
    return (sombra(x + w / 2, y + 30, w / 2 + 4, 7) + R(x + 6, y + 18, 6, 14, "#24242c", sw=2) + R(x + w - 12, y + 18, 6, 14, "#24242c", sw=2)
            + R(x, y, w, 10, "#8a5a34", rx=2) + R(x, y + 11, w, 10, "#9e6a40", rx=2))

def pombo(x, y, flip=1):
    return (E(x, y, 7, 5, "#8a8c96", 1.5) + C(x + 6 * flip, y - 4, 3.4, "#6e707a", 1.5) + C(x + 7 * flip, y - 5, 0.9, OL, 0)
            + Pth(f"M{x+9*flip},{y-4} L{x+12*flip},{y-3} L{x+9*flip},{y-2} Z", "#d9a43a", 0))

def casa(x, y, w, cor, cor_d, topo=60, parede=84, porta_x=None, letreiro=None, sacada=False):
    o = R(x, y, w, topo, "url(#telha)", sw=3) + L(f"M{x},{y+6} L{x+w},{y+6}", "#7e3b28", 4)
    o += R(x, y + topo, w, parede, cor, sw=3) + R(x, y + topo, 10, parede, cor_d, sw=0) + L(f"M{x},{y+topo+8} L{x+w},{y+topo+8}", "#f4efe2", 4, 0.8)
    py = y + topo + parede
    px = porta_x if porta_x is not None else x + w / 2 - 18
    o += R(px, py - 58, 36, 58, "#5a3b24") + L(f"M{px+18},{py-56} L{px+18},{py-2}", "#3e2818", 2) + C(px + 28, py - 28, 2.2, "#d9a43a", 0)
    o += Pth(f"M{px-4},{py-58} L{px+40},{py-58} L{px+36},{py-64} L{px},{py-64} Z", "#efe6d2", 2)
    for wx in range(int(x + 16), int(x + w - 40), 56):
        if abs(wx + 15 - (px + 18)) < 40:
            continue
        o += R(wx - 7, py - 62, 8, 38, "#3f7a52", sw=2) + R(wx + 29, py - 62, 8, 38, "#3f7a52", sw=2)
        o += R(wx + 1, py - 62, 28, 38, "#2e3c5c") + L(f"M{wx+15},{py-62} L{wx+15},{py-24} M{wx+1},{py-43} L{wx+29},{py-43}", "#efe6d2", 2.5)
        if sacada:
            o += R(wx - 6, py - 26, 42, 6, "#24242c", sw=2)
    if letreiro:
        lw = len(letreiro) * 10 + 20
        o += R(x + w / 2 - lw / 2, y + topo + 4, lw, 20, "#3a2a20", rx=3, sw=2) + TX(x + w / 2, y + topo + 19, letreiro, 13)
    return o

# ------------------------------------------------------------------ cenas
def catedral():
    o = sombra(600, 478, 330, 14)
    o += R(420, 70, 360, 160, "url(#ardosia)") + L("M600,70 L600,230", "#3c404a", 3)
    o += R(300, 220, 600, 252, "#d9d1c1") + R(300, 220, 600, 14, "#c4bba8", sw=2)
    o += L("M300,300 L900,300 M300,380 L900,380", "#b9b09c", 4)
    o += Pth("M430,222 L770,222 L600,124 Z", "#d9d1c1") + Pth("M470,222 L730,222 L600,148 Z", "#cbc2b0", 2)
    o += L("M600,124 L600,92 M588,104 L612,104", OL, 6) + L("M600,124 L600,92 M588,104 L612,104", "#d9a43a", 3)
    for tx in (300, 770):
        cx = tx + 65
        o += R(tx, 118, 130, 354, "#e2dbcc") + R(tx, 118, 18, 354, "#c4bba8", sw=0) + R(tx, 118, 130, 354, "none")
        o += Pth(f"M{tx-6},{122} L{tx+136},{122} L{cx},{8} Z", "url(#ardosia)") + Pth(f"M{cx},{8} L{tx+136},{122} L{cx+4},{122} Z", "#4a4f5c", 0, 0.55)
        o += L(f"M{cx},{8} L{cx},{-6}", OL, 4) + C(cx, -2, 4, "#d9a43a", 2)
        for px_ in (tx + 4, tx + 126):
            o += Pth(f"M{px_-8},{124} L{px_+8},{124} L{px_},{88} Z", "#cbc2b0", 2)
        for (wy, wh) in ((150, 58), (250, 78)):
            o += Pth(f"M{cx-17},{wy+wh} L{cx-17},{wy+18} Q{cx-17},{wy} {cx},{wy-6} Q{cx+17},{wy} {cx+17},{wy+18} L{cx+17},{wy+wh} Z", "#2e3c5c")
            o += L(f"M{cx},{wy} L{cx},{wy+wh} M{cx-17},{wy+wh*0.55:.0f} L{cx+17},{wy+wh*0.55:.0f}", "#7f93c4", 2)
        o += Pth(f"M{cx-20},472 L{cx-20},430 Q{cx-20},404 {cx},398 Q{cx+20},404 {cx+20},430 L{cx+20},472 Z", "#5a3b24")
    o += C(600, 266, 46, "#c4bba8") + C(600, 266, 36, "#2e3c5c", 2)
    for i in range(8):
        import math
        a = i * math.pi / 4
        o += L(f"M600,266 L{600+33*math.cos(a):.1f},{266+33*math.sin(a):.1f}", "#9fb0d8", 3)
    o += C(600, 266, 9, "#d9a43a", 2)
    o += Pth("M540,472 L540,394 Q540,346 600,328 Q660,346 660,394 L660,472 Z", "#c4bba8")
    o += Pth("M552,472 L552,396 Q552,356 600,342 Q648,356 648,396 L648,472 Z", "#5a3b24")
    o += Pth("M600,342 Q648,356 648,396 L648,472 L600,472 Z", "#47301d", 0)
    o += L("M600,344 L600,470 M556,410 L644,410 M556,440 L644,440", "#2e1f12", 3)
    for sx in (566, 584, 616, 634):
        for sy in (424, 454):
            o += C(sx, sy, 2.2, "#8a8c96", 0)
    o += R(500, 472, 200, 14, "#b4ad9e", sw=2) + R(486, 486, 228, 12, "#a49d90", sw=2)
    return o

def praca():
    o = R(0, 480, PW, 528, "url(#petit)", sw=0)
    o += R(0, 480, PW, 8, "#bdb6a8", sw=0)
    o += canteiro(48, 576, 336, 336) + canteiro(816, 576, 336, 336)
    o += arbusto(80, 610, 18) + arbusto(350, 880, 20) + arbusto(1120, 610, 18) + arbusto(850, 880, 20, "#4a7a3a")
    o += sombra(600, 712, 52, 14) + C(600, 700, 42, "#a49d90") + C(600, 700, 30, "#bdb6a8", 2)
    o += Pth("M588,704 L612,704 L608,650 L592,650 Z", "#d9d1c1") + Pth("M586,652 L614,652 L600,640 Z", "#c4bba8", 2)
    o += R(590, 670, 20, 14, "#8a6a3e", sw=1.6) + TX(600, 681, "0", 11, "#f4efe2")
    o += R(480, 816, 240, 48, "#4e4a46", rx=4) + R(488, 822, 224, 36, "url(#pedra)", sw=0)
    o += R(488, 822, 224, 36, "#bfe3f0", sw=2, op=0.35) + L("M500,826 L530,854 M560,826 L590,854 M640,826 L670,854", "#ffffff", 3, 0.6)
    o += banco(384, 590) + banco(736, 590) + banco(384, 870) + banco(736, 870)
    o += pombo(540, 780) + pombo(560, 790, -1) + pombo(660, 760) + pombo(470, 960, -1) + pombo(820, 960)
    return o

def rua():
    o = R(0, 1008, PW, 96, "#4a4a50", sw=0) + R(0, 1004, PW, 10, "#9a948a", sw=2) + R(0, 1098, PW, 10, "#9a948a", sw=2)
    for x in range(0, PW, 72):
        if 440 < x < 750:
            continue
        o += R(x + 12, 1053, 40, 5, "#e8e4d8", sw=0)
    for x in range(462, 744, 40):
        o += R(x, 1020, 22, 76, "#ecebe4", sw=0)
    return o

CORES_CASA = [("#e2b85a", "#c49a44"), ("#6a95b8", "#4f7a9c"), ("#d48a8a", "#b46e6e"), ("#7fae8a", "#62907a"), ("#e6d8b8", "#c8b994"), ("#b98ac9", "#9a6eab")]

def claudino():
    o = R(432, 1104, 336, 384, "url(#pedra)", sw=0) + L("M432,1104 L432,1488 M768,1104 L768,1488", "#5e564f", 4)
    i = 0
    letreiros = {(0, 1): "CAFÉ", (1, 0): "LIVROS", (2, 1): "BAR", (3, 2): "ANTIQUÁRIO"}
    for row, y in enumerate((1104, 1296)):
        lados = [[(0, 144), (144, 144), (288, 144)], [(768, 192), (960, 96), (1056, 144)]]
        if row == 1:
            lados = [[(0, 192), (192, 96), (288, 144)], [(768, 144), (912, 144), (1056, 144)]]
        for lado, casas in enumerate(lados):
            o += R(casas[0][0], y + 144, sum(c[1] for c in casas), 48, "url(#calcada)", sw=0)
            for k, (x, w) in enumerate(casas):
                cor, cor_d = CORES_CASA[i % len(CORES_CASA)]
                i += 1
                o += casa(x, y, w, cor, cor_d, letreiro=letreiros.get((row * 2 + lado, k)), sacada=(k % 2 == 0))
    o += canteiro(436, 1446, 40, 36, True) + canteiro(724, 1254, 40, 36, True)
    return o

def largo():
    o = R(0, 1488, PW, 432, "url(#pedra)", sw=0)
    o += sombra(270, 1734, 230, 12)
    o += R(168, 1500, 312, 64, "url(#telha)") + R(168, 1560, 312, 168, "#efe9dc") + R(168, 1560, 14, 168, "#d6cfbf", sw=0)
    o += R(168, 1560, 312, 10, "#c9a45a", sw=2) + R(168, 1718, 312, 10, "#c9a45a", sw=2)
    for px_ in (168, 252, 396, 470):
        o += R(px_, 1570, 10, 148, "#c9a45a", sw=2)
    o += Pth("M240,1562 L408,1562 L324,1510 Z", "#efe9dc") + Pth("M262,1558 L386,1558 L324,1522 Z", "#e2dbcc", 2)
    o += L("M324,1510 L324,1484 M314,1494 L334,1494", OL, 6) + L("M324,1510 L324,1484 M314,1494 L334,1494", "#d9a43a", 3)
    for wx in (196, 422):
        o += Pth(f"M{wx},1660 L{wx},1612 Q{wx},1596 {wx+15},1592 Q{wx+30},1596 {wx+30},1612 L{wx+30},1660 Z", "#2e3c5c") + L(f"M{wx+15},1596 L{wx+15},1660", "#7f93c4", 2)
    o += Pth("M294,1728 L294,1664 Q294,1640 324,1634 Q354,1640 354,1664 L354,1728 Z", "#c9a45a")
    o += Pth("M300,1728 L300,1666 Q300,1646 324,1641 Q348,1646 348,1666 L348,1728 Z", "#5a3b24") + L("M324,1642 L324,1726", "#2e1f12", 3)
    o += R(280, 1728, 88, 12, "#b4ad9e", sw=2)
    o += R(48, 1540, 120, 188, "#efe9dc") + R(48, 1540, 14, 188, "#d6cfbf", sw=0) + R(48, 1540, 120, 10, "#c9a45a", sw=2) + R(48, 1718, 120, 10, "#c9a45a", sw=2)
    o += Pth("M42,1544 L174,1544 L108,1492 Z", "url(#telha)") + L("M108,1492 L108,1474", OL, 4) + C(108, 1472, 4, "#d9a43a", 2)
    o += Pth("M86,1640 L86,1590 Q86,1572 108,1566 Q130,1572 130,1590 L130,1640 Z", "#2e3c5c") + Pth("M98,1600 Q108,1588 118,1600 L118,1616 L98,1616 Z", "#d9a43a", 2)
    o += C(108, 1678, 14, "#f4efe2", 2.5) + L("M108,1678 L108,1669 M108,1678 L114,1682", OL, 2)
    # casario à direita
    o += casa(960, 1488, 120, "#e2b85a", "#c49a44", letreiro="ARTE") + casa(1080, 1488, 120, "#6a95b8", "#4f7a9c", sacada=True)
    o += R(960, 1632, 240, 48, "url(#calcada)", sw=0)
    # chafariz do Cavalo Babão
    o += sombra(816, 1776, 104, 14)
    o += Pth("M752,1724 L752,1606 Q752,1580 784,1576 L848,1576 Q880,1580 880,1606 L880,1724 Z", "#9a948a") + R(752, 1590, 16, 134, "#827c72", sw=0)
    o += L("M760,1640 L872,1640 M760,1690 L872,1690", "#827c72", 3)
    hx, hy = 816, 1636
    o += Pth(f"M{hx-26},{hy-26} C{hx-30},{hy-48} {hx-14},{hy-56} {hx-4},{hy-44} L{hx+6},{hy-50} C{hx+14},{hy-46} {hx+24},{hy-34} {hx+22},{hy-12} "
             f"C{hx+20},{hy+8} {hx+16},{hy+30} {hx+10},{hy+44} C{hx+4},{hy+54} {hx-12},{hy+54} {hx-16},{hy+42} C{hx-22},{hy+24} {hx-24},{hy} {hx-26},{hy-26} Z", "#8a6a3e")
    o += Pth(f"M{hx-26},{hy-26} C{hx-24},{hy} {hx-22},{hy+24} {hx-16},{hy+42} C{hx-12},{hy+50} {hx-4},{hy+52} {hx+2},{hy+50} C{hx-6},{hy+30} {hx-12},{hy+2} {hx-14},{hy-30} Z", "#5e4628", 0)
    o += Pth(f"M{hx-22},{hy-34} L{hx-28},{hy-58} L{hx-12},{hy-44} Z", "#8a6a3e", 2.5) + Pth(f"M{hx+2},{hy-44} L{hx+4},{hy-66} L{hx+14},{hy-44} Z", "#8a6a3e", 2.5)
    o += L(f"M{hx-26},{hy-22} C{hx-34},{hy-8} {hx-34},{hy+10} {hx-30},{hy+26}", "#5e4628", 5)
    o += E(hx - 6, hy - 14, 5, 4, "#1e1a24") + E(hx + 10, hy - 14, 5, 4, "#1e1a24") + C(hx - 6, hy - 15, 1.4, "#e8e4d8", 0) + C(hx + 10, hy - 15, 1.4, "#e8e4d8", 0)
    o += L(f"M{hx-10},{hy-22} L{hx-1},{hy-18} M{hx+14},{hy-22} L{hx+5},{hy-18}", OL, 3)
    o += E(hx - 6, hy + 42, 4, 3, "#2e2218") + E(hx + 6, hy + 42, 4, 3, "#2e2218") + L(f"M{hx-12},{hy+48} C{hx-4},{hy+52} {hx+4},{hy+52} {hx+10},{hy+46}", OL, 2.5)
    o += Pth(f"M{hx-4},{hy+52} C{hx-6},{hy+62} {hx-3},{hy+76} {hx-5},{hy+86} L{hx+3},{hy+86} C{hx+1},{hy+76} {hx+4},{hy+62} {hx+2},{hy+52} Z", "#9fd8ec", 1.8)
    o += R(730, 1712, 172, 62, "#a49d90", rx=12) + R(744, 1722, 144, 40, "#5aa6c8", rx=8, sw=2)
    o += L("M760,1742 C772,1736 784,1748 796,1742 M820,1750 C832,1744 844,1756 856,1750", "#bfe7f4", 2.5) + E(hx, 1724, 16, 5, "#e6f6fb", 0, 0.9)
    o += R(776, 1694, 80, 18, "#3a2a20", rx=3, sw=2) + TX(hx, 1707, "CAVALO BABÃO", 10)
    return o

def laterais_topo():
    o = R(0, 0, 240, 480, "url(#grama)", sw=0) + R(960, 0, 240, 480, "url(#grama)", sw=0)
    o += L("M0,2 L240,2 M960,2 L1200,2", "#2f5228", 8)
    o += arbusto(40, 420, 22) + arbusto(200, 440, 20) + arbusto(1000, 430, 22) + arbusto(1170, 420, 20, "#4a7a3a")
    o += banco(1040, 400)
    o += R(424, 468, 40, 30, "#5a3b24", sw=2) + R(410, 452, 68, 28, "#8a5a34", rx=3) + TX(444, 471, "CATEDRAL", 10)
    return o

# árvores e postes (tronco no chão, copa/cabeça na camada superior)
ARVORES = [("araucaria", 110, 300), ("ipe", 1100, 300), ("ipe", 216, 760), ("araucaria", 984, 700), ("verde", 1080, 860),
           ("verde", 552, 1830), ("ipe", 1032, 1860), ("verde", 1150, 1780)]
POSTES = [(456, 572), (744, 572), (456, 980), (744, 980), (456, 1296), (744, 1440), (624, 1760), (960, 1720)]

def gerar_svgs():
    chao = DEFS + R(0, 0, PW, PH, "#5f8a3e", sw=0)
    chao += laterais_topo() + catedral() + praca() + rua() + claudino() + largo()
    topo = ""
    for kind, x, base in ARVORES:
        if kind == "araucaria":
            chao += araucaria_tronco(x, base)
            topo += araucaria_copa(x, base - 120)
        else:
            chao += tronco(x, base)
            cor = ("#e9c23c", "#c99a22", "#f7e07a") if kind == "ipe" else ("#4f8a3e", "#33602a", "#79b05a")
            topo += copa(x, base - 66, 46, *cor)
    for x, base in POSTES:
        chao += poste(x, base)
        topo += poste_topo(x, base)
    cab = f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {PW} {PH}" width="{PW}" height="{PH}">\n'
    return cab + chao + "</svg>\n", cab + topo + "</svg>\n"

# ------------------------------------------------------------------ colisão (região 1 = bloqueado)
def regioes():
    reg = [[0] * W for _ in range(H)]
    def bloq(x0, y0, x1, y1):
        for y in range(y0, y1 + 1):
            for x in range(x0, x1 + 1):
                reg[y][x] = 1
    bloq(0, 0, 24, 9)                                      # catedral e jardins laterais
    bloq(8, 10, 9, 10)                                     # placa
    bloq(1, 12, 7, 18); bloq(17, 12, 23, 18)               # canteiros
    bloq(12, 14, 12, 14)                                   # marco zero
    bloq(10, 17, 14, 17)                                   # vitrine do calçamento antigo
    for bx, by in ((8, 12), (15, 12), (8, 18), (15, 18)):  # bancos
        bloq(bx, by, bx + 1, by)
    bloq(0, 23, 8, 25); bloq(16, 23, 24, 25)               # casario linha 1
    bloq(0, 27, 8, 29); bloq(16, 27, 24, 29)               # casario linha 2
    bloq(1, 31, 9, 35)                                     # Igreja da Ordem
    bloq(20, 31, 24, 33)                                   # casario do largo
    bloq(15, 33, 18, 36)                                   # chafariz do Cavalo Babão
    bloq(9, 30, 9, 30); bloq(15, 26, 15, 26)               # vasos de flores na rua
    for kind, x, base in ARVORES:
        tx, ty = int(x // T), int((base - 4) // T)
        reg[ty][tx] = 1
    for x, base in POSTES:
        reg[int((base - 4) // T)][int(x // T)] = 1
    for y in range(H):                                     # bordas laterais
        reg[y][0] = reg[y][0] or (1 if y < 21 or y > 22 else 0)
    return reg

# ------------------------------------------------------------------ eventos
def evento(id_, nome, x, y, linhas_por_janela, fim=False):
    lista = []
    for falante, linhas in linhas_por_janela:
        lista.append({"code": 101, "indent": 0, "parameters": ["", 0, 0, 2, falante]})
        for l in linhas:
            lista.append({"code": 401, "indent": 0, "parameters": [l]})
    if fim:
        lista.append({"code": 354, "indent": 0, "parameters": []})
    lista.append({"code": 0, "indent": 0, "parameters": []})
    return {"id": id_, "name": nome, "note": "", "x": x, "y": y, "pages": [{
        "conditions": {"actorId": 1, "actorValid": False, "itemId": 1, "itemValid": False, "selfSwitchCh": "A",
                       "selfSwitchValid": False, "switch1Id": 1, "switch1Valid": False, "switch2Id": 1, "switch2Valid": False,
                       "variableId": 1, "variableValid": False, "variableValue": 0},
        "directionFix": False, "image": {"characterIndex": 0, "characterName": "", "direction": 2, "pattern": 0, "tileId": 0},
        "list": lista, "moveFrequency": 3, "moveRoute": {"list": [{"code": 0, "parameters": []}], "repeat": True, "skippable": False, "wait": False},
        "moveSpeed": 3, "moveType": 0, "priorityType": 1, "stepAnime": False, "through": False, "trigger": 0, "walkAnime": True}]}

def mapa_json():
    reg = regioes()
    data = [0] * (W * H * 6)
    for y in range(H):
        for x in range(W):
            data[(5 * H + y) * W + x] = reg[y][x]
    eventos = [None,
               evento(1, "Placa da Catedral", 9, 10, [("", ["Catedral Basílica Menor de Nossa Senhora da Luz.", "Daqui você segue para o Largo da Ordem..."])]),
               evento(2, "Marco Zero", 12, 14, [("", ["\\C[6]Marco Zero de Curitiba\\C[0]", "O ponto onde a cidade começou."])]),
               evento(3, "Vitrine", 12, 17, [("", ["Sob o vidro, o calçamento antigo da cidade."])]),
               evento(4, "Cavalo Babão", 16, 36, [("", ["\\C[3]O Cavalo Babão\\C[0] baba sem parar...", "Você chegou ao Largo da Ordem!"]),
                                                  ("", ["\\C[6]FIM DO TESTE\\C[0]", "Obrigado por jogar."])], fim=True)]
    return {"autoplayBgm": False, "autoplayBgs": False, "battleback1Name": "", "battleback2Name": "",
            "bgm": {"name": "", "pan": 0, "pitch": 100, "volume": 90}, "bgs": {"name": "", "pan": 0, "pitch": 100, "volume": 90},
            "disableDashing": False, "displayName": "Praça Tiradentes", "encounterList": [], "encounterStep": 30,
            "height": H, "note": "<paralaxe>\n<topo: !praca_tiradentes_topo>", "parallaxLoopX": False, "parallaxLoopY": False,
            "parallaxName": "!praca_tiradentes", "parallaxShow": True, "parallaxSx": 0, "parallaxSy": 0, "scrollType": 0,
            "specifyBattleback": False, "tilesetId": 1, "width": W, "data": data, "events": eventos}, reg

PLUGIN = r"""/*:
 * @target MZ
 * @plugindesc Mapas de paralaxe: colisão por região e camada acima do personagem.
 * @author LPCSM
 * @help MapaParalaxe.js
 * Nas notas do mapa:
 *   <paralaxe>          ativa o modo paralaxe: tudo é passável, exceto região 1.
 *   <topo: arquivo>     imagem de img/parallaxes desenhada ACIMA dos personagens
 *                       (copas de árvores, cabeças de poste...), presa ao mapa.
 * Use um nome de paralaxe começando com "!" para a imagem rolar junto com o mapa.
 */
(() => {
  const ehParalaxe = () => $dataMap && /<paralaxe>/i.test($dataMap.note || "");

  const _checkPassage = Game_Map.prototype.checkPassage;
  Game_Map.prototype.checkPassage = function(x, y, bit) {
    if (ehParalaxe()) return this.regionId(x, y) !== 1;
    return _checkPassage.call(this, x, y, bit);
  };

  const _createTilemap = Spriteset_Map.prototype.createTilemap;
  Spriteset_Map.prototype.createTilemap = function() {
    _createTilemap.call(this);
    const m = ehParalaxe() && /<topo:\s*([^>]+)>/i.exec($dataMap.note);
    if (m) {
      this._topoParalaxe = new Sprite(ImageManager.loadParallax(m[1].trim()));
      this._topoParalaxe.z = 9;
      this._tilemap.addChild(this._topoParalaxe);
    }
  };

  const _update = Spriteset_Map.prototype.update;
  Spriteset_Map.prototype.update = function() {
    _update.call(this);
    if (this._topoParalaxe) {
      this._topoParalaxe.x = Math.round(-$gameMap.displayX() * $gameMap.tileWidth());
      this._topoParalaxe.y = Math.round(-$gameMap.displayY() * $gameMap.tileHeight());
    }
  };
})();
"""

def main():
    for sub in ("fonte", "img/parallaxes", "data", "js/plugins"):
        os.makedirs(os.path.join(RAIZ, sub), exist_ok=True)
    chao, topo = gerar_svgs()
    f_chao, f_topo = os.path.join(RAIZ, "fonte", "praca_tiradentes.svg"), os.path.join(RAIZ, "fonte", "praca_tiradentes_topo.svg")
    open(f_chao, "w").write(chao)
    open(f_topo, "w").write(topo)
    mapa, reg = mapa_json()
    json.dump(mapa, open(os.path.join(RAIZ, "data", "Map002.json"), "w"), ensure_ascii=False, separators=(",", ":"))
    open(os.path.join(RAIZ, "js", "plugins", "MapaParalaxe.js"), "w").write(PLUGIN)
    js = os.path.join(os.path.dirname(os.path.abspath(__file__)), "svg_para_png.js")
    for src, dst in ((f_chao, "!praca_tiradentes.png"), (f_topo, "!praca_tiradentes_topo.png")):
        subprocess.run(["node", js, src, os.path.join(RAIZ, "img", "parallaxes", dst)], check=True)
    print("mapa ok:", RAIZ)

if __name__ == "__main__":
    main()
