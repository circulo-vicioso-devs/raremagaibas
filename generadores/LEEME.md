# Generadores del sitio

El HTML publicado es la **salida** de estos scripts, no su fuente. Si se pierden,
el sitio no se puede regenerar.

| script | genera |
|---|---|
| `landing.py` | `/es/` y `/en/` (la landing del token) + `sitemap.xml` + `robots.txt` |
| `cartas-idiomas.py` | `/es/raremagaiba/` y `/en/raremagaiba/` desde `../index.html` |
| `naipes.py` | las 24 cartas compuestas en 1000×1400, que son el arte de los NFT |

## Correrlos

```bash
cd ~/Escritorio/cripto/magaiba
source ~/.config/solana/helius.env     # landing.py lee el supply de la chain
python3 landing.py
python3 cartas-idiomas.py
```

`web/publicar.sh` hace el ciclo entero: copia los recursos, genera las páginas
por idioma y pushea los dos repos.

⚠️ **Rutas absolutas.** Las páginas viven en `/es/raremagaiba/` y los recursos en
`/raremagaiba/`. Desde un subdirectorio una ruta relativa apunta un nivel más
abajo y da 404, así que los generadores absolutizan el import de `mint.js`, los
`img/` del HTML y los del array `CARTAS`.

⚠️ **`cartas-idiomas.py` aborta si detecta una reasignación a constante.** No es
paranoia: `ponIdioma()` arrancaba con `lang = l;`, y al fijar `lang` como `const`
eso tira `TypeError`. Una excepción a nivel de módulo corta la ejecución entera —
sin cartas, sin contador y sin acuñación. `node --check` no lo agarra porque es
un error de ejecución, no de sintaxis.

## Fuentes

`naipes.py` usa Cinzel y Nunito, que están en `../fuentes/` (o sea `web/fuentes/`) bajo licencia OFL.
Vienen del repo de Google Fonts.
