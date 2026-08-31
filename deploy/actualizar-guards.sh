#!/bin/bash
# Reescribe el merkleRoot de los guards on-chain desde config.json.
# Correr después de cambiar la allowlist y regenerar data/merkle.json.
export PATH="$HOME/.local/share/solana/install/active_release/bin:$PATH"
source ~/.config/solana/helius.env
cd "$(dirname "$0")"
RPC="https://mainnet.helius-rpc.com/?api-key=$HELIUS_KEY"
ok=0; mal=0
for d in carta-*; do
  [ -d "$d" ] || continue
  if (cd "$d" && timeout 300 sugar guard update -k ~/.config/solana/raremagaibas.json -r "$RPC" 2>&1 | grep -q "Command successful"); then
    echo "  ok   $d"; ok=$((ok+1))
  else
    echo "  FALLO $d"; mal=$((mal+1))
  fi
done
echo "FIN  ok=$ok  fallos=$mal  saldo: $(solana balance)"
