// Sube los assets de una carpeta a Arweave por Turbo (ArDrive) y arma el
// cache.json que espera Sugar.
//
// Existe porque Sugar 2.9.1 apunta a node1.bundlr.network, que ya no existe.
//
//   node subir.mjs <carpeta-de-la-carta>

import { TurboFactory, HexSolanaSigner } from "@ardrive/turbo-sdk";
import fs from "node:fs";
import path from "node:path";
import * as bs58mod from "bs58";
const bs58 = bs58mod.default ?? bs58mod;

const dir = process.argv[2];
if (!dir) { console.error("falta la carpeta"); process.exit(1); }

const kp = JSON.parse(fs.readFileSync(process.env.HOME + "/.config/solana/raremagaibas.json"));
const signer = new HexSolanaSigner(bs58.encode(Uint8Array.from(kp)));
const turbo = TurboFactory.authenticated({ signer, token: "solana" });

const assets = path.join(dir, "assets");
const archivos = fs.readdirSync(assets);
const pngs = archivos.filter(f => f.endsWith(".png")).sort();

async function subir(file, type) {
  const p = path.join(assets, file);
  const size = fs.statSync(p).size;
  const r = await turbo.uploadFile({
    fileStreamFactory: () => fs.createReadStream(p),
    fileSizeFactory: () => size,
    dataItemOpts: { tags: [{ name: "Content-Type", value: type }] },
  });
  return `https://arweave.net/${r.id}`;
}

const cache = {
  program: { candyMachine: "", candyGuard: "", candyMachineCreator: "", collectionMint: "" },
  items: {},
};
const yaSubido = {};   // misma imagen → misma URI, no la subimos 25 veces

for (const png of pngs) {
  const base = png.replace(/\.png$/, "");
  const jsonF = base + ".json";
  if (!fs.existsSync(path.join(assets, jsonF))) continue;

  const hash = fs.readFileSync(path.join(assets, png)).length;   // todas iguales dentro de la carpeta
  if (!yaSubido[hash]) {
    yaSubido[hash] = await subir(png, "image/webp");
    console.log(`  imagen → ${yaSubido[hash]}`);
  }
  const imgUri = yaSubido[hash];

  const meta = JSON.parse(fs.readFileSync(path.join(assets, jsonF), "utf8"));
  meta.image = imgUri;
  meta.properties.files = [{ uri: imgUri, type: "image/webp" }];
  const tmp = path.join(assets, ".tmp.json");
  fs.writeFileSync(tmp, JSON.stringify(meta));
  const r = await turbo.uploadFile({
    fileStreamFactory: () => fs.createReadStream(tmp),
    fileSizeFactory: () => fs.statSync(tmp).size,
    dataItemOpts: { tags: [{ name: "Content-Type", value: "application/json" }] },
  });
  fs.unlinkSync(tmp);

  const idx = base === "collection" ? "-1" : base;
  cache.items[idx] = {
    name: meta.name, image_hash: "", image_link: imgUri,
    metadata_hash: "", metadata_link: `https://arweave.net/${r.id}`, onChain: false,
  };
  if (base !== "collection") process.stdout.write(`\r  ${Object.keys(cache.items).length}/${pngs.length}`);
}
console.log();
fs.writeFileSync(path.join(dir, "cache.json"), JSON.stringify(cache, null, 1));
console.log(`  cache.json con ${Object.keys(cache.items).length} ítems`);
