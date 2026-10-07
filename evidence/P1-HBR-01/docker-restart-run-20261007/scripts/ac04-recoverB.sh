#!/bin/bash
T5=$(date -d "23:17:21" +%s)
while [ "$(date +%s)" -lt "$T5" ]; do sleep 1; done
echo "== B start gate $(date '+%F %T')"
docker ps -a --format '{{.Names}} {{.Status}}'
getent ahosts localhost
timeout 3 bash -c 'exec 3<>/dev/tcp/localhost/1514; exec 3>&-; exec 3<&-'; rc=$?; echo "tcp_1514_rc=$rc"
[ "$rc" -eq 0 ] || { echo "ABORT: localhost:1514 not reachable"; exit 3; }
[ "$(docker inspect -f '{{.State.Status}}' harbor-log)" = "running" ] || { echo "ABORT: harbor-log not running"; exit 3; }
systemctl is-active fds-harbor-ac04-guard docker
for n in harbor-db redis registry registryctl harbor-core harbor-portal harbor-jobservice trivy-adapter nginx; do
  s=$(date '+%T'); timeout 60 docker start "$n" >/dev/null 2>/tmp/ac04b-$n.err; rc=$?
  ok=0; for i in $(seq 1 60); do h=$(docker inspect -f '{{if .State.Health}}{{.State.Health.Status}}{{else}}{{.State.Status}}{{end}}' "$n" 2>/dev/null); if [ "$h" = "healthy" ] || [ "$h" = "running" ]; then ok=1; break; fi; sleep 1; done
  echo "start $n rc=$rc start=$s end=$(date '+%T') state=$h ok=$ok err=$(head -c 200 /tmp/ac04b-$n.err | tr '\n' ' ')"
  [ "$ok" -eq 1 ] || { echo "STOP: $n not ready within 60s"; exit 4; }
done
echo "== B done $(date '+%F %T')"; docker ps -a --format '{{.Names}} {{.Status}}'
