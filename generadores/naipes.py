#!/usr/bin/env python3
"""
Compone las cartas de RareMagaibas como imagen, para que el NFT se vea igual
que en el sitio.

El sitio dibuja el marco, el título, los sellos y el foil con HTML y CSS, así
que nada de eso viajaba al NFT: lo que se subió a Arweave fueron los memes
crudos, sin recortar y con proporciones que iban de 5:7 a cuadrada y hasta
horizontal. Esto replica ese diseño en píxeles.

  python3 naipes.py            genera las 24 en naipes/
  python3 naipes.py --una 002  sólo una carta, para mirarla

Las medidas salen del CSS de web/index.html, que está pensado sobre una carta
de 440 px de ancho. Acá se sale a 1000x1400, que es 5:7 exacto, así que todo
lo que estaba en px se escala por 1000/440 y lo que estaba en cqw (porcentaje
del ancho de la carta) se aplica directo sobre 1000.
"""
import os, re, sys, math
from PIL import Image, ImageDraw, ImageFont, ImageFilter

# Vive en web/generadores/ pero opera sobre la raíz del proyecto.
AQUI = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
WEB  = os.path.join(AQUI, "web")
SAL  = os.path.join(AQUI, "naipes")
FUE  = os.path.join(AQUI, "web", "fuentes")   # versionadas junto al generador

W, H = 1000, 1400                 # 5:7 exacto
K = W / 440                       # el CSS está pensado sobre 440 px

def px(v): return int(round(v * K))

PAD      = px(14)                 # .carta padding / .ventana inset
R_CARTA  = px(30)
R_VENT   = px(18)
TIT_TOP  = px(20)
LADO     = px(22)
PIE_BOT  = px(18)
SELLO    = px(30)                 # círculo blanco 0ED
SELLO_SET= px(20)                 # círculo dorado
ANILLO_1 = px(3)                  # borde dorado interior
ANILLO_2 = px(5)                  # borde oscuro

NEGRO   = (11, 10, 9)
VENT_BG = (26, 21, 18)
ORO     = (215, 192, 142)
ORO_OSC = (30, 24, 15)
CREMA   = (247, 238, 214)
PIE_COL = (230, 217, 186)

def fuente(arch, tam, peso=None):
    f = ImageFont.truetype(os.path.join(FUE, arch), tam)
    if peso:
        try: f.set_variation_by_axes([peso])
        except Exception: pass
    return f

F_NOM = lambda: fuente("Cinzel.ttf", int(W * 0.05), 700)      # .nom 5cqw
F_PIE = lambda: fuente("Cinzel.ttf", int(W * 0.026), 600)     # .pie-carta 2.6cqw
F_SEL = lambda: fuente("Nunito.ttf", px(10), 800)             # .sello b


def leer_cartas():
    """Las 12 cartas salen de web/index.html, que es la fuente de verdad."""
    s = open(os.path.join(WEB, "index.html"), encoding="utf-8").read()
    bloque = re.search(r"const CARTAS = \[(.*?)\n\];", s, re.S).group(1)
    out = []
    for ln in bloque.strip().split("\n"):
        d = dict(re.findall(r'(\w+):"([^"]*)"', ln))
        if d.get("s"): out.append(d)
    return out


def pct(v):
    return float(v.strip().rstrip("%")) / 100.0


def cubrir(im, caja, pos="50% 50%"):
    """object-fit: cover con object-position."""
    cw, ch = caja
    iw, ih = im.size
    e = max(cw / iw, ch / ih)
    nw, nh = max(1, int(round(iw * e))), max(1, int(round(ih * e)))
    im = im.resize((nw, nh), Image.LANCZOS)
    px_, py_ = [pct(x) for x in pos.split()]
    x = int(round((nw - cw) * px_))
    y = int(round((nh - ch) * py_))
    return im.crop((x, y, x + cw, y + ch))


def redondear(im, r):
    m = Image.new("L", im.size, 0)
    ImageDraw.Draw(m).rounded_rectangle([0, 0, im.size[0] - 1, im.size[1] - 1], r, fill=255)
    out = Image.new("RGBA", im.size, (0, 0, 0, 0))
    out.paste(im, (0, 0), m)
    return out


def velo(size):
    """.velo: oscuro arriba y abajo, transparente en el medio."""
    w, h = size
    g = Image.new("L", (1, h), 0)
    d = ImageDraw.Draw(g)
    paradas = [(0.00, 0.60), (0.20, 0.0), (0.66, 0.0), (1.00, 0.75)]
    for y in range(h):
        t = y / (h - 1)
        for (t0, a0), (t1, a1) in zip(paradas, paradas[1:]):
            if t0 <= t <= t1:
                f = 0 if t1 == t0 else (t - t0) / (t1 - t0)
                d.point((0, y), fill=int(round((a0 + (a1 - a0) * f) * 255)))
                break
    capa = Image.new("RGBA", (w, h), (8, 6, 4, 255))
    capa.putalpha(g.resize((w, h)))
    return capa


def foil(size):
    """.foil1: arcoíris en color-dodge al 40%, + .foil2, el barrido blanco."""
    w, h = size
    paradas = [(0.00, (255, 0, 128)), (0.18, (255, 190, 0)), (0.36, (0, 255, 170)),
               (0.54, (0, 140, 255)), (0.72, (180, 0, 255)), (1.00, (255, 0, 128))]
    arco = Image.new("RGB", (w, h))
    d = ImageDraw.Draw(arco)
    # gradiente a 115°, proyectando cada píxel sobre la dirección
    ang = math.radians(115 - 90)
    dx, dy = math.cos(ang), math.sin(ang)
    largo = abs(w * dx) + abs(h * dy)
    for x in range(w):
        t = ((x * dx) + (h / 2 * dy) + largo / 2) / largo
        t = min(1.0, max(0.0, t))
        for (t0, c0), (t1, c1) in zip(paradas, paradas[1:]):
            if t0 <= t <= t1:
                f = 0 if t1 == t0 else (t - t0) / (t1 - t0)
                c = tuple(int(round(a + (b - a) * f)) for a, b in zip(c0, c1))
                d.line([(x, 0), (x, h)], fill=c)
                break
    arco.putalpha(int(0.32 * 255))

    barrido = Image.new("L", (w, h), 0)
    db = ImageDraw.Draw(barrido)
    cx = int(w * 0.34)
    ancho = int(w * 0.40)
    for x in range(max(0, cx - ancho), min(w, cx + ancho)):
        a = 1 - abs(x - cx) / ancho
        db.line([(x, 0), (x, h)], fill=int(round(a * a * 0.34 * 255)))
    blanco = Image.new("RGBA", (w, h), (255, 255, 255, 0))
    blanco.putalpha(barrido)
    return arco, blanco


def dodge(base, capa):
    """mix-blend-mode: color-dodge."""
    b = base.convert("RGB").split()
    c = capa.convert("RGB").split()
    a = capa.split()[3].point(lambda v: v)
    sal = []
    for cb, cc in zip(b, c):
        tb = cb.point(lambda v: v)
        tc = cc.point(lambda v: 255 if v >= 255 else v)
        res = Image.eval(tb, lambda v: v)
        res = Image.merge("L", (res,))
        sal.append(Image.composite(
            Image.eval(cb, lambda v: v), cb, cb))  # placeholder, se calcula abajo
    # PIL no trae color-dodge: se hace numérico
    import numpy as np
    nb = np.asarray(base.convert("RGB"), dtype=np.float32)
    nc = np.asarray(capa.convert("RGB"), dtype=np.float32)
    na = np.asarray(capa.split()[3], dtype=np.float32)[..., None] / 255.0
    den = np.clip(255.0 - nc, 1.0, 255.0)
    res = np.clip(nb * 255.0 / den, 0, 255)
    mez = nb * (1 - na) + res * na
    return Image.fromarray(mez.astype("uint8"), "RGB")


def texto_espaciado(d, xy, txt, font, fill, esp=0.0, ancla_derecha=False):
    """letter-spacing, que PIL no tiene."""
    anchos = [d.textlength(c, font=font) + esp for c in txt]
    total = sum(anchos) - (esp if txt else 0)
    x, y = xy
    if ancla_derecha: x -= total
    for c, a in zip(txt, anchos):
        d.text((x, y), c, font=font, fill=fill)
        x += a
    return total


def componer(c, es_foil):
    base = Image.new("RGB", (W, H), NEGRO)

    vw, vh = W - 2 * PAD, H - 2 * PAD
    vent = Image.new("RGB", (vw, vh), VENT_BG)

    if c.get("cut"):
        fondo = Image.open(os.path.join(WEB, c["bg"])).convert("RGB")
        vent.paste(cubrir(fondo, (vw, vh)), (0, 0))
        rec = Image.open(os.path.join(WEB, c["cut"])).convert("RGBA")
        rw = int(round(vw * pct(c["cw"])))
        rh = int(round(rec.size[1] * rw / rec.size[0]))
        rec = rec.resize((rw, rh), Image.LANCZOS)
        x = vw - rw - int(round(vw * pct(c["cr"])))
        y = vh - rh - int(round(vh * pct(c["cb"])))
        sombra = Image.new("RGBA", (vw, vh), (0, 0, 0, 0))
        sombra.paste(rec, (x, y + px(10)), rec)
        sombra = sombra.filter(ImageFilter.GaussianBlur(px(9)))
        vent = Image.alpha_composite(vent.convert("RGBA"), sombra).convert("RGB")
        vent.paste(rec, (x, y), rec)
    else:
        arte = Image.open(os.path.join(WEB, c["src"])).convert("RGB")
        vent.paste(cubrir(arte, (vw, vh), c.get("op", "50% 50%")), (0, 0))

    vent = Image.alpha_composite(vent.convert("RGBA"), velo((vw, vh))).convert("RGB")

    if es_foil:
        arco, blanco = foil((vw, vh))
        vent = dodge(vent, arco)
        vent = Image.alpha_composite(vent.convert("RGBA"), blanco).convert("RGB")

    d = ImageDraw.Draw(vent)
    d.rounded_rectangle([0, 0, vw - 1, vh - 1], R_VENT, outline=ORO, width=ANILLO_1)
    d.rounded_rectangle([ANILLO_1, ANILLO_1, vw - 1 - ANILLO_1, vh - 1 - ANILLO_1],
                        max(1, R_VENT - ANILLO_1), outline=ORO_OSC, width=ANILLO_2 - ANILLO_1)

    lienzo = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    lienzo.paste(redondear(vent, R_VENT), (PAD, PAD))
    base = Image.alpha_composite(redondear(base, R_CARTA), lienzo).convert("RGB")

    d = ImageDraw.Draw(base)
    x0, x1 = PAD + LADO, W - PAD - LADO

    # título
    f = F_NOM()
    d.text((x0, PAD + TIT_TOP), c["n"], font=f, fill=CREMA,
           stroke_width=max(1, px(1)), stroke_fill=(0, 0, 0))
    # sello de set: círculo dorado
    sx = x1 - SELLO_SET
    sy = PAD + TIT_TOP + px(4)
    d.ellipse([sx, sy, sx + SELLO_SET, sy + SELLO_SET], fill=(216, 185, 106),
              outline=(30, 24, 14), width=max(1, px(1)))
    d.ellipse([sx + SELLO_SET * 0.18, sy + SELLO_SET * 0.14,
               sx + SELLO_SET * 0.52, sy + SELLO_SET * 0.48], fill=(255, 251, 239))

    # pie
    fp = F_PIE()
    esp = int(round(W * 0.026 * 0.22))          # letter-spacing .22em
    yb = H - PAD - PIE_BOT - SELLO
    d.ellipse([x0, yb, x0 + SELLO, yb + SELLO], fill=(255, 255, 255))
    fs = F_SEL()
    bb = d.textbbox((0, 0), "0ED", font=fs)
    d.text((x0 + SELLO / 2 - (bb[2] - bb[0]) / 2, yb + SELLO / 2 - (bb[3] - bb[1]) / 2 - bb[1]),
           "0ED", font=fs, fill=(0, 0, 0))

    ytxt = yb + SELLO / 2 - (W * 0.026) / 2 - px(2)
    medio = f"{c['s']}/012 · MGB"
    dere  = "ULTRA GENTLE" if es_foil else "GENTLE"
    ancho = lambda t: sum(d.textlength(ch, font=fp) + esp for ch in t) - esp
    # space-between: el del medio va centrado en el hueco que queda entre el
    # sello y el texto de la derecha. Sin esto, "ULTRA GENTLE" lo pisa.
    hueco_ini = x0 + SELLO + px(10)
    hueco_fin = x1 - ancho(dere) - px(10)
    texto_espaciado(d, (hueco_ini + (hueco_fin - hueco_ini) / 2 - ancho(medio) / 2, ytxt),
                    medio, fp, PIE_COL, esp)
    texto_espaciado(d, (x1, ytxt), dere, fp, PIE_COL, esp, ancla_derecha=True)
    return base


def main():
    os.makedirs(SAL, exist_ok=True)
    cartas = leer_cartas()
    solo = None
    if "--una" in sys.argv:
        solo = sys.argv[sys.argv.index("--una") + 1]
    hechas = 0
    for c in cartas:
        if solo and c["s"] != solo: continue
        for es_foil in (False, True):
            im = componer(c, es_foil)
            nom = f"c{c['s']}{'f' if es_foil else ''}.png"
            im.save(os.path.join(SAL, nom), "PNG", optimize=True)
            print(f"  {nom:<12} {im.size[0]}x{im.size[1]}  {c['n']}{' · foil' if es_foil else ''}")
            hechas += 1
    print(f"\n  {hechas} imágenes en {SAL}")

if __name__ == "__main__":
    main()
