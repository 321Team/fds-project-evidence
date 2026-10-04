#!/bin/bash
if [[ "${BASH_SOURCE[0]}" != "$0" ]]; then
  printf 'STOP: bash run.sh로 실행하세요.\n' >&2
  return 1
fi
umask 077
kit=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd -P) || exit 1
cd -- "$kit" || exit 1
sha256sum -c SHA256SUMS || exit 1
python3 -I -B "$kit/precheck.py" check-login || exit 1
env_file="$HOME/.config/ansible/p1-ans-01.env"
[[ -f "$env_file" && ! -L "$env_file" ]] || { printf 'STOP: 기존 Ansible 환경 파일을 확인하세요.\n'; exit 1; }
# Existing operational configuration is loaded in this child Bash only.
source "$env_file" > /dev/null || exit 1
export ANSIBLE_PRIVATE_KEY_FILE
exec python3 -I -B "$kit/precheck.py" run
