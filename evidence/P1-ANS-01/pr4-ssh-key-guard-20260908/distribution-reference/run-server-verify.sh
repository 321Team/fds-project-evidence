#!/usr/bin/env bash
set -euo pipefail
umask 077
kit_root="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
cd "$kit_root"
sha256sum --check SHA256SUMS
if [[ "$(hostnamectl --static)" != ansible01 || "$(id -un)" != server01_ansible ]]; then
  printf '%s\n' 'Run as server01_ansible on ansible01; do not use sudo for this wrapper.' >&2
  exit 1
fi
python3 - <<'PY'
import sys
if not (3, 12) <= sys.version_info[:2] <= (3, 14):
    raise SystemExit('Python 3.12–3.14 is required.')
PY
run_root="$(mktemp -d "$HOME/FDS_SSH_Main_Verification.XXXXXXXX")"
mkdir -p "$run_root/results" "$run_root/tmp"
export TMPDIR="$run_root/tmp"
export PYTHONDONTWRITEBYTECODE=1
export PIP_NO_INPUT=1
unset PYTHONPATH PR3_REVIEW_MOCK PR3_REVIEW_CASE PR3_REVIEW_TRACE
package_results() {
  rc=$?
  trap - EXIT
  printf '%s\n' "$rc" > "$run_root/results/wrapper_exit_code.txt"
  cp "$kit_root/SOURCE_MANIFEST.json" "$run_root/results/SOURCE_MANIFEST.json"
  cp "$kit_root/SHA256SUMS" "$run_root/results/INPUT_SHA256SUMS"
  tar -czf "$run_root/FDS_SSH_Main_Verification_Result.tar.gz" -C "$run_root" results
  (cd "$run_root" && sha256sum FDS_SSH_Main_Verification_Result.tar.gz > FDS_SSH_Main_Verification_Result.tar.gz.sha256)
  printf 'REVIEW_EXPORT_READY\nARCHIVE=%s\nSIDECAR=%s\n' "$run_root/FDS_SSH_Main_Verification_Result.tar.gz" "$run_root/FDS_SSH_Main_Verification_Result.tar.gz.sha256"
  exit "$rc"
}
trap package_results EXIT
python3 -m venv "$run_root/venv221"
"$run_root/venv221/bin/python" -m pip install --disable-pip-version-check -r "$kit_root/requirements-2213.txt" 2>&1 | tee "$run_root/results/install221.txt"
"$run_root/venv221/bin/python" -m pip freeze > "$run_root/results/packages221.txt"
python3 "$kit_root/repo/scripts/verify-ssh-main.py" --python221 "$run_root/venv221/bin/python" --output "$run_root/results" 2>&1 | tee "$run_root/results/console.txt"
