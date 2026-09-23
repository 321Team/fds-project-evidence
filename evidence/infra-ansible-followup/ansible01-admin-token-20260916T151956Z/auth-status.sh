#!/usr/bin/env bash
# Read-only authentication metadata. Do not issue Runner tokens or print credentials.
(
set +x
set +e
set -u -o pipefail
umask 077
TASK_AUTH_EVIDENCE=$(mktemp "$HOME/ansible-gh-auth.XXXXXXXX.txt") || exit 1
{
  date -u '+OBSERVED_AT=%Y-%m-%dT%H:%M:%SZ'
  [[ -n "${GH_TOKEN:-}" ]] && echo GH_TOKEN_SET=yes || echo GH_TOKEN_SET=no
  [[ -n "${GITHUB_TOKEN:-}" ]] && echo GITHUB_TOKEN_SET=yes || echo GITHUB_TOKEN_SET=no
  env -u GH_DEBUG -u GH_FORCE_TTY LC_ALL=C gh auth status --active --hostname github.com 2>&1 |
    awk '/Token:/ {
      kind="unknown"
      if ($0 ~ /github_pat_/) kind="fine-grained PAT"
      else if ($0 ~ /ghp_/) kind="classic PAT"
      else if ($0 ~ /gho_/) kind="OAuth"
      else if ($0 ~ /ghs_/) kind="GitHub App installation"
      else if ($0 ~ /ghu_/) kind="GitHub App user"
      print "  - Token kind: " kind
      next
    } {print}'
  TASK_AUTH_PIPE=("${PIPESTATUS[@]}")
  printf 'AUTH_STATUS_RC=%s\nFILTER_RC=%s\n' "${TASK_AUTH_PIPE[0]}" "${TASK_AUTH_PIPE[1]}"
} > "$TASK_AUTH_EVIDENCE"
cat -- "$TASK_AUTH_EVIDENCE"
(cd "$HOME" && sha256sum -- "${TASK_AUTH_EVIDENCE##*/}") > "$TASK_AUTH_EVIDENCE.sha256"
printf 'HOME_EVIDENCE=%s\n' "$TASK_AUTH_EVIDENCE"
if (( TASK_AUTH_PIPE[1] != 0 )); then exit "${TASK_AUTH_PIPE[1]}"; fi
exit "${TASK_AUTH_PIPE[0]}"
)
