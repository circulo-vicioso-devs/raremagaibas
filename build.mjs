// Arma vendor-mint.js: las librerías de Metaplex en un solo archivo, para que
// la acuñación no dependa de que un CDN esté arriba ni de que una versión
// cambie sola. El archivo generado se commitea.
//
//   npm run build
//
// Regenerarlo sólo al actualizar dependencias. mint.js se edita a mano y no
// pasa por acá.
import { build } from "esbuild";

const r = await build({
  entryPoints: ["vendor/sdk.src.mjs"],
  outfile: "vendor-mint.js",
  bundle: true,
  format: "esm",
  platform: "browser",
  target: ["es2022"],
  minify: true,
  sourcemap: false,
  legalComments: "none",
  define: { "process.env.NODE_ENV": '"production"', global: "globalThis" },
  metafile: true,
});

const bytes = Object.values(r.metafile.outputs)[0].bytes;
console.log(`  vendor-mint.js  ${(bytes / 1024).toFixed(0)} KB`);
