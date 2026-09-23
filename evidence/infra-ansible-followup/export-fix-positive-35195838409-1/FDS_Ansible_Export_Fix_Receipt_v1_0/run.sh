#!/usr/bin/env bash
set -euo pipefail
umask 077
cd -- "$(dirname -- "${BASH_SOURCE[0]}")"
if [[ "$#" != 1 || "$1" != admin ]]; then
  printf '%s\n' 'Usage: bash run.sh admin' >&2
  exit 2
fi
sha256sum -c SHA256SUMS
exec python3 -I -B collect.py
