import { createUmi } from "@metaplex-foundation/umi-bundle-defaults";
import { mplCandyMachine, fetchCandyMachine } from "@metaplex-foundation/mpl-candy-machine";
import { publicKey } from "@metaplex-foundation/umi";
import fs from "node:fs";
const umi = createUmi(process.env.RPC).use(mplCandyMachine());
const cfg = fs.readFileSync("config.js","utf8");
const maq = [];
for (const m of cfg.matchAll(/"(\d{3})":\s*\{\s*foil:\s*"([^"]+)",\s*gentle:\s*"([^"]+)"/g)) {
  maq.push([`${m[1]} gentle`, m[3]], [`${m[1]} foil`, m[2]]);
}
let vacias=0, total=0, quedan=0;
for (const [n,a] of maq) {
  const cm = await fetchCandyMachine(umi, publicKey(a));
  const r = Number(cm.itemsRedeemed), t = Number(cm.data.itemsAvailable);
  total+=t; quedan+=t-r;
  if (r>=t) vacias++;
  if (r>0) console.log(`  ${n.padEnd(12)} ${r}/${t}${r>=t?"   ✗ AGOTADA":""}`);
}
console.log(`\n  quedan ${quedan} de ${total} · máquinas agotadas: ${vacias}`);
