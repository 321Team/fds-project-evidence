# P1-MON-01 — Grafana Datasource FQDN Runtime 정합화 증적 수신

- Record ID: `P1-MON-01`
- Runtime 수행 시각: 2026-09-29 17:04~17:09 KST
- 증적 수신 시각: 2026-09-29 17:44:48 KST
- 실행 호스트: `k8s-control01`
- 실행 계정: `server02`
- 수신 호스트: `ansible01`
- 수신 계정: `server01_ansible`
- 전송 계정: `svc_ansible`
- 전송 방식: Ansible `fetch`
- 원본 archive: `/home/server02/p1-mon-grafana-ds-fqdn-20260929T170935.tar.gz`
- 임시 staging: `/var/tmp/p1-mon-transfer-20260929T170935/`
- archive SHA256: `f43fa29f681b6a2c73fbb1535c6170e6eb5380bb6e5092daab226c6d505ef918`

## 범위

승인·병합된 `infra-monitoring#18`의 Grafana Prometheus Datasource URL 정합화를 Runtime에서 적용한 증적이다.

변경:
- `http://prometheus:9090`
- → `http://prometheus.monitoring-api.svc:9090`

검증:
- ConfigMap exact patch 성공
- projected ConfigMap volume 반영 확인
- Grafana provisioning datasource reload HTTP 200
- Datasource API HTTP 200 및 URL exact match
- Datasource health HTTP 200
- Pod UID 동일
- restartCount `0 → 0`
- imageID 동일
- Pod restart / image repull 없음

## 전송·무결성

control01의 사용자 홈은 `svc_ansible`에서 직접 읽을 수 없어 홈 디렉터리 권한을 완화하지 않았다. 대신 archive와 sidecar만 `/var/tmp/p1-mon-transfer-20260929T170935/`에 `root:svc_ansible`, mode `0640`으로 staging하고 Ansible `fetch(validate_checksum=yes)`로 수신했다.

수신 후 archive SHA256을 원본 sidecar와 다시 비교해 `TRANSFER_SHA256=PASS`를 확인했다. 원격 staging은 이후 Ansible `file state=absent`로 삭제했고 `stat.exists=false`를 확인했다.

`RECEIPT.txt`는 ansible01 수신 시 생성한 전송 기록이며, `RECEIPT.txt.sha256`은 해당 receipt 자체의 무결성을 고정한다.

## 판정 경계

이 회차는 Grafana Datasource FQDN Runtime drift 해소 및 그 증적 수신을 기록한다. 다음을 의미하지 않는다.

- Grafana image digest/Trivy 승인 완료
- monitor01 Remote Write / watchdog 완료
- P1-MON-01 전체 AC 완료
- 티켓 종결

따라서 P1-MON-01 전체 상태는 계속 OPEN이다.
