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
TIRADA = 60

# Se completan antes de desplegar.
TESORO = "PONER_LA_WALLET_QUE_COBRA_EL_SOL"
AUTORIDAD = "PONER_LA_WALLET_QUE_DESPLIEGA"


def metadatos(serie, nombre, archivo, edicion):
    return {
        "name": f"{nombre} #{edicion}",
        "symbol": "MGB",
        "description": (
            f"RareMagaibas · Serie 0 «El Génesis» (2024) · carta {serie}/012.\n\n"
            "Los memes que hizo la comunidad MAGAIBA en marzo de 2024, montados "
            "como cartas. Se acuñan quemando MAGAIBA: los tokens se destruyen en "
            "la misma transacción que crea esta pieza.\n\n"
            "Obra bajo CC BY-SA 4.0."
        ),
        "image": archivo,
        "external_url": "https://circulo-vicioso-devs.github.io/raremagaibas/",
        "attributes": [
            {"trait_type": "Serie", "value": "0 · El Génesis (2024)"},
            {"trait_type": "Carta", "value": f"{serie}/012"},
            {"trait_type": "Gentileza", "value": "Gentle"},
            {"trait_type": "Licencia", "value": "CC BY-SA 4.0"},
        ],
        "properties": {
            "files": [{"uri": archivo, "type": "image/webp"}],
            "category": "image",
            "creators": [{"address": AUTORIDAD, "share": 100}],
        },
    }


def config(serie, nombre):
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
            g["allowList"] = {"merkleRoot": f"PEGAR_MERKLE_ROOT_DE_{lista}"}
        return g

    return {
        "number": TIRADA,
        "symbol": "MGB",
        "sellerFeeBasisPoints": 500,
        "isMutable": True,
        "isSequential": False,
        "creators": [{"address": AUTORIDAD, "share": 100}],
        "uploadMethod": "bundlr",          # Arweave, pago único
        "awsConfig": None,
        "nftStorageAuthToken": None,
        "shdwStorageAccount": None,
        "pinataConfig": None,
        "hiddenSettings": None,
        "guards": {
            "default": None,
            "groups": [
                {"label": "gentle",   "guards": guards(GENTLE, "club")},
                {"label": "ultra",    "guards": guards(ULTRA,  "club")},
                {"label": "foilclub", "guards": guards(GENTLE, "foil")},
            ],
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
        src = os.path.join(img, arch + ".webp")
        if not os.path.exists(src):
            faltan.append((serie, nombre, arch))
            continue
        d = os.path.join(AQUI, f"carta-{serie}")
        a = os.path.join(d, "assets")
        os.makedirs(a, exist_ok=True)

        for i in range(TIRADA):
            shutil.copy(src, os.path.join(a, f"{i}.png"))
            with open(os.path.join(a, f"{i}.json"), "w") as f:
                json.dump(metadatos(serie, nombre, f"{i}.png", i + 1), f, indent=2,
                          ensure_ascii=False)

        # la colección va igual en las doce: Sugar la sube una vez y se reusa
        shutil.copy(os.path.join(img, "bicho.webp"), os.path.join(a, "collection.png"))
        with open(os.path.join(a, "collection.json"), "w") as f:
            json.dump(COLECCION, f, indent=2, ensure_ascii=False)

        with open(os.path.join(d, "config.json"), "w") as f:
            json.dump(config(serie, nombre), f, indent=2, ensure_ascii=False)
        hechas += 1
        print(f"  carta-{serie}  {nombre:<24} {TIRADA} ediciones")

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
