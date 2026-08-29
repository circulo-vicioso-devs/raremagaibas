import { getMerkleRoot } from "@metaplex-foundation/mpl-candy-machine";
import fs from "node:fs";
const base = "/home/realjuanruocco/Escritorio/cripto/magaiba/data/";
const out = {};
for (const l of ["club", "foil"]) {
  const ws = fs.readFileSync(base + `allowlist_${l}.csv`, "utf8").trim().split("\n").map(s => s.trim()).filter(Boolean);
  const root = getMerkleRoot(ws);
  out[l] = { n: ws.length, root: Buffer.from(root).toString("hex") };
  console.log(`  ${l.padEnd(5)} ${ws.length} wallets → ${out[l].root}`);
}
fs.writeFileSync(base + "merkle.json", JSON.stringify(out, null, 1));
