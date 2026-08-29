# Deploy de la Serie 0

## Estado (2026-08-29)

| | |
|---|---|
| **Desplegadas** | **21 de 24**, todas con sus guards verificados |
| Faltan | `carta-011-foil`, `carta-012`, `carta-012-foil` |
| SOL gastado | 0,4836 |
| SOL restante | 0,026 |
| Assets en Arweave | 24/24 subidos **y asentados** |
| Colección | `DsC9cF8DMYCvFpaJWVGZNZH2J7tEZe4TaYMxBmH2S7ws`, compartida |

Las 11 cartas desplegadas ya están en `web/config.js`. La 011 tiene la Gentle
pero no la foil; la 012 no tiene ninguna.

## Para terminar

1. **Fondear la wallet** `3ukZwiJ9ciZtdfya9Wc8F8kGewMmhbj6ssYKdB2invYq`
   con **0,1 SOL** — sobra para las tres que faltan (0,020 cada una).

2. **Desplegar**:
   ```bash
   cd deploy && ./desplegar.sh     # sigue por donde quedó, solo, y corta si falta saldo
   ```

3. **Pasar las direcciones al sitio**:
   ```bash
   python3 deploy/actualizar-config.py
   ```

4. `git add -A && git commit && git push`

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
