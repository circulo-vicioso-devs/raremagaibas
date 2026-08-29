#!/bin/bash
# Despliega las máquinas que falten, mientras haya SOL. Corta con margen.
export PATH="$HOME/.local/share/solana/install/active_release/bin:$PATH"
cd "$(dirname "$0")"
MIN=0.045
for d in carta-*; do
  yad=$(python3 -c "import json;print(json.load(open('$d/cache.json'))['program'].get('candyMachine') or '')")
  [ -n "$yad" ] && continue
  b=$(solana balance | cut -d' ' -f1)
  if python3 -c "import sys; sys.exit(0 if $b < $MIN else 1)"; then
    echo "SIN SALDO ($b) — corto en $d"; break
  fi
  echo "=== $d  (saldo $b) ==="
  (cd $d && timeout 400 sugar deploy 2>&1 | grep -E "Candy machine ID|🛑" | head -2)
  (cd $d && timeout 400 sugar guard add 2>&1 | grep -E "Candy guard ID|🛑" | head -2)
done
echo "FIN  saldo: $(solana balance)"
