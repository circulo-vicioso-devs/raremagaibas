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

  // Tope de la serie: una carta por billetera del club
  TOPE: 160,

  // RPC. El público alcanza para leer saldos y anda con CORS, pero tiene límite
  // de pedidos. Si hace falta más, poner acá una key de Helius RESTRINGIDA POR
  // DOMINIO — este repo es público y cualquiera puede leer lo que se escriba acá.
  RPC: "https://api.mainnet-beta.solana.com",

  // Candy Machine de la Serie 0. Mientras esté vacío, el botón explica que la
  // acuñación todavía no abrió.
  CANDY_MACHINE: "",

  // Dirección que recibe el SOL del artista, por carta. Se completa al desplegar.
  TESOROS: {},
};
