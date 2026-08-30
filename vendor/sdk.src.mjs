// Entrada del bundle. Sólo reexporta lo que usa mint.js: esbuild recorta el
// resto. No poner lógica acá — la lógica va en mint.js, que se edita a mano.
//
//   npm run build   →   vendor-mint.js

export { createUmi } from "@metaplex-foundation/umi-bundle-defaults";
export { walletAdapterIdentity } from "@metaplex-foundation/umi-signer-wallet-adapters";
export { mplTokenMetadata } from "@metaplex-foundation/mpl-token-metadata";
export { setComputeUnitLimit } from "@metaplex-foundation/mpl-toolbox";

export {
  mplCandyMachine,
  mintV2,
  route,
  getMerkleRoot,
  getMerkleProof,
  fetchCandyMachine,
  safeFetchCandyGuard,
  safeFetchAllowListProofFromSeeds,
  findAllowListProofPda,
} from "@metaplex-foundation/mpl-candy-machine";

export {
  publicKey,
  generateSigner,
  some,
  none,
  sol,
  transactionBuilder,
  base58,
} from "@metaplex-foundation/umi";
