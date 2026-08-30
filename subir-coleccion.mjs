// Sube la metadata corregida de la colección: el external_url apuntaba a
// github.io, y ese es el link que los marketplaces muestran como sitio oficial.
import { TurboFactory } from "@ardrive/turbo-sdk";
import { Readable } from "node:stream";
import fs from "node:fs";
import bs58 from "bs58";

const j = JSON.parse(fs.readFileSync("/tmp/colmeta.json", "utf8"));
j.external_url = "https://magaiba.xyz/raremagaiba/";
const buf = Buffer.from(JSON.stringify(j));

const kp = JSON.parse(fs.readFileSync(process.env.HOME + "/.config/solana/raremagaibas.json", "utf8"));
const turbo = TurboFactory.authenticated({ privateKey: bs58.encode(Uint8Array.from(kp)), token: "solana" });
const r = await turbo.uploadFile({
  fileStreamFactory: () => Readable.from(buf),
  fileSizeFactory: () => buf.length,
  dataItemOpts: { tags: [{ name: "Content-Type", value: "application/json" }] },
});
console.log("  nueva uri: https://arweave.net/" + r.id);
fs.writeFileSync("/tmp/coluri.txt", "https://arweave.net/" + r.id);
