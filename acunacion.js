// Armado de la transacción de acuñación.
//
// Este módulo no importa nada: recibe el SDK de Metaplex como parámetro (`s`).
// Así el mismo código corre en el navegador, donde el SDK sale del bundle
// vendor-mint.js, y en node para simular, donde sale de node_modules. Una sola
// versión de la lógica que mueve tokens.
//
// Cada carta tiene dos Candy Machines. La gentle lleva un grupo; la foil lleva
// dos, y el grupo decide qué cobra:
//
//   gentle   quema   710.000 · lista club  · máquina gentle
//   ultra    quema 1.000.000 · lista club  · máquina foil
//   foil36   quema   710.000 · lista foil  · máquina foil ← las 36 del club
//
// El guard allowList no valida contra la lista en el momento del mint: exige
// una PDA que se crea antes con una instrucción `route` que lleva el proof.
//
// Van en DOS transacciones, no en una: juntas dan 1.324 bytes y Solana topea en
// 1.232. La PDA queda en la chain, así que el route se paga una vez por máquina
// y las acuñaciones siguientes lo saltean.

export function grupoPara(foil, enFoil36) {
  if (!foil) return "gentle";
  return enFoil36 ? "foil36" : "ultra";
}

export function listaDe(grupo, listas) {
  return grupo === "foil36" ? listas.foil : listas.club;
}

/**
 * Devuelve { tbRoute, tbMint, ... } sin firmar ni mandar nada.
 * tbRoute es null si la wallet ya probó el proof en esta máquina.
 * `minter` es la dirección que acuña, en base58.
 */
export async function construir(s, umi, { maquina, grupo, lista, minter, mintToken, tesoro }) {
  const candyMachine = s.publicKey(maquina);
  const cm = await s.fetchCandyMachine(umi, candyMachine);
  const candyGuard = cm.mintAuthority;

  if (!lista.includes(minter)) {
    throw new Error(`La billetera no está en la lista del grupo ${grupo}.`);
  }

  const merkleRoot = s.getMerkleRoot(lista);
  const merkleProof = s.getMerkleProof(lista, minter);

  // ¿Ya probó el proof antes? Si sí, la PDA existe y el route sobra.
  const pdaPrevia = await s.safeFetchAllowListProofFromSeeds(umi, {
    merkleRoot,
    user: s.publicKey(minter),
    candyGuard,
    candyMachine,
  });
  const yaTenia = pdaPrevia !== null;

  // Transacción 1: el proof. Sólo si la PDA no está.
  const tbRoute = yaTenia ? null : s.transactionBuilder().add(
    s.route(umi, {
      candyMachine,
      candyGuard,
      guard: "allowList",
      group: s.some(grupo),
      routeArgs: { path: "proof", merkleRoot, merkleProof },
    }),
  );

  // Transacción 2: el mint. El de la Candy Machine come CU: sin subir el
  // límite entra en riesgo de quedarse sin unidades.
  const nftMint = s.generateSigner(umi);
  const tbMint = s.transactionBuilder()
    .add(s.setComputeUnitLimit(umi, { units: 800_000 }))
    .add(
      s.mintV2(umi, {
        candyMachine,
        candyGuard,
        nftMint,
        collectionMint: cm.collectionMint,
        collectionUpdateAuthority: cm.authority,
        group: s.some(grupo),
        mintArgs: {
          // Los montos viven en el guard on-chain: acá sólo se nombran las
          // cuentas. Que el precio no se pueda pasar por parámetro es la
          // garantía de que el navegador no puede abaratar la quema.
          tokenBurn: s.some({ mint: s.publicKey(mintToken) }),
          solPayment: s.some({ destination: s.publicKey(tesoro) }),
          allowList: s.some({ merkleRoot }),
        },
      }),
    );

  return { tbRoute, tbMint, cm, candyGuard, grupo, yaTenia, nftMint };
}
