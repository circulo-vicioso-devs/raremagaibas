#!/usr/bin/env python3
"""
Prepara todo lo que Sugar necesita para desplegar la Serie 0.

Una Candy Machine por carta —así el usuario elige cuál acuñar— y las doce
apuntando a la misma colección, para que en Magic Eden y Tensor se vea como
una sola colección de 12 cartas.

  python3 preparar.py

Deja en deploy/ una carpeta por carta con:
  config.json      la config de Sugar, con los guards
  assets/0.png     la obra
  assets/0.json    los metadatos
  assets/collection.png / .json   (solo en la primera; las demás la reusan)

Después, por cada carpeta:
  sugar validate && sugar upload && sugar deploy && sugar guard add
"""
import json, os, shutil, sys

AQUI = os.path.dirname(os.path.abspath(__file__))
RAIZ = os.path.dirname(AQUI)

MINT = "A6rSPi9JmJgVkW6BatsA6MjFYLseizPM2Fnt92coFjf4"
DECIMALES = 8
GENTLE = 710_000
ULTRA = 1_000_000
SOL_ARTISTA = 0.05

# Las 12 cartas. El `archivo` sale de web/img/.
CARTAS = [
    ("001", "Magaiba",                 "c001", "cut1"),
    ("002", "Magaiba Tokyo",           "c002", None),
    ("003", "Magaiba Mecha",           "c003", None),
    ("004", "Magaiba Springfield",     "c004", None),
    ("005", "Magaiba Lo-Fi",           "c005", None),
    ("006", "Magaiba Instrumentality", "c006", None),
    ("007", "Magaiba Neural",          "c007", None),
    ("008", "Magaiba Portrait",        "c008", None),
    ("009", "Magaiba Prime",           "c009", None),
    ("010", "Magaiba Sketch",          "c010", "cut10"),
    ("011", "Magaiba Oracle",          "c011", None),
    ("012", "Magaiba Fuji",            "c012", None),
]

# Cuántas de cada una. Sin tope por billetera: alcanza para que nadie
# se quede afuera, y lo que no se acuña no existe.
TIRADA = 25   # por máquina; con foil son 50 por carta, 600 en total

# Se completan antes de desplegar.
TESORO = "3ukZwiJ9ciZtdfya9Wc8F8kGewMmhbj6ssYKdB2invYq"
AUTORIDAD = "3ukZwiJ9ciZtdfya9Wc8F8kGewMmhbj6ssYKdB2invYq"


def metadatos(serie, nombre, archivo, edicion, foil):
    nivel = "Ultra Gentle" if foil else "Gentle"
    return {
        # el nombre on-chain topea en 32 caracteres: el foil va con ✦
        "name": f"{nombre} #{edicion}" + (" ✦" if foil else ""),
        "symbol": "MGB",
        "description": (
            f"RareMagaibas · Serie 0 «El Génesis» (2024) · carta {serie}/012.\n\n"
            "Los memes que hizo la comunidad MAGAIBA en marzo de 2024, montados "
            "como cartas. Se acuñan quemando MAGAIBA: los tokens se destruyen en "
            "la misma transacción que crea esta pieza.\n\n"
            + ("Ultra Gentle: la versión foil.\n\n" if foil else "")
            + "Obra bajo CC BY-SA 4.0."
        ),
        "image": archivo,
        "external_url": "https://circulo-vicioso-devs.github.io/raremagaibas/",
        "attributes": [
            {"trait_type": "Serie", "value": "0 · El Génesis (2024)"},
            {"trait_type": "Carta", "value": f"{serie}/012"},
            {"trait_type": "Gentileza", "value": nivel},
            {"trait_type": "Licencia", "value": "CC BY-SA 4.0"},
        ],
        "properties": {
            "files": [{"uri": archivo, "type": "image/webp"}],
            "category": "image",
            "creators": [{"address": AUTORIDAD, "share": 100}],
        },
    }


def config(serie, nombre, foil):
    """La config de Sugar para una carta.

    Tres grupos de guards:
      gentle    · 710.000 quemados, abierto al club
      ultra     · 1.000.000 quemados, la misma carta en foil
      foilclub  · 710.000 quemados, foil, solo para las 36 de la lista
    """
    def guards(quema, lista):
        g = {
            "tokenBurn": {"amount": quema * 10 ** DECIMALES, "mint": MINT},
            "solPayment": {"value": SOL_ARTISTA, "destination": TESORO},
        }
        if lista:
            raiz = json.load(open(os.path.join(RAIZ, "data", "merkle.json")))
            g["allowList"] = {"merkleRoot": raiz[lista]["root"]}
        return g

    return {
        "number": TIRADA,
        "symbol": "MGB",
        "sellerFeeBasisPoints": 500,
        "isMutable": False,   # inmutable: los metadatos no se tocan nunca más
        "isSequential": False,
        "creators": [{"address": AUTORIDAD, "share": 100}],
        "uploadMethod": "bundlr",          # Arweave, pago único
        "awsConfig": None,
        "nftStorageAuthToken": None,
        "shdwStorageAccount": None,
        "pinataConfig": None,
        "hiddenSettings": None,
        "ruleSet": None,
        # La máquina Gentle cobra 710.000 y entrega el arte normal.
        # La Ultra Gentle entrega el foil: 1.000.000 para el club, y 710.000
        # para las 36 que nunca vendieron.
        "guards": {
            "default": {},
            "groups": (
                [{"label": "gentle", "guards": guards(GENTLE, "club")}]
                if not foil else
                [{"label": "ultra",    "guards": guards(ULTRA,  "club")},
                 {"label": "foil36", "guards": guards(GENTLE, "foil")}]
            ),
        },
    }


COLECCION = {
    "name": "RareMagaibas · El Génesis",
    "symbol": "MGB",
    "description": (
        "Doce cartas hechas por la comunidad MAGAIBA en marzo de 2024. "
        "Se acuñan quemando MAGAIBA. Obras bajo CC BY-SA 4.0."
    ),
    "image": "collection.png",
    "external_url": "https://circulo-vicioso-devs.github.io/raremagaibas/",
    "properties": {
        "files": [{"uri": "collection.png", "type": "image/webp"}],
        "category": "image",
    },
}


def main():
    img = os.path.join(RAIZ, "web", "img")
    hechas, faltan = 0, []
    for serie, nombre, arch, cut in CARTAS:
      for foil in (False, True):
        src = os.path.join(img, "foil", arch + "f.webp") if foil \
              else os.path.join(img, arch + ".webp")
        if not os.path.exists(src):
            faltan.append((serie, nombre, os.path.basename(src)))
            continue
        d = os.path.join(AQUI, f"carta-{serie}" + ("-foil" if foil else ""))
        a = os.path.join(d, "assets")
        os.makedirs(a, exist_ok=True)

        for i in range(TIRADA):
            shutil.copy(src, os.path.join(a, f"{i}.png"))
            with open(os.path.join(a, f"{i}.json"), "w") as f:
                json.dump(metadatos(serie, nombre, f"{i}.png", i + 1, foil), f,
                          indent=2, ensure_ascii=False)

        # la colección va igual en las doce: Sugar la sube una vez y se reusa
        shutil.copy(os.path.join(img, "bicho.webp"), os.path.join(a, "collection.png"))
        with open(os.path.join(a, "collection.json"), "w") as f:
            json.dump(COLECCION, f, indent=2, ensure_ascii=False)

        with open(os.path.join(d, "config.json"), "w") as f:
            json.dump(config(serie, nombre, foil), f, indent=2, ensure_ascii=False)
        hechas += 1
        et = "Ultra Gentle" if foil else "Gentle"
        print(f"  carta-{serie}{'-foil' if foil else '':<5}  {nombre:<24} {et}")

    print(f"\n  {hechas} carpetas listas en deploy/")
    if faltan:
        print(f"\n  ⚠ faltan {len(faltan)} obras en web/img/:")
        for s, n, a in faltan:
            print(f"      carta {s} · {n} · esperaba {a}.webp")
    print("""
  Antes de desplegar, en cada config.json:
    1. TESORO y AUTORIDAD → las wallets de verdad
    2. los merkle root de club y foil → `sugar guard add` los pide

  Y después, por carpeta:
    cd deploy/carta-001
    sugar validate && sugar upload && sugar deploy && sugar guard add
""")


if __name__ == "__main__":
    main()
