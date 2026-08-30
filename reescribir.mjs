// Reescribe las líneas de configuración de las 24 Candy Machines para que
// apunten a las cartas compuestas, en vez de a los memes crudos que se
// subieron en el despliegue.
//
//   source ~/.config/solana/helius.env
//   node reescribir.mjs --ver     muestra qué cambiaría, sin tocar nada
//   node reescribir.mjs           lo hace
//
// La máquina guarda sólo los sufijos: el prefijo "https://arweave.net/" y el
// nombre viven en configLineSettings. Cada línea son 43 caracteres del id de
// Arweave más 6 del número de edición, así que entran de a muchas.
//
// ⚠️ Las ediciones ya acuñadas NO cambian: su metadata es inmutable y vive en
// el NFT, no en la máquina. Reescribirlas es inofensivo pero inútil.
import { createUmi } from "@metaplex-foundation/umi-bundle-defaults";
import { mplCandyMachine, fetchCandyMachine, addConfigLines } from "@metaplex-foundation/mpl-candy-machine";
import { publicKey, createSignerFromKeypair, signerIdentity, base58 } from "@metaplex-foundation/umi";
import fs from "node:fs";
import path from "node:path";

const AQUI = path.join(path.dirname(new URL(import.meta.url).pathname), "..");
const MAPA = JSON.parse(fs.readFileSync(path.join(AQUI, "data/naipes-arweave.json"), "utf8"));
const CFG = fs.readFileSync(path.join(AQUI, "web/config.js"), "utf8");
const VER = process.argv.includes("--ver");
const LOTE = 12;                       // líneas por transacción

const rpc = process.env.RPC || `https://mainnet.helius-rpc.com/?api-key=${process.env.HELIUS_KEY}`;
const umi = createUmi(rpc).use(mplCandyMachine());
const secreto = Uint8Array.from(JSON.parse(
  fs.readFileSync(process.env.HOME + "/.config/solana/raremagaibas.json", "utf8")));
const kp = umi.eddsa.createKeypairFromSecretKey(secreto);
umi.use(signerIdentity(createSignerFromKeypair(umi, kp)));
console.log(`  autoridad: ${kp.publicKey}\n`);

// carpeta de deploy -> dirección de la máquina, desde config.js
const maquinas = {};
for (const m of CFG.matchAll(/"(\d{3})":\s*\{\s*foil:\s*"([^"]+)",\s*gentle:\s*"([^"]+)"/g)) {
  maquinas[`carta-${m[1]}-foil`] = m[2];
  maquinas[`carta-${m[1]}`] = m[3];
}

let cambios = 0, saltadas = 0, tx = 0;

for (const carpeta of Object.keys(MAPA).sort()) {
  const dir = maquinas[carpeta];
  if (!dir) { console.log(`  ${carpeta}: sin máquina en config.js`); continue; }
  const meta = MAPA[carpeta].metadatos || {};

  const cm = await fetchCandyMachine(umi, publicKey(dir));
  const pref = cm.data.configLineSettings.value.prefixUri;   // https://arweave.net/

  // sólo se toca lo que de verdad cambia
  const lineas = [];
  for (let i = 0; i < cm.items.length; i++) {
    const nueva = meta[i];
    if (!nueva) continue;
    if (cm.items[i].uri === nueva) { saltadas++; continue; }
    lineas.push({ i, name: cm.items[i].name.replace(cm.data.configLineSettings.value.prefixName, ""),
                  uri: nueva.replace(pref, "") });
  }
  if (!lineas.length) { console.log(`  ${carpeta}: al día`); continue; }

  const acu = cm.items.filter((x) => x.minted).length;
  console.log(`  ${carpeta}  ${lineas.length} líneas${acu ? `  (${acu} ya acuñada${acu > 1 ? "s" : ""}, no cambian)` : ""}`);
  cambios += lineas.length;
  if (VER) continue;

  // en lotes contiguos, que es como los acepta el programa
  for (let k = 0; k < lineas.length; k += LOTE) {
    const trozo = lineas.slice(k, k + LOTE);
    const cont = trozo.every((l, n) => n === 0 || l.i === trozo[n - 1].i + 1);
    if (!cont) throw new Error("las líneas no son contiguas; bajá LOTE");
    const r = await addConfigLines(umi, {
      candyMachine: publicKey(dir),
      index: trozo[0].i,
      configLines: trozo.map((l) => ({ name: l.name, uri: l.uri })),
    }).sendAndConfirm(umi, { confirm: { commitment: "confirmed" } });
    tx++;
    console.log(`    ${trozo[0].i}-${trozo[trozo.length - 1].i}  ${base58.deserialize(r.signature)[0].slice(0, 16)}…`);
  }
}

console.log(`\n  ${cambios} líneas ${VER ? "a reescribir" : `reescritas en ${tx} transacciones`} · ${saltadas} ya estaban bien`);
