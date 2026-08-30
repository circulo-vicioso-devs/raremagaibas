// Las librerías de Solana usan el Buffer global de Node en 21 lugares, y
// esbuild no rellena los globales: en el navegador eso tira
// "ReferenceError: Buffer is not defined" apenas se arma una transacción.
//
// El paquete `buffer` ya viaja adentro del bundle, así que sólo hay que
// colgarlo del global. Va importado PRIMERO en sdk.src.mjs para que corra
// antes que cualquier otra cosa.
import { Buffer } from "buffer";

if (typeof globalThis.Buffer === "undefined") globalThis.Buffer = Buffer;
if (typeof globalThis.process === "undefined") globalThis.process = { env: {} };
