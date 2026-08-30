// Conexión de wallet, elegibilidad y contador en vivo.
//
// Lo que hace hoy, de verdad y contra la chain:
//   · conecta Phantom / Solflare / Backpack
//   · lee cuánto MAGAIBA tiene la billetera y si llega a los 710.000
//   · dice si está en la lista del club y si le toca el foil sin plus
//   · lee el supply del token y muestra cuánto se quemó desde que abrió
//
//   · acuña: dos transacciones, el proof del allowList y el mint
//
// El SDK de Metaplex pesa ~292 KB comprimido, así que se carga recién cuando
// alguien aprieta acuñar. La página no lo paga de entrada.

import { CFG } from "./config.js";
import { construir, grupoPara, listaDe } from "./acunacion.js";

const $ = (id) => document.getElementById(id);
const fmt = (n, loc) => n.toLocaleString(loc || "es-AR");

let listas = { club: [], foil: [] };
let wallet = null;   // { proveedor, address }

// ---------- RPC ----------
async function rpc(metodo, params) {
  const r = await fetch(CFG.RPC, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ jsonrpc: "2.0", id: 1, method: metodo, params }),
  });
  const d = await r.json();
  if (d.error) throw new Error(d.error.message);
  return d.result;
}

async function saldoDe(address) {
  const r = await rpc("getTokenAccountsByOwner",
    [address, { mint: CFG.MINT }, { encoding: "jsonParsed" }]);
  return (r.value || []).reduce((t, c) =>
    t + Number(c.account.data.parsed.info.tokenAmount.uiAmount || 0), 0);
}

async function supplyActual() {
  const r = await rpc("getTokenSupply", [CFG.MINT]);
  return Number(r.value.uiAmountString);
}

// Coleccionistas: billeteras que tienen al menos una carta. Sale de la colección
// cuando esté desplegada; hasta entonces es 0 y no inventa nada.
async function contarColeccionistas() {
  if (!CFG.COLECCION) return 0;
  try {
    const r = await rpc("getAssetsByGroup", {
      groupKey: "collection", groupValue: CFG.COLECCION, page: 1, limit: 1000,
    });
    return new Set((r.items || []).map((i) => i.ownership?.owner).filter(Boolean)).size;
  } catch { return 0; }
}

// ---------- contador ----------
export async function refrescarContador() {
  try {
    const supply = await supplyActual();
    const coleccionistas = await contarColeccionistas();
    const quemado = Math.max(0, CFG.SUPPLY_BASE - supply);
    // piso de cartas: si todas fueran Gentle. No exagera.
    const hechas = Math.floor(quemado / CFG.PRECIO_GENTLE);
    // El tope sale de la lista real, no de una constante: es la que produjo el
    // merkle root que está on-chain, así que no puede desincronizarse.
    const club = listas.club.length;
    const meta = club * CFG.PRECIO_GENTLE;
    const loc = document.documentElement.lang === "en" ? "en-US" : "es-AR";

    // La etiqueta del tope también se escribe desde acá, por lo mismo. Hay una
    // por idioma: el CSS muestra la que corresponde.
    if ($("m-tope"))    $("m-tope").textContent    = fmt(meta, "es-AR");
    if ($("m-tope-en")) $("m-tope-en").textContent = fmt(meta, "en-US");

    $("m-quemado").textContent = fmt(quemado, loc);
    $("m-hechas").textContent = fmt(hechas, loc);
    $("m-quedan").textContent = fmt(coleccionistas, loc);
    $("b-quemado").style.width = (quemado / meta * 100).toFixed(1) + "%";
    $("m-barra").style.width = Math.min(100, hechas / CFG.CARTAS_META * 100).toFixed(1) + "%";
    $("b-quedan").style.width = Math.min(100, coleccionistas / club * 100).toFixed(1) + "%";
  } catch (e) {
    console.warn("no se pudo leer el supply:", e.message);
  }
}

// ---------- wallet ----------
const esMovil = () =>
  /Android|iPhone|iPad|iPod/i.test(navigator.userAgent) ||
  (navigator.maxTouchPoints > 1 && /Macintosh/.test(navigator.userAgent));

function proveedores() {
  const p = [];
  if (window.phantom?.solana?.isPhantom) p.push(["Phantom", window.phantom.solana]);
  else if (window.solana?.isPhantom) p.push(["Phantom", window.solana]);
  if (window.solflare?.isSolflare) p.push(["Solflare", window.solflare]);
  if (window.backpack?.isBackpack) p.push(["Backpack", window.backpack]);
  return p;
}

async function conectar() {
  const ps = proveedores();
  if (!ps.length) {
    // En el navegador del celular no hay wallet inyectada: mandarlo a
    // phantom.app no sirve de nada. El deep link abre ESTA página adentro del
    // navegador de Phantom, que sí inyecta el proveedor.
    if (esMovil()) {
      estado("es", "Abriendo Phantom…", "Opening Phantom…");
      const u = encodeURIComponent(location.href);
      location.href = `https://phantom.app/ul/browse/${u}?ref=${encodeURIComponent(location.origin)}`;
      return;
    }
    estado("es", "No encontramos ninguna wallet de Solana. Instalá Phantom y volvé.",
                 "No Solana wallet found. Install Phantom and come back.");
    window.open("https://phantom.app/download", "_blank", "noopener");
    return;
  }
  const [nombre, prov] = ps[0];
  try {
    const res = await prov.connect();
    const address = (res?.publicKey || prov.publicKey).toString();
    wallet = { nombre, prov, address };
    await revisar();
  } catch (e) {
    estado("es", "Conexión cancelada.", "Connection cancelled.");
  }
}

function corto(a) { return a.slice(0, 4) + "…" + a.slice(-4); }

// silencioso: actualiza los flags y el saldo sin tocar el cartel, para no
// pisar el mensaje de éxito recién puesto.
async function revisar(silencioso) {
  const es = document.documentElement.lang !== "en";
  estado("es", "Leyendo tu billetera…", "Reading your wallet…");

  let saldo = 0;
  try { saldo = await saldoDe(wallet.address); }
  catch (e) {
    estado("es", "No pudimos leer tu saldo. Probá de nuevo en un minuto.",
                 "Couldn't read your balance. Try again in a minute.");
    return;
  }

  const enClub  = listas.club.includes(wallet.address);
  const enFoil  = listas.foil.includes(wallet.address);
  const alcanza = saldo >= CFG.PRECIO_GENTLE;
  const loc = es ? "es-AR" : "en-US";
  const s = fmt(Math.floor(saldo), loc);

  let clase = "no", txtEs, txtEn;
  if (enFoil) {
    clase = "si foil";
    txtEs = `${corto(wallet.address)} · ${s} MAGAIBA. Estás en el club y la Ultra Gentle te sale 710.000: el foil no te lo cobramos.`;
    txtEn = `${corto(wallet.address)} · ${s} MAGAIBA. You're in the club, and the Ultra Gentle costs you 710,000 — we don't charge you foil.`;
  } else if (enClub || alcanza) {
    clase = "si";
    const n = Math.floor(saldo / CFG.PRECIO_GENTLE);
    txtEs = `${corto(wallet.address)} · ${s} MAGAIBA. Te alcanza para ${n} ${n === 1 ? "carta" : "cartas"}.`;
    txtEn = `${corto(wallet.address)} · ${s} MAGAIBA. Enough for ${n} card${n === 1 ? "" : "s"}.`;
  } else {
    const falta = fmt(Math.ceil(CFG.PRECIO_GENTLE - saldo), loc);
    txtEs = `${corto(wallet.address)} · ${s} MAGAIBA. Te faltan ${falta} para llegar a los 710.000 del airdrop.`;
    txtEn = `${corto(wallet.address)} · ${s} MAGAIBA. You're ${falta} short of the 710,000 from the airdrop.`;
  }
  if (!silencioso) estado(clase, txtEs, txtEn);
  document.documentElement.dataset.elegible = (enClub || alcanza) ? "si" : "no";
  document.documentElement.dataset.foilgratis = enFoil ? "si" : "no";
}

function estado(clase, es, en) {
  const c = $("wstate");
  if (!c) return;
  c.className = "wstate " + (clase === "es" ? "" : clase);
  c.innerHTML = `<span class="l-es">${es}</span><span class="l-en">${en}</span>`;
}

// El cartel de estado vive arriba de la grilla, así que al acuñar desde una
// carta queda fuera de pantalla y parece que no pasó nada. Cuando el mensaje
// viene de un clic en una carta, se lo trae a la vista.
function estadoAcunar(clase, es, en) {
  estado(clase, es, en);
  const c = $("wstate");
  if (c && typeof c.scrollIntoView === "function") {
    c.scrollIntoView({ behavior: "smooth", block: "center" });
  }
}

// ---------- acuñar ----------

// El bundle con umi + mpl-candy-machine. Se baja una sola vez, y recién cuando
// hace falta: en la primera acuñación de la sesión.
// CFG.RPC es relativa ("/rpc") porque el proxy vive en el mismo dominio. El
// fetch del contador la resuelve solo, pero umi exige URL absoluta y si no
// tira "Endpoint URL must start with http: or https:".
function rpcAbsoluto() {
  return /^https?:/i.test(CFG.RPC) ? CFG.RPC : new URL(CFG.RPC, location.origin).href;
}

// sendAndConfirm() de umi confirma por WebSocket (signatureSubscribe), y el
// proxy /rpc es sólo HTTP: la promesa nunca resuelve y la acuñación se cuelga
// después de firmar. Se manda y se consulta el estado por HTTP, que es lo que
// el proxy sí deja pasar.
async function mandar(s, umi, tb) {
  const firma = await tb.send(umi);
  const f58 = s.base58.deserialize(firma)[0];

  for (let i = 0; i < 90; i++) {
    await new Promise((r) => setTimeout(r, 1000));
    let st;
    try {
      const r = await fetch(rpcAbsoluto(), {
        method: "POST",
        headers: { "content-type": "application/json" },
        body: JSON.stringify({
          jsonrpc: "2.0", id: 1, method: "getSignatureStatuses",
          params: [[f58], { searchTransactionHistory: true }],
        }),
      });
      st = (await r.json())?.result?.value?.[0];
    } catch { continue; }   // un corte de red no cancela la espera

    if (!st) continue;
    if (st.err) throw new Error(`La red rechazó la transacción: ${JSON.stringify(st.err)}`);
    if (st.confirmationStatus === "confirmed" || st.confirmationStatus === "finalized") return f58;
  }
  throw new Error(`No confirmó en 90 s. Puede haber entrado igual: revisá https://solscan.io/tx/${f58}`);
}

let sdk = null;
async function cargarSdk() {
  if (!sdk) sdk = await import("./vendor-mint.js");
  return sdk;
}

// Los errores del Candy Guard llegan como códigos. Traducirlos es la diferencia
// entre "no anduvo" y saber qué hacer.
function traducir(e) {
  const t = (e?.message || String(e));
  // El guard solPayment avisa antes de empezar; el "insufficient lamports" salta
  // más tarde, cuando ya pagó el solPayment y no le alcanza para las rentas del
  // NFT. Los dos son lo mismo para quien está del otro lado: falta SOL.
  if (/NotEnoughSOL|6018|insufficient lamports/i.test(t))
    return ["Te falta SOL. Una acuñación necesita unos 0,07 SOL: 0,05 del precio y el resto en comisiones y renta de las cuentas del NFT.",
            "Not enough SOL. A mint needs about 0.07 SOL: 0.05 for the price and the rest in fees and rent for the NFT accounts."];
  if (/NotEnoughTokens|6015|insufficient funds/i.test(t))
    return ["No te alcanzan los MAGAIBA para quemar.",
            "You don't have enough MAGAIBA to burn."];
  if (/AddressNotFoundInAllowedList|allow ?list|6008/i.test(t))
    return ["Esta billetera no está en la lista.",
            "This wallet isn't on the list."];
  if (/CandyMachineEmpty|6001|index greater/i.test(t))
    return ["No quedan ediciones de esta carta.",
            "No editions left for this card."];
  if (/User rejected|rejected the request|4001/i.test(t))
    return ["Cancelaste la firma.", "You cancelled the signature."];
  if (/blockhash|expired|timeout/i.test(t))
    return ["La transacción venció antes de confirmar. Probá de nuevo.",
            "The transaction expired before confirming. Try again."];
  // Los errores del SDK vienen con el volcado entero de logs del programa.
  // Se muestra sólo la primera línea, y el resto queda en la consola.
  const corto = t.split("\n")[0].split(" Source:")[0].slice(0, 180);
  return [`No se pudo acuñar: ${corto}`, `Mint failed: ${corto}`];
}

export async function acunar(carta, foil, nombre) {
  if (!wallet) { await conectar(); return; }

  const maquina = CFG.MAQUINAS[carta]?.[foil ? "foil" : "gentle"];
  if (!maquina) {
    estadoAcunar("no",
      "La acuñación todavía no abrió. Cuando abra, este mismo botón la ejecuta.",
      "Minting hasn't opened yet. When it does, this same button runs it.");
    return;
  }

  try {
    estadoAcunar("es", "Preparando la transacción…", "Preparing the transaction…");
    const s = await cargarSdk();
    const umi = s.createUmi(rpcAbsoluto())
      .use(s.mplTokenMetadata())
      .use(s.mplCandyMachine())
      .use(s.walletAdapterIdentity(wallet.prov));

    const enFoil36 = listas.foil.includes(wallet.address);
    const grupo = grupoPara(foil, enFoil36);
    const lista = listaDe(grupo, listas);

    const { tbRoute, tbMint } = await construir(s, umi, {
      maquina, grupo, lista,
      minter: wallet.address,
      mintToken: CFG.MINT,
      tesoro: CFG.TESORO,
    });

    // El proof va aparte: juntas las dos instrucciones pasan los 1.232 bytes.
    // La PDA queda en la chain, así que esto se firma una vez por carta.
    if (tbRoute) {
      estadoAcunar("es", "Firma 1 de 2: habilitar la billetera.",
                   "Signature 1 of 2: enable the wallet.");
      await mandar(s, umi, tbRoute);
    }

    estadoAcunar("es", tbRoute ? "Firma 2 de 2: acuñar." : "Firmá para acuñar.",
                 tbRoute ? "Signature 2 of 2: mint." : "Sign to mint.");
    const firma = await mandar(s, umi, tbMint);

    const url = `https://solscan.io/tx/${firma}`;
    const quema = fmt(grupo === "ultra" ? CFG.PRECIO_ULTRA : CFG.PRECIO_GENTLE, "es-AR");
    const quemaEn = fmt(grupo === "ultra" ? CFG.PRECIO_ULTRA : CFG.PRECIO_GENTLE, "en-US");
    const clase = foil ? "Ultra Gentle" : "Gentle";
    const cual = nombre ? `<b>${nombre}</b>` : `la carta ${carta}`;
    const cualEn = nombre ? `<b>${nombre}</b>` : `card ${carta}`;
    const regalo = grupo === "foil36"
      ? ' <span class="premio">El foil no te lo cobramos: estás en las 36.</span>' : "";
    const regaloEn = grupo === "foil36"
      ? ' <span class="premio">The foil is on us: you\'re one of the 36.</span>' : "";

    estadoAcunar("si",
      `🎴 Es tuya. Acuñaste ${cual} en <b>${clase}</b> y quemaste <b>${quema} MAGAIBA</b>, `
      + `que ya no existen más.${regalo}<br>`
      + `<a href="${url}" target="_blank" rel="noopener">Ver la transacción</a><br>`
      + `<span class="tip">Si no la ves en Phantom, está oculta: <b>Collectibles → los tres `
      + `puntos → Manage Collectibles</b>, y la activás. Phantom esconde las colecciones que `
      + `todavía no conoce. <a href="https://help.phantom.com/hc/en-us/articles/12983715032083-How-to-manage-hidden-NFTs-in-Phantom" target="_blank" rel="noopener">Cómo se hace</a></span>`,
      `🎴 It's yours. You minted ${cualEn} in <b>${clase}</b> and burned <b>${quemaEn} MAGAIBA</b>, `
      + `gone for good.${regaloEn}<br>`
      + `<a href="${url}" target="_blank" rel="noopener">See the transaction</a><br>`
      + `<span class="tip">If you don't see it in Phantom, it's hidden: <b>Collectibles → three `
      + `dots → Manage Collectibles</b>, then toggle it on. Phantom hides collections it doesn't `
      + `know yet. <a href="https://help.phantom.com/hc/en-us/articles/12983715032083-How-to-manage-hidden-NFTs-in-Phantom" target="_blank" rel="noopener">How to do it</a></span>`);

    await refrescarContador();
    await revisar(true);   // sin pisar el mensaje
  } catch (e) {
    const [es, en] = traducir(e);
    estadoAcunar("no", es, en);
    console.error(e);
  }
}

// ---------- arranque ----------
export async function iniciarMint() {
  try {
    listas = await (await fetch("./allowlist.json")).json();
  } catch { /* sin listas: se cae al chequeo por saldo */ }

  const b = $("conectar");
  if (b) b.onclick = conectar;

  await refrescarContador();
  setInterval(refrescarContador, 60_000);

  // si la wallet ya autorizó el sitio antes, entra sola
  const ps = proveedores();
  if (ps.length) {
    try {
      const [nombre, prov] = ps[0];
      const res = await prov.connect({ onlyIfTrusted: true });
      wallet = { nombre, prov, address: (res?.publicKey || prov.publicKey).toString() };
      await revisar();
    } catch { /* no estaba autorizada, que apriete el botón */ }
  }
}
