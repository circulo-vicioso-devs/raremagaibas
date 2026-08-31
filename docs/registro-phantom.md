# Dar de alta el sitio en Phantom

El proceso **cambió**: ya no se pide a Blowfish. Phantom lo hace autogestión
desde **Phantom Portal**, verificando el dominio con un TXT de DNS.

## Cómo (docs.phantom.com/phantom-portal/verify-domain)

1. Entrar a **Phantom Portal** → **Edit App Info**
2. Poner el dominio en **Public URL**: `https://magaiba.xyz`
3. **Save**, y copiar el código de la sección **Domain Verification**
   (viene con formato `phantom-verification-XXXXX`)
4. Cargar un **TXT en el dominio raíz**:

   | campo | valor |
   |---|---|
   | Tipo | TXT |
   | Host | `@` (o vacío) |
   | Valor | el código de Phantom |
   | TTL | 3600 |

   El DNS de `magaiba.xyz` está en **Netlify DNS** (`dns1-4.p07.nsone.net`),
   así que el TXT se carga desde el panel de Netlify → Domains → magaiba.xyz.
5. Esperar la propagación y apretar **Verify Domain** en el Portal.

Propaga en 15-60 minutos, aunque puede tardar hasta 48 h. Una vez verificado
queda así mientras el TXT siga puesto.

Para chequear la propagación sin entrar al panel:
```bash
dig +short TXT magaiba.xyz
```

⚠️ El **Public URL** es `https://magaiba.xyz`, el dominio raíz. La colección
vive en `/raremagaiba/`, pero la verificación es del dominio.

## Datos del sitio

| campo | valor |
|---|---|
| Dominio | `magaiba.xyz` |
| URL de la dApp | `https://magaiba.xyz/raremagaiba/` |
| Nombre | RareMagaibas |
| Categoría | NFT / colección coleccionable |
| Cadena | Solana (mainnet-beta) |
| Repositorio | https://github.com/circulo-vicioso-devs/raremagaibas (público) |
| Contacto | realjuanruocco@421.news |

## Programas y cuentas con las que interactúa

| qué | dirección |
|---|---|
| Candy Machine Core v3 | `CndyV3LdqHUfDLmE5naZjVN8rBZz4tqhdefbAnjHG3JR` |
| Candy Guard | `Guard1JwRhJkVH6XZhzoYxeBVQe872VH6QggF4BWmS9g` |
| Token Metadata | `metaqbxxUerdq28cj1RbAWkYQm3ybzjb6a8bt518x1s` |
| Colección | `DsC9cF8DMYCvFpaJWVGZNZH2J7tEZe4TaYMxBmH2S7ws` |
| Token MAGAIBA | `A6rSPi9JmJgVkW6BatsA6MjFYLseizPM2Fnt92coFjf4` |
| Tesoro (recibe el solPayment) | `3ukZwiJ9ciZtdfya9Wc8F8kGewMmhbj6ssYKdB2invYq` |
| 24 Candy Machines | en `web/config.js`, campo `MAQUINAS` |

## Texto para el formulario (inglés)

> RareMagaibas is an NFT trading-card collection for the MAGAIBA community token
> on Solana. The token launched in March 2024 out of the Argentine podcast
> Círculo Vicioso; the cards are its 2026 follow-up.
>
> Cards are minted by burning MAGAIBA: 710,000 for a Gentle, 1,000,000 for the
> Ultra Gentle foil. The site uses Metaplex Candy Machine Core v3 with Candy
> Guard. Each mint runs two transactions: a `route` instruction that validates a
> Merkle proof against the allow list, then `mintV2`, which burns the tokens
> (tokenBurn guard), takes 0.05 SOL (solPayment guard) and mints the NFT.
>
> Minting is limited to an allow list of 166 wallets holding at least 710,000
> MAGAIBA. The mint and freeze authorities of the MAGAIBA token are revoked. The
> site is fully open source and holds no user funds or keys: every transaction is
> built client-side and signed by the user's own wallet.
>
> Site: https://magaiba.xyz/raremagaiba/
> Source: https://github.com/circulo-vicioso-devs/raremagaibas
> Collection: DsC9cF8DMYCvFpaJWVGZNZH2J7tEZe4TaYMxBmH2S7ws

## Qué ya se hizo del lado del sitio
- `<meta charset>`, `viewport`, `description`, `canonical`
- `og:*` y `twitter:card` con imagen (carta 001, 1000×1400)
- favicon propio
- HTTPS con HSTS, `X-Content-Type-Options`, `Referrer-Policy`, `X-Frame-Options`
- Código fuente público, sin claves: el RPC pasa por un proxy del lado servidor

## Lo que NO se va a poder sacar
Phantom avisa igual cuando una transacción toca un programa que no conoce y
cuando hay quema de tokens. Eso es correcto y no se saca registrando el dominio:
lo que se saca es la advertencia de **dominio no verificado**.


---

## ⚠️ Las cartas no aparecen en Phantom (2026-08-30)

Phantom esconde por defecto las colecciones que no reconoce, como defensa contra
el spam de airdrops. Le pasa a RareMagaibas.

**La colección está bien.** Verificado on-chain, no hay nada que arreglar:

| chequeo | resultado |
|---|---|
| `collection.verified` en los NFT | **true** |
| metadata de la colección | 200 |
| imagen de la colección | 200 · 520×520 |
| `tokenStandard` | NonFungible |
| `collectionDetails` | `V1 size 6` |
| Magic Eden | **renderiza las cartas correctamente** |
| Helius DAS | las ve, `burnt:false` |

Si Magic Eden y Helius la leen bien, el problema es exclusivamente la heurística
de Phantom.

### Vías abiertas, en orden de utilidad
1. **Reclamar la colección en `creators.magiceden.io`.** Es autogestión y gratis;
   la colección ya es Metaplex Certified con `verified:true`, así que la detecta
   sola. Las wallets se apoyan en los marketplaces para decidir qué es legítimo.
2. **Soporte de Phantom**: `help.phantom.com` → *Submit a request*. El Portal
   está cerrado a altas nuevas, pero el soporte es **otro canal** y recibe
   pedidos de colecciones marcadas mal. Mandar la dirección de la colección
   `DsC9cF8DMYCvFpaJWVGZNZH2J7tEZe4TaYMxBmH2S7ws` y el link de Magic Eden.
3. **Phantom Portal**, cuando reabra.

### Mientras tanto
El sitio ya avisa, antes de conectar y en el mensaje de éxito, que Phantom puede
esconder la carta y cómo mostrarla. ⚠️ **Los pasos de la documentación de Phantom
están desactualizados** — hablan de un ícono de tres puntos que ya no existe. El
texto del sitio nombra *Collectibles → Manage Collectibles*, que es lo estable.

⚠️ **Timing**: reclamar la colección en Magic Eden **después** de actualizar la
metadata de la colección, porque el marketplace la cachea al indexarla.
