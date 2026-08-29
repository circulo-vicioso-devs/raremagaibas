# Deploy de la Serie 0 — COMPLETO

**Las 24 Candy Machines están en mainnet**, cada una con su guard, todas
agrupadas en una sola colección.

| | |
|---|---|
| Colección | `DsC9cF8DMYCvFpaJWVGZNZH2J7tEZe4TaYMxBmH2S7ws` |
| Máquinas | 24 (12 cartas × gentle/foil), 25 piezas cada una |
| Wallet | `3ukZwiJ9ciZtdfya9Wc8F8kGewMmhbj6ssYKdB2invYq` |
| Gastado | ~0,60 SOL · quedan 0,11 |
| Assets | Arweave, subidos gratis por Turbo |

Las direcciones están en `web/config.js`. Para regenerarlas:
`python3 deploy/actualizar-config.py`

## Los guards, verificados on-chain

| grupo | quema | quién |
|---|---:|---|
| `gentle` | 710.000 MAGAIBA | las 166 del club |
| `ultra` | 1.000.000 | las 166, sale foil |
| `foil36` | 710.000 | las 36 que nunca vendieron, sale foil |

Los tres cobran 0,05 SOL al tesoro. Merkle roots en `../data/merkle.json`.

## Pendiente

**Recuperar renta de dos máquinas huérfanas.** Antes de encontrar el fix de la
colección, `carta-001-foil` y `carta-002` se desplegaron con colección propia y
se rehicieron. Las viejas quedaron con ~0,034 SOL de renta adentro:

```
DVYRSYsHEwozeTR2dC6gYCxTCzPnw1F7grCkwUmuy1Fv
3ThV5e3iQCZijFe52KG8CepjC6i7CXQzKobxMVU81x6T
```

`sugar withdraw` necesita terminal interactiva (pide confirmación), así que hay
que correrlo desde una terminal normal:

```bash
cd deploy/carta-001-foil && sugar withdraw DVYRSYsHEwozeTR2dC6gYCxTCzPnw1F7grCkwUmuy1Fv
```

## El truco de la colección compartida

`sugar deploy` crea una colección nueva por máquina **aunque el `cache.json`
traiga `collectionMint`**. Para que la reuse hay que marcar el ítem `-1` como
`onChain: true`; ahí responde *"Collection mint already deployed"*.

Sin eso, en Magic Eden aparecen 24 colecciones sueltas en vez de una de 12
cartas. Además, baja el costo por máquina de 0,037 a 0,020 SOL.

## Los seis bugs que hubo que resolver

| problema | solución |
|---|---|
| `sugar upload` roto: Bundlr murió | subir con `subir-arweave.mjs` (Turbo) |
| `"default": null` | va `{}` |
| falta `ruleSet` | agregado como `null` |
| nombre on-chain > 32 chars | el foil se marca con ✦ |
| falta `candyMachineCreator` en el cache | lo escribe el uploader |
| label `foilclub` > 6 chars | renombrado a `foil36` |
| colección duplicada por máquina | ítem `-1` con `onChain: true` |

## Lo que falta para que la acuñación funcione

`web/mint.js` tiene la wallet, la elegibilidad y el contador andando contra la
chain. La transacción de acuñar está como comentario: hay que armarla con
`mintV2` de `@metaplex-foundation/mpl-candy-machine`, eligiendo el grupo
(`gentle` / `ultra` / `foil36`) y pasando el merkle proof de la billetera.
