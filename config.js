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

  // RPC. Va contra Helius, que hace falta porque getAssetsByGroup es un método
  // DAS que el RPC público no tiene (sin él, el contador de coleccionistas da 0).
  //
  // La key NO va acá: este repo es público. El navegador pega a /rpc, que es un
  // proxy de Netlify definido en el netlify.toml del repo privado magaiba-web.
  // La key vive ahí y nunca sale al cliente.
  RPC: "/rpc",

  // Dos Candy Machines por carta: la Gentle entrega el arte normal y la Ultra
  // Gentle el foil. Los metadatos son inmutables, así que cada una tiene los
  // suyos y no hay forma de que salga una carta mal etiquetada.
  MAQUINAS: {
    "001": {
        foil: "Ch69kDugSrKSAcus4wXdhyjtMuZo3Y1snW6u8PWdaoD2",
        gentle: "44QWm4EEFt5zioAuBT5WvfA95776J9AESDikompKy8mV"
    },
    "002": {
        foil: "ETresJebu3m5ZDs4dcxdgQrJcpW1aUUBkzxWHx4pPsx8",
        gentle: "5kMednpevDv6yrRzFkQb2QCV47vJZX8bPNYaR9x3xnob"
    },
    "003": {
        foil: "9WA2Jqp9mapCDS2pkFRm564AQc96westWReoYGKyaoVr",
        gentle: "ERss2okJNfNqF2BRrxvtwCXZ9o9HzRxk7SnztFvyTCnK"
    },
    "004": {
        foil: "48hnWKshU5iKHwSoghUAtn8qBBuwHwR4aMHYJrueU3HB",
        gentle: "5HhbQzuUC2vojccjb1dTooHg2G853NbxyhYhNZP1YwcL"
    },
    "005": {
        foil: "D5bdAVznkfxWTWt2cHhGGtZ1AHCCJUKzi1HpZEYRXy4H",
        gentle: "GixRLHh8mcaz4gq9Jq3P3Ghh7DokxLwpFxTRtfeEevc5"
    },
    "006": {
        foil: "Fq33qdiXumU5TmxH5MbMmmE6ftXeKQXTj2HZSGuriodY",
        gentle: "SeDqsg7NBpiTv2tF64gC6JQbd12eFDvSse5BDBqWQ7f"
    },
    "007": {
        foil: "4ggLaGhymSHafJUZU2t5Z54zb2gwjuDs4FRwupG8C2sq",
        gentle: "FFbxWAZJZifqh75b1MBmtoivJipWDXSwAYAVdQL5Ygt7"
    },
    "008": {
        foil: "ADCpsxBcRcNGCizd1jjQrZLsDgdU5T6npjKf6r16WMMJ",
        gentle: "CEtgVe13QtAPZUqp43k5PG8mioimJgGtLYcRPKvuXxtX"
    },
    "009": {
        foil: "GHq4GBy6rrR7CfiVepw3sBsJYyYye977oyeLytfyNWMf",
        gentle: "6LKPmDSB5pNhJsi8hvDmqW92GG9LUC2waZgcf8YF1n6t"
    },
    "010": {
        foil: "Ev135pheFaN534BME3mTEgKUwgc2yjjhfB3dAG2XHKWL",
        gentle: "8R8QL1ryKrK7YWRMFE7nZ5TRmUd2t7dm8ifTUXTdgiZr"
    },
    "011": {
        foil: "7zNgQMZpGczai4Eg4Z14VQeiwiD3M45EuMuE5VCdYywy",
        gentle: "6Goc51jeNBdG5Rsrv2WRe1AeXvAEvVXzJy85ube6zZGL"
    },
    "012": {
        foil: "Ag91JkGSmLK3eBRN3eSahsX3YhU58Gv7ZBYGy9RJnYih",
        gentle: "CFXSqe34oCgKN59WZLZmv5jsShQkVodDRNMdbWc3LBqH"
    }
},

  // La colección que agrupa las 12 cartas en los marketplaces.
  COLECCION: "DsC9cF8DMYCvFpaJWVGZNZH2J7tEZe4TaYMxBmH2S7ws",

  // Destino del solPayment. Está fijado en los guards on-chain: ponerlo mal acá
  // no abarata nada, la transacción se rechaza. Va para que el navegador pueda
  // nombrar la cuenta al armar el mint.
  TESORO: "3ukZwiJ9ciZtdfya9Wc8F8kGewMmhbj6ssYKdB2invYq",
};
