// Simula una acuñación sin gastar nada y sin necesitar la clave privada.
//
//   source ~/.config/solana/helius.env
//   node simular.mjs <wallet> <carta> [foil]
//
// Arma la MISMA transacción que el navegador (usa acunacion.js, el módulo
// compartido) y la manda a simulateTransaction con sigVerify:false. El programa
// corre de verdad contra el estado actual de la chain: valida el merkle proof,
// el tokenBurn, el solPayment y que haya ítems. No firma ni manda nada.
import { createUmi } from "@metaplex-foundation/umi-bundle-defaults";
import { walletAdapterIdentity } from "@metaplex-foundation/umi-signer-wallet-adapters";
import { mplTokenMetadata } from "@metaplex-foundation/mpl-token-metadata";
import { setComputeUnitLimit } from "@metaplex-foundation/mpl-toolbox";
import {
  mplCandyMachine, mintV2, route, getMerkleRoot, getMerkleProof,
  fetchCandyMachine, safeFetchCandyGuard, safeFetchAllowListProofFromSeeds,
  findAllowListProofPda,
} from "@metaplex-foundation/mpl-candy-machine";
import {
  publicKey, generateSigner, some, none, sol, transactionBuilder, base58,
  createNoopSigner, signerIdentity,
} from "@metaplex-foundation/umi";
import fs from "node:fs";
import { construir, grupoPara, listaDe } from "./acunacion.js";
import { CFG } from "./config.js";

const s = {
  createUmi, walletAdapterIdentity, mplTokenMetadata, setComputeUnitLimit,
  mplCandyMachine, mintV2, route, getMerkleRoot, getMerkleProof,
  fetchCandyMachine, safeFetchCandyGuard, safeFetchAllowListProofFromSeeds,
  findAllowListProofPda, publicKey, generateSigner, some, none, sol,
  transactionBuilder, base58,
};

const [wallet, carta, foilArg] = process.argv.slice(2);
if (!wallet || !carta) {
  console.error("uso: node simular.mjs <wallet> <carta 001-012> [foil]");
  process.exit(1);
}
const foil = foilArg === "foil";
const rpc = process.env.RPC || `https://mainnet.helius-rpc.com/?api-key=${process.env.HELIUS_KEY}`;

const listas = JSON.parse(fs.readFileSync("./allowlist.json", "utf8"));
const umi = createUmi(rpc).use(mplTokenMetadata()).use(mplCandyMachine())
  .use(signerIdentity(createNoopSigner(publicKey(wallet))));

const enFoil36 = listas.foil.includes(wallet);
const grupo = grupoPara(foil, enFoil36);
const lista = listaDe(grupo, listas);
const maquina = CFG.MAQUINAS[carta]?.[foil ? "foil" : "gentle"];
if (!maquina) { console.error(`no hay máquina para la carta ${carta}`); process.exit(1); }

console.log(`  wallet    ${wallet}`);
console.log(`  carta     ${carta}${foil ? " (foil)" : ""}`);
console.log(`  grupo     ${grupo}${enFoil36 ? "   (la wallet está en las 36)" : ""}`);
console.log(`  máquina   ${maquina}`);
console.log(`  lista     ${grupo === "foil36" ? "foil" : "club"} (${lista.length})`);

const { tbRoute, tbMint, cm, yaTenia } = await construir(s, umi, {
  maquina, grupo, lista, minter: wallet,
  mintToken: CFG.MINT, tesoro: CFG.TESORO,
});
console.log(`  proof PDA ${yaTenia ? "ya existe → no hace falta route" : "no existe → hay que correr route primero"}`);
console.log(`  ítems     ${cm.itemsRedeemed}/${cm.data.itemsAvailable} acuñados`);

async function simular(nombre, tb) {
  const conBh = await tb.setLatestBlockhash(umi);
  const tx = conBh.build(umi);
  const bytes = umi.transactions.serialize(tx);
  const cabe = bytes.length <= 1232;
  console.log(`\n  ── ${nombre} ──`);
  console.log(`  tamaño    ${bytes.length} bytes  ${cabe ? "✓ entra" : "✗ PASA EL LÍMITE DE 1232"}`);
  if (!cabe) return false;

  const r = await fetch(rpc, {
    method: "POST", headers: { "content-type": "application/json" },
    body: JSON.stringify({ jsonrpc: "2.0", id: 1, method: "simulateTransaction",
      params: [Buffer.from(bytes).toString("base64"),
               { sigVerify: false, replaceRecentBlockhash: true, encoding: "base64", commitment: "confirmed" }] }),
  });
  const d = await r.json();
  if (d.error) { console.log("  RPC error:", d.error.message); return false; }
  const v = d.result.value;
  console.log(`  unidades  ${v.unitsConsumed}`);
  if (v.err) {
    console.log(`  RESULTADO ✗ ${JSON.stringify(v.err)}`);
    for (const l of (v.logs || []).slice(-8)) console.log("     ", l);
    return false;
  }
  console.log("  RESULTADO ✓ pasaría");
  for (const l of (v.logs || []).slice(-5)) console.log("     ", l);
  return true;
}

if (tbRoute) await simular("transacción 1: route (proof)", tbRoute);
await simular("transacción 2: mintV2", tbMint);
