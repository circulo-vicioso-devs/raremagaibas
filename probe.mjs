import { createUmi } from "@metaplex-foundation/umi-bundle-defaults";
import { mplCandyMachine, fetchCandyMachine, safeFetchCandyGuard } from "@metaplex-foundation/mpl-candy-machine";
import { mplTokenMetadata, fetchDigitalAsset } from "@metaplex-foundation/mpl-token-metadata";
import { publicKey } from "@metaplex-foundation/umi";

const umi = createUmi(process.env.RPC).use(mplTokenMetadata()).use(mplCandyMachine());
const CM = publicKey("44QWm4EEFt5zioAuBT5WvfA95776J9AESDikompKy8mV"); // carta-001 gentle

const cm = await fetchCandyMachine(umi, CM);
console.log("  candy machine   :", CM);
console.log("  authority       :", cm.authority);
console.log("  mintAuthority   :", cm.mintAuthority, "(= candy guard)");
console.log("  collectionMint  :", cm.collectionMint);
console.log("  itemsLoaded     :", cm.itemsLoaded);
console.log("  itemsRedeemed   :", cm.itemsRedeemed.toString());
console.log("  itemsAvailable  :", cm.data.itemsAvailable.toString());

const guard = await safeFetchCandyGuard(umi, cm.mintAuthority);
console.log("\n  candy guard     :", guard.publicKey);
console.log("  grupos          :", guard.groups.map(g => g.label).join(", "));
for (const g of guard.groups) {
  const gu = g.guards;
  console.log(`   · ${g.label}:`,
    "tokenBurn=" + (gu.tokenBurn.__option === "Some" ? gu.tokenBurn.value.amount : "no"),
    "solPayment=" + (gu.solPayment.__option === "Some" ? gu.solPayment.value.lamports.basisPoints : "no"),
    "allowList=" + (gu.allowList.__option === "Some" ? Buffer.from(gu.allowList.value.merkleRoot).toString("hex").slice(0,12) : "no"));
}

const col = await fetchDigitalAsset(umi, cm.collectionMint);
console.log("\n  collection name :", col.metadata.name);
console.log("  updateAuthority :", col.metadata.updateAuthority, "  ← collectionUpdateAuthority");
