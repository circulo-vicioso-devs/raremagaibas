// Sube a Arweave, con Turbo de ArDrive, las 24 cartas compuestas y los 600
// metadatos que las apuntan.
//
//   node subir-naipes.mjs          sube todo
//   node subir-naipes.mjs --solo 002-foil
//
// Sugar 2.9.1 no sirve para esto: su `upload` apunta a node1.bundlr.network,
// dominio que murió cuando Bundlr pasó a llamarse Irys, y explota parseando el
// HTML de error. Por eso se sube por acá y después se reescriben las líneas.
//
// Deja el resultado en data/naipes-arweave.json. Turbo es gratis por archivo
// de menos de 100 KB: las imágenes entran justo y los JSON pesan ~1 KB.
import { TurboFactory } from "@ardrive/turbo-sdk";
import fs from "node:fs";
import { Readable } from "node:stream";
import path from "node:path";
import bs58 from "bs58";

// El script vive en web/ para tener node_modules al lado; los datos, un nivel arriba.
const AQUI = path.join(path.dirname(new URL(import.meta.url).pathname), "..");
const WEBP = path.join(AQUI, "naipes/webp");
const DEPLOY = path.join(AQUI, "web/deploy");
const SALIDA = path.join(AQUI, "data/naipes-arweave.json");
const CONC = 8;                      // subidas en paralelo

const kp = JSON.parse(fs.readFileSync(process.env.HOME + "/.config/solana/raremagaibas.json", "utf8"));
const turbo = TurboFactory.authenticated({
  privateKey: bs58.encode(Uint8Array.from(kp)),
  token: "solana",
});

const gw = (id) => `https://arweave.net/${id}`;

async function subir(buf, tipo) {
  const r = await turbo.uploadFile({
    fileStreamFactory: () => Readable.from(buf),
    fileSizeFactory: () => buf.length,
    dataItemOpts: { tags: [{ name: "Content-Type", value: tipo }] },
  });
  return r.id;
}

async function enTanda(items, fn) {
  const out = new Array(items.length);
  let i = 0;
  await Promise.all(Array.from({ length: CONC }, async () => {
    while (i < items.length) {
      const n = i++;
      out[n] = await fn(items[n], n);
    }
  }));
  return out;
}

const carpetas = fs.readdirSync(DEPLOY).filter((d) => /^carta-\d{3}(-foil)?$/.test(d)).sort();
const solo = process.argv.includes("--solo") ? process.argv[process.argv.indexOf("--solo") + 1] : null;
const objetivo = solo ? carpetas.filter((d) => d.includes(solo)) : carpetas;

const res = fs.existsSync(SALIDA) ? JSON.parse(fs.readFileSync(SALIDA, "utf8")) : {};

for (const carpeta of objetivo) {
  const m = carpeta.match(/^carta-(\d{3})(-foil)?$/);
  const num = m[1], esFoil = !!m[2];
  const webp = path.join(WEBP, `c${num}${esFoil ? "f" : ""}.webp`);
  if (!fs.existsSync(webp)) { console.log(`  ${carpeta}: falta ${webp}`); continue; }

  res[carpeta] ??= {};
  if (!res[carpeta].imagen) {
    const id = await subir(fs.readFileSync(webp), "image/webp");
    res[carpeta].imagen = gw(id);
    fs.writeFileSync(SALIDA, JSON.stringify(res, null, 1));
    console.log(`  ${carpeta}  imagen  ${id}`);
  }

  // Los metadatos se reconstruyen sobre los que ya existían: se cambia sólo la
  // imagen y el external_url, que apuntaba a github.io en vez del dominio.
  const dirA = path.join(DEPLOY, carpeta, "assets");
  const idx = fs.readdirSync(dirA).filter((f) => /^\d+\.json$/.test(f))
    .map((f) => parseInt(f)).sort((a, b) => a - b);

  res[carpeta].metadatos ??= {};
  const faltan = idx.filter((i) => !res[carpeta].metadatos[i]);
  if (faltan.length) {
    const ids = await enTanda(faltan, async (i) => {
      const j = JSON.parse(fs.readFileSync(path.join(dirA, `${i}.json`), "utf8"));
      j.image = res[carpeta].imagen;
      j.external_url = "https://magaiba.xyz/raremagaiba/";
      j.properties.files = [{ uri: res[carpeta].imagen, type: "image/webp" }];
      return subir(Buffer.from(JSON.stringify(j)), "application/json");
    });
    faltan.forEach((i, k) => { res[carpeta].metadatos[i] = gw(ids[k]); });
    fs.writeFileSync(SALIDA, JSON.stringify(res, null, 1));
    console.log(`  ${carpeta}  ${faltan.length} metadatos`);
  }
}

const nI = Object.values(res).filter((v) => v.imagen).length;
const nM = Object.values(res).reduce((s, v) => s + Object.keys(v.metadatos || {}).length, 0);
console.log(`\n  ${nI} imágenes · ${nM} metadatos → ${SALIDA}`);
