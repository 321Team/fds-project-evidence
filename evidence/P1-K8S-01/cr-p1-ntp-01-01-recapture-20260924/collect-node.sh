#!/usr/bin/env bash
# CR-P1-NTP-01-01 PR44 재기준용 읽기 전용 수집 (노드별 1회, root 또는 sudo로 실행)
# - 서버 상태를 바꾸는 명령 없음: 조회(save/list/show/--state/--get-*)만 실행
# - NTP 패킷 시험 없음, conntrack 조작 없음, firewalld 시작/중지 없음
# - 명령 인수는 tools/ntp-post-egress-remote.py KERNEL_COMMANDS 및
#   9/21 fixture(current_kernel_20260921_1614.json) 명령 키와 동일하게 맞춤
# 사용(ansible01): ansible k8s_nodes -b -m ansible.builtin.script -a "collect-node.sh <수집자>"
#   → 각 노드 /root/ntp-recapture-<host>-<UTC>.tar.gz
set -u
umask 077
export LC_ALL=C
COLLECTOR=${1:-${COLLECTOR:-UNSET}}
HOST=$(hostname -s)
TS=$(date -u +%Y%m%dT%H%M%SZ)
OUT=/root/ntp-recapture-${HOST}-${TS}
mkdir -m 700 "$OUT" || exit 1
cd "$OUT" || exit 1

run() {  # run <key> <cmd...> : stdout/stderr/rc/시각을 원문 그대로 보존
  local key=$1; shift
  date -u +%Y-%m-%dT%H:%M:%S.%6NZ > "$key.started"
  "$@" > "$key.stdout" 2> "$key.stderr"
  echo $? > "$key.rc"
  date -u +%Y-%m-%dT%H:%M:%S.%6NZ > "$key.ended"
  printf '%q ' "$@" > "$key.argv"
}

{
  echo "collector=$COLLECTOR"
  echo "host=$HOST"
  echo "started_utc=$(date -u +%Y-%m-%dT%H:%M:%S.%6NZ)"
  echo "started_local=$(date +%Y-%m-%dT%H:%M:%S.%6N%:z)"
  echo "boot_id=$(cat /proc/sys/kernel/random/boot_id)"
  echo "uptime=$(cat /proc/uptime)"
  echo "read_only=true"
  echo "ntp_probe=false"
} > meta.txt

# 1) 계약 4종 원문 (BASELINE 재계산 입력) — 절대경로·인수 고정
run iptables-save   /usr/sbin/iptables-save
run ip6tables-save  /usr/sbin/ip6tables-save
run nft-ruleset     /usr/sbin/nft list ruleset
# A안 검증기 입력 형식(카운터 포함): 커널 fixture 교체용
run iptables-save-c /usr/sbin/iptables-save -c
run ipset-save      /usr/sbin/ipset save

# 2) firewalld 상태 (9/22 문서의 disabled/inactive 여부 확인)
run fw-is-active    /usr/bin/systemctl is-active firewalld
run fw-is-enabled   /usr/bin/systemctl is-enabled firewalld
run fw-status       /usr/bin/systemctl status firewalld --no-pager -l
run fw-state        /usr/bin/firewall-cmd --state
for p in "" "--permanent"; do
  tag=${p:+-perm}
  run "fw-direct-rules$tag"   /usr/bin/firewall-cmd $p --direct --get-all-rules
  run "fw-direct-chains$tag"  /usr/bin/firewall-cmd $p --direct --get-all-chains
done
run fw-journal      /usr/bin/journalctl -u firewalld --since 2026-09-21 --no-pager -o short-iso-precise
run ntp-chain-v4    /usr/sbin/iptables  -w 5 -n -v -x -L FDS_NTP_0101 --line-numbers
run ntp-chain-v6    /usr/sbin/ip6tables -w 5 -n -v -x -L FDS_NTP_0101 --line-numbers

# 3) 보존 대상 파일 메타·해시 (내용 변경 여부 대조용)
for f in /etc/chrony.conf /etc/chrony.d/50-cr-p1-ntp-01-01.conf /etc/sysconfig/chronyd \
         /etc/firewalld/firewalld.conf /etc/firewalld/zones/public.xml /etc/firewalld/direct.xml \
         /var/lib/fds-change/CR-P1-NTP-01-01/original-ntp-pair.json \
         /var/lib/fds-change/CR-P1-NTP-01-01/original-ntp-dropin.json; do
  if [ -e "$f" ]; then stat -c '%n %U:%G %a %s %y' "$f"; sha256sum "$f"; else echo "$f ABSENT"; fi
done > preserved-files.txt 2>&1

# 4) 경로·동기화 상태 (9/21 fixture 명령 키와 동일)
run identity-ip     /usr/sbin/ip -j addr show
run ipv4-rule       /usr/sbin/ip -j -4 rule show
run ipv6-address    /usr/sbin/ip -j -6 addr show
run ipv6-route      /usr/sbin/ip -j -6 route show
run ipv6-rule       /usr/sbin/ip -j -6 rule show
for d in 192.0.2.123 162.159.200.1 162.159.200.123 10.1.93.102; do
  run "ipv4-route-$d" /usr/sbin/ip -j -4 route get "$d"
done
run chrony-tracking /usr/bin/chronyc -n tracking
run chrony-sources  /usr/bin/chronyc -n sources -a
run chronyd-active  /usr/bin/systemctl is-active chronyd

echo "ended_utc=$(date -u +%Y-%m-%dT%H:%M:%S.%6NZ)" >> meta.txt
find . -type f ! -name SHA256SUMS -print0 | sort -z | xargs -0 sha256sum > SHA256SUMS
cd .. && tar -czf "$OUT.tar.gz" "$(basename "$OUT")" && chmod 600 "$OUT.tar.gz" && sha256sum "$OUT.tar.gz"
