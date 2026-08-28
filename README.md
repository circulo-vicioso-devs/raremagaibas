# RareMagaibas

Cartas coleccionables de la comunidad MAGAIBA. Se acuñan quemando tokens.

- **Serie 0 · El Génesis (2024)** — 12 cartas, una por billetera, para las ~160
  direcciones que tienen el airdrop original de 710.000 MAGAIBA.
- **Gentle** 710.000 · **Ultra Gentle** 1.000.000 (la misma carta en foil).
- Las 32 billeteras que nunca movieron un token, y el dev team, sacan la Ultra
  Gentle pagando 710.000.

Mint: `A6rSPi9JmJgVkW6BatsA6MjFYLseizPM2Fnt92coFjf4`

## Estructura

```
index.html     el sitio, bilingüe (detecta el idioma del navegador)
img/           las obras y la animación
```

Sitio estático, sin build. Se sirve tal cual.

## Pendiente

- Conectar wallet y acuñar (Core Candy Machine, guards `tokenBurn` + `solPayment`
  + `mintLimit` de 1 por billetera + `allowList`).
- Contador en vivo leyendo la chain — hoy los números son estáticos en `index.html`.

## Licencia

Las obras van bajo **CC BY-SA 4.0**, cada una acreditada a su autor.
