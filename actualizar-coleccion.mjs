// Apunta el NFT de la colección a la metadata corregida.
//
//   source ~/.config/solana/helius.env
//   node actualizar-coleccion.mjs <uri>
//
// La colección es isMutable:true, así que su update authority puede cambiarle
// la URI. Los NFT ya acuñados NO cambian: son inmutables y su metadata vive en
// cada uno. Esto sólo arregla lo que los marketplaces muestran de la colección.
import { createUmi } from "@metaplex-foundation/umi-bundle-defaults";
import { mplTokenMetadata, fetchDigitalAsset, updateV1 } from "@metaplex-foundation/mpl-token-metadata";
import { publicKey, createSignerFromKeypair, signerIdentity, some, base58 } from "@metaplex-foundation/umi";
import fs from "node:fs";

const uri = process.argv[2];
if (!uri) { console.error("falta la uri"); process.exit(1); }

const umi = createUmi(process.env.RPC).use(mplTokenMetadata());
const kp = umi.eddsa.createKeypairFromSecretKey(Uint8Array.from(
  JSON.parse(fs.readFileSync(process.env.HOME + "/.config/solana/raremagaibas.json", "utf8"))));
umi.use(signerIdentity(createSignerFromKeypair(umi, kp)));

const COL = publicKey("DsC9cF8DMYCvFpaJWVGZNZH2J7tEZe4TaYMxBmH2S7ws");
const antes = await fetchDigitalAsset(umi, COL);
console.log("  autoridad :", kp.publicKey);
console.log("  antes     :", antes.metadata.uri);
if (antes.metadata.uri === uri) { console.log("  ya está apuntada ahí"); process.exit(0); }

// data lleva SÓLO estos cinco campos. Pasarle el objeto metadata entero hace
// que el serializador ignore el cambio y la transacción pase sin efecto.
const m = antes.metadata;
const r = await updateV1(umi, {
  mint: COL,
  authority: umi.identity,
  data: some({
    name: m.name,
    symbol: m.symbol,
    uri,
    sellerFeeBasisPoints: m.sellerFeeBasisPoints,
    creators: m.creators,
  }),
}).sendAndConfirm(umi, { confirm: { commitment: "confirmed" } });
console.log("  firma     :", base58.deserialize(r.signature)[0]);

await new Promise(r => setTimeout(r, 3000));   // que el RPC deje de servir el estado viejo
const desp = await fetchDigitalAsset(umi, COL);
console.log("  después   :", desp.metadata.uri);
console.log(desp.metadata.uri === uri ? "  ✓ actualizada" : "  ✗ no cambió");
