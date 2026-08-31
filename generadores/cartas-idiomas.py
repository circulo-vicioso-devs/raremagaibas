#!/usr/bin/env python3
"""
Genera /es/raremagaiba/ y /en/raremagaiba/ desde web/index.html.

El idioma va primero en la ruta, igual que la home: /es/ y /en/ son las raíces
de cada idioma. Los recursos (mint.js, img/, allowlist.json) quedan en
/raremagaiba/, que es neutro, y se referencian absolutos.

El sitio de las cartas trae los dos idiomas en el mismo HTML, con spans
.l-es/.l-en que el CSS muestra u oculta. Eso deja UN solo URL para los dos
idiomas y Google indexa uno solo. Acá se parte en dos páginas de verdad.

  python3 cartas-idiomas.py

No se toca web/index.html: sigue siendo la fuente. Los recursos (mint.js,
img/, allowlist.json) quedan donde están, en /raremagaiba/, y las rutas se
absolutizan porque desde un subdirectorio las relativas se rompen.

⚠️ El CSS de .l-es/.l-en se conserva a propósito: mint.js genera esos spans en
tiempo de ejecución para los mensajes de estado.
"""
import os, re, sys
from bs4 import BeautifulSoup

# Vive en web/generadores/ pero opera sobre la raíz del proyecto.
AQUI = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
FUENTE = os.path.join(AQUI, "web/index.html")
DEST = os.path.join(AQUI, "landing")
SITIO = "https://magaiba.xyz"
BASE = "/raremagaiba"      # dónde viven los recursos
RUTA = "raremagaiba"      # la página, colgando de /es/ o /en/

META = {
  "es": ("RareMagaibas · Cartas de MAGAIBA",
         "Cartas coleccionables de MAGAIBA en Solana. Se acuñan quemando el token: "
         "710.000 la Gentle, 1.000.000 la Ultra Gentle en foil. Serie 0 · El Génesis, "
         "12 cartas, 25 ediciones cada una."),
  "en": ("RareMagaibas · MAGAIBA Cards",
         "Collectible cards for MAGAIBA on Solana, minted by burning the token: "
         "710,000 for a Gentle, 1,000,000 for the Ultra Gentle foil. Series 0 · "
         "The Genesis, 12 cards, 25 editions each."),
}
OTRO = {"es": ("en", "EN"), "en": ("es", "ES")}


def absolutizar(html):
    """Desde /raremagaiba/es/ una ruta relativa apunta un nivel más abajo."""
    html = html.replace('from "./mint.js"', f'from "{BASE}/mint.js"')
    html = re.sub(r'(src|href)="(?:\./)?(img/[^"]+)"', rf'\1="{BASE}/\2"', html)
    # las rutas dentro del array CARTAS, que van a un src por template literal
    html = re.sub(r'\b(bg|cut|src):"(?:\./)?(img/[^"]+)"', rf'\1:"{BASE}/\2"', html)
    return html


def pagina(sopa_html, idi):
    sopa = BeautifulSoup(sopa_html, "html.parser")
    otro, otro_nom = OTRO[idi]

    # fuera el idioma que no es; los del idioma bueno pierden la marca
    for el in sopa.select(f".l-{otro}"):
        el.decompose()
    for el in sopa.select(f".l-{idi}"):
        if el.name == "span":
            el.unwrap()
        else:
            del el["class"]

    # el toggle de idioma pasa a ser un enlace de verdad
    cont = sopa.select_one(".idioma")
    if cont:
        cont.clear()
        a = sopa.new_tag("a", href=f"/{otro}/{RUTA}/", hreflang=otro)
        a["class"] = "lang"
        a.string = otro_nom
        cont.append(a)

    html = sopa.decode()

    # el idioma queda fijo en la página, no lo decide el navegador
    html = html.replace(
        'let lang = (navigator.language || "es").toLowerCase().startsWith("en") ? "en" : "es";',
        f'const lang = "{idi}";   // fijo: cada idioma tiene su propio URL')
    html = html.replace(
        "for (const b of document.querySelectorAll('.lang'))\n  b.onclick = () => ponIdioma(b.dataset.lang);\n",
        "")
    html = html.replace('class="volver" href="/"', f'class="volver" href="/{idi}/"')
    html = html.replace("ponIdioma(lang);", "arrancar();")
    # ponIdioma arrancaba con "lang = l;" para cambiar de idioma en caliente.
    # Con lang const eso tira TypeError y mata el módulo entero: sin cartas,
    # sin contador y sin iniciarMint(). Se saca esa línea.
    html = html.replace("function ponIdioma(l){\n  lang = l;",
                        "function arrancar(){\n  const l = lang;")
    html = html.replace("function ponIdioma(l){", "function arrancar(){\n  const l = lang;")

    titulo, desc = META[idi]
    cabeza = f'''<!DOCTYPE html>
<html lang="{idi}" data-lang="{idi}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="color-scheme" content="light dark">
<title>{titulo}</title>
<meta name="description" content="{desc}">
<link rel="canonical" href="{SITIO}/{idi}/{RUTA}/">
<link rel="alternate" hreflang="es" href="{SITIO}/es/{RUTA}/">
<link rel="alternate" hreflang="en" href="{SITIO}/en/{RUTA}/">
<link rel="alternate" hreflang="x-default" href="{SITIO}/en/{RUTA}/">
<meta property="og:type" content="website">
<meta property="og:site_name" content="RareMagaibas">
<meta property="og:url" content="{SITIO}/{idi}/{RUTA}/">
<meta property="og:title" content="{titulo}">
<meta property="og:description" content="{desc}">
<meta property="og:image" content="{SITIO}{BASE}/img/c001.webp">
<meta property="og:image:width" content="1000">
<meta property="og:image:height" content="1400">
<meta property="og:locale" content="{"es_AR" if idi == "es" else "en_US"}">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{titulo}">
<meta name="twitter:description" content="{desc}">
<meta name="twitter:image" content="{SITIO}{BASE}/img/c001.webp">
'''
    # se reemplaza toda la cabeza vieja, quedándose con su <style> y sus <link>
    i = html.index("<head>") + len("<head>")
    j = html.index("</head>")
    resto = html[i:j]
    for quitar in (r"<title>.*?</title>", r'<meta charset[^>]*>', r'<meta name="viewport"[^>]*>',
                   r'<meta name="color-scheme"[^>]*>', r'<meta name="description"[^>]*>',
                   r'<link rel="canonical"[^>]*>', r'<meta property="og:[^>]*>',
                   r'<meta name="twitter:[^>]*>', r'<link rel="alternate"[^>]*>'):
        resto = re.sub(quitar, "", resto, flags=re.S)
    html = cabeza + resto.strip() + "\n</head>" + html[j + len("</head>"):]
    html = re.sub(r"^.*?<!DOCTYPE html>", "<!DOCTYPE html>", html, count=1, flags=re.S)
    return html


def main():
    bruto = absolutizar(open(FUENTE, encoding="utf-8").read())
    for idi in ("es", "en"):
        os.makedirs(f"{DEST}/{idi}/{RUTA}", exist_ok=True)
        h = pagina(bruto, idi)

        # Guarda: al fijar lang como const, cualquier "lang = ..." que quede de
        # la versión con toggle tira TypeError y mata el módulo entero. No es un
        # error de sintaxis, así que node --check no lo agarra.
        js = re.search(r'<script type="module">(.*?)</script>', h, re.S).group(1)
        for v in re.findall(r"\bconst\s+(\w+)\s*=", js):
            if re.search(rf"(?<![.\w]){v}\s*=(?!=)", js.replace(f"const {v} =", "", 1)):
                raise SystemExit(f"[{idi}] se reasigna la constante {v}: rompería la página")

        open(f"{DEST}/{idi}/{RUTA}/index.html", "w", encoding="utf-8").write(h)
        txt = re.sub(r"<[^>]+>", " ", re.sub(r"<(script|style)[^>]*>.*?</\1>", "", h, flags=re.S))
        print(f"  {idi}/{RUTA}/index.html  {len(h)//1024} KB · ~{len(txt.split())} palabras")


if __name__ == "__main__":
    main()
