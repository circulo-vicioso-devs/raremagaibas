// Configuración de RareMagaibas — todo lo que hay que tocar está acá.
export const CFG = {
  // El token
  MINT: "A6rSPi9JmJgVkW6BatsA6MjFYLseizPM2Fnt92coFjf4",
  DECIMALES: 8,

  // Supply al abrir la acuñación. Lo quemado por la colección es la diferencia
  // contra el supply que devuelve la chain, así que el contador es real.
  SUPPLY_BASE: 878_625_325.475,

  // Precios de la Serie 0, en tokens enteros
  PRECIO_GENTLE: 710_000,
  PRECIO_ULTRA: 1_000_000,

  // Sin tope por billetera: cada uno acuña tantas como pueda quemar.
  CLUB: 163,               // billeteras con el airdrop, para la barra
  CARTAS_META: 600,        // piezas de la serie
  META_QUEMA: 163 * 710_000,  // referencia de la barra de quemado

  // RPC. El público alcanza para leer saldos y anda con CORS, pero tiene límite
  // de pedidos. Si hace falta más, poner acá una key de Helius RESTRINGIDA POR
  // DOMINIO — este repo es público y cualquiera puede leer lo que se escriba acá.
  RPC: "https://api.mainnet-beta.solana.com",

  // Dos Candy Machines por carta: la Gentle entrega el arte normal y la Ultra
  // Gentle el foil. Los metadatos son inmutables, así que cada una tiene los
  // suyos y no hay forma de que salga una carta mal etiquetada.
  MAQUINAS: {
    // "001": { gentle: "…", foil: "…" },
  },

  // La colección que agrupa las 12 cartas en los marketplaces.
  COLECCION: "",

  // Dirección que recibe el SOL del artista, por carta. Se completa al desplegar.
  TESOROS: {},
};
