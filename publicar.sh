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
python3 "$AQUI/generadores/cartas-idiomas.py"

MSG="${1:-Actualiza RareMagaibas}"

# Commitea si hay algo nuevo y pushea SIEMPRE que haya algo sin subir.
#
# Antes el push colgaba del commit: si el commit ya estaba hecho y el push había
# fallado (por ejemplo, por credenciales), la corrida siguiente decía "sin
# cambios" y se iba sin subir nada. Eso dejó el sitio sirviendo una allowlist
# vieja cuyo merkle root ya no coincidía con el guard on-chain: nadie podía
# acuñar. El estado que importa es el del remoto, no el del índice.
publicar() {
  local repo="$1" rama="$2" etiqueta="$3"
  git -C "$repo" add -A
  if git -C "$repo" diff --cached --quiet; then
    echo "    sin cambios para commitear"
  else
    git -C "$repo" -c user.name="RareMagaibas" -c user.email="realjuanruocco@421.news" \
      commit -q -m "$MSG"
    echo "    commit hecho"
  fi
  git -C "$repo" fetch -q origin "$rama" || true
  if [ -z "$(git -C "$repo" log --oneline "origin/$rama..HEAD")" ]; then
    echo "    el remoto ya está al día"
    return
  fi
  git -C "$repo" push -q origin "HEAD:$rama"
  echo "    pusheado$etiqueta"
}

echo "==> Repo del sitio"
publicar "$AQUI" main ""

echo "==> Repo de deploy (dispara el build de Netlify)"
publicar "$LANDING" main " — Netlify rebuildea en ~1 min"

echo
echo "https://magaiba.xyz/raremagaiba/"
