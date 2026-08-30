#!/usr/bin/env bash
# Publica RareMagaibas en https://magaiba.xyz/raremagaiba/
#
# El sitio se escribe acá (repo público circulo-vicioso-devs/raremagaibas).
# El deploy sale de ../landing (repo privado circulo-vicioso-devs/magaiba-web),
# que es el que Netlify tiene linkeado al dominio. Este script copia uno en el
# otro y pushea los dos, para que no deriven.
#
# deploy/ queda afuera a propósito: son 1.278 archivos de configuración de
# Sugar, ~31 MB, y no son parte del sitio. Tampoco van las herramientas:
# build.mjs, simular.mjs, probe.mjs, package.json ni node_modules.
#
# vendor-mint.js es generado: si tocaste las dependencias, corré antes
#   npm run build
set -euo pipefail

AQUI="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LANDING="$(dirname "$AQUI")/landing"
DESTINO="$LANDING/raremagaiba"

[ -d "$LANDING/.git" ] || {
  echo "Falta el clon de la landing en $LANDING" >&2
  echo "  gh repo clone circulo-vicioso-devs/magaiba-web $LANDING" >&2
  exit 1
}

echo "==> Copiando los recursos a $DESTINO"
mkdir -p "$DESTINO"
# index.html NO va acá: la página se genera por idioma más abajo. Y README.md
# tampoco: es documentación de desarrollo, no tiene por qué servirse al público.
rsync -a --delete \
  "$AQUI/mint.js" "$AQUI/config.js" "$AQUI/acunacion.js" \
  "$AQUI/vendor-mint.js" "$AQUI/allowlist.json" "$AQUI/img" \
  "$DESTINO/"

echo "==> Generando /es/raremagaiba/ y /en/raremagaiba/"
python3 "$(dirname "$AQUI")/cartas-idiomas.py"

MSG="${1:-Actualiza RareMagaibas}"

echo "==> Repo del sitio"
git -C "$AQUI" add -A
if git -C "$AQUI" diff --cached --quiet; then
  echo "    sin cambios"
else
  git -C "$AQUI" -c user.name="RareMagaibas" -c user.email="realjuanruocco@421.news" \
    commit -q -m "$MSG"
  git -C "$AQUI" push -q origin HEAD
  echo "    pusheado"
fi

echo "==> Repo de deploy (dispara el build de Netlify)"
git -C "$LANDING" add -A
if git -C "$LANDING" diff --cached --quiet; then
  echo "    sin cambios"
else
  git -C "$LANDING" -c user.name="RareMagaibas" -c user.email="realjuanruocco@421.news" \
    commit -q -m "$MSG"
  git -C "$LANDING" push -q origin main
  echo "    pusheado — Netlify rebuildea en ~1 min"
fi

echo
echo "https://magaiba.xyz/raremagaiba/"
