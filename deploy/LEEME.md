# Deploy de la Serie 0

## Dónde quedó (2026-08-29, 03:00 UTC aprox)

| | |
|---|---|
| Desplegadas | **2 de 24** — `carta-001` y `carta-001-foil` |
| SOL gastado | 0,0796 |
| SOL restante | ~0,43 |
| Assets en Arweave | **24/24 subidos**, gratis vía Turbo |
| Asentados en arweave.net | **2 de 24** — el resto sigue propagando |

## Lo que falta

1. **Esperar que Arweave asiente las 22 restantes.** Verificar con:
   ```bash
   cd deploy && python3 - <<'PY'
   import json,urllib.request,glob
   for f in sorted(glob.glob('carta-*/cache.json')):
       c=json.load(open(f))
       if c['program'].get('candyMachine'): continue
       try:
           m=json.load(urllib.request.urlopen(c['items']['0']['metadata_link'],timeout=15))
           n=len(urllib.request.urlopen(m['image'],timeout=15).read())
           print(f"  {f.split('/')[0]:<16} {'listo' if n>5000 else 'esperando'}")
       except Exception: print(f"  {f.split('/')[0]:<16} esperando")
   PY
   ```
   **No desplegar antes de que digan `listo`**: los metadatos son inmutables y
   una URI rota no se arregla nunca.

2. **Fondear la wallet.** Faltan ~0,45 SOL para las 22 restantes
   (0,037 por máquina).

3. **Desplegar**, carpeta por carpeta:
   ```bash
   cd deploy/carta-002 && sugar deploy && sugar guard add
   ```

4. **Pegar las direcciones** en `web/config.js` (`MAQUINAS`).

## Bugs que ya están resueltos

| problema | solución |
|---|---|
| `sugar upload` roto: Bundlr murió | subir con `subir-arweave.mjs` (Turbo) |
| `"default": null` | va `{}` |
| falta `ruleSet` | agregado como `null` |
| nombre on-chain > 32 chars | el foil se marca con ✦ |
| falta `candyMachineCreator` en cache | lo escribe el uploader |
| label `foilclub` > 6 chars | renombrado a `foil36` |

## ⚠️ Pendiente de decidir: la colección está partida

`sugar deploy` crea una colección nueva por máquina aunque el `cache.json`
traiga `collectionMint` puesto. Hoy hay dos:

- `DsC9cF8DMYCvFpaJWVGZNZH2J7tEZe4TaYMxBmH2S7ws` (carta-001)
- `CEj9vHx3ZxPfz4vnA79aE7YkA1xjTHZY96VsoBnEQdVJ` (carta-001-foil)

Si sigue así, en Magic Eden se van a ver **24 colecciones sueltas** en vez de
una de 12 cartas. Antes de desplegar el resto hay que probar
`sugar collection set <mint>` en una carpeta y confirmar que la reusa.
