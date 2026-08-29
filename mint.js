// Conexión de wallet, elegibilidad y contador en vivo.
//
// Lo que hace hoy, de verdad y contra la chain:
//   · conecta Phantom / Solflare / Backpack
//   · lee cuánto MAGAIBA tiene la billetera y si llega a los 710.000
//   · dice si está en la lista del club y si le toca el foil sin plus
//   · lee el supply del token y muestra cuánto se quemó desde que abrió
//
// Lo que falta es la acuñación en sí: necesita la Candy Machine desplegada.
// Cuando exista, se pone su dirección en config.js y se conecta acá abajo.

import { CFG } from "./config.js";

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
    const meta = CFG.META_QUEMA;
    const loc = document.documentElement.lang === "en" ? "en-US" : "es-AR";

    $("m-quemado").textContent = fmt(quemado, loc);
    $("m-hechas").textContent = fmt(hechas, loc);
    $("m-quedan").textContent = fmt(coleccionistas, loc);
    $("b-quemado").style.width = (quemado / meta * 100).toFixed(1) + "%";
    $("m-barra").style.width = Math.min(100, hechas / CFG.CARTAS_META * 100).toFixed(1) + "%";
    $("b-quedan").style.width = Math.min(100, coleccionistas / CFG.CLUB * 100).toFixed(1) + "%";
  } catch (e) {
    console.warn("no se pudo leer el supply:", e.message);
  }
}

// ---------- wallet ----------
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
    estado("es", "No encontramos ninguna wallet de Solana. Instalá Phantom y volvé.",
                 "No Solana wallet found. Install Phantom and come back.");
    window.open("https://phantom.app/", "_blank", "noopener");
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

async function revisar() {
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
  estado(clase, txtEs, txtEn);
  document.documentElement.dataset.elegible = (enClub || alcanza) ? "si" : "no";
  document.documentElement.dataset.foilgratis = enFoil ? "si" : "no";
}

function estado(clase, es, en) {
  const c = $("wstate");
  if (!c) return;
  c.className = "wstate " + (clase === "es" ? "" : clase);
  c.innerHTML = `<span class="l-es">${es}</span><span class="l-en">${en}</span>`;
}

// ---------- acuñar ----------
export async function acunar(carta, foil) {
  if (!wallet) { await conectar(); return; }
  if (!CFG.MAQUINAS[carta]) {
    estado("no",
      "La acuñación todavía no abrió. Cuando abra, este mismo botón la ejecuta.",
      "Minting hasn't opened yet. When it does, this same button runs it.");
    return;
  }
  // Con las máquinas desplegadas, acá va la transacción. Una por carta, y el
  // grupo del guard decide si es gentle, ultra o el foil sin plus de las 36.
  //   const grupo = foil ? (esDeLas36 ? "foilclub" : "ultra") : "gentle";
  //   mintV2(umi, { candyMachine: CFG.MAQUINAS[carta], group: grupo,
  //                 mintArgs: { tokenBurn: {...}, solPayment: {...},
  //                             allowList: { merkleRoot } } })
  estado("no", "Falta conectar la Candy Machine.", "Candy Machine not wired yet.");
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
