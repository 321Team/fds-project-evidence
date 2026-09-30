# P1-LB-01 Stage B FIELD_ROLLBACK post-check — 2026-09-28 KST

책임 티켓: `321Team/fds-project-baseline#9`  
Evidence PR: `321Team/fds-project-evidence#60`

## 목적

Stage B Runtime #2 후 임시 최소권한 구성의 FIELD_ROLLBACK 결과를 서버 원본 archive로 보존한다.

회수 대상:
- `/etc/sudoers.d/p1-lb-stageb`
- `/usr/local/sbin/p1-lb-stageb-privileged`

## 실행 및 수집 시각

- rollback start: `2026-09-28T00:46:55+09:00`
- rollback complete: `2026-09-28T00:46:56+09:00`
- post-check metadata: `2026-09-28T00:50:18+09:00`
- host: `k8s-api-lb01`
- user: `server01_k8s-api-lb`

## 확인 결과

- temporary sudoers: absent (`rc=0`)
- temporary helper: absent (`rc=0`)
- `visudo -c`: PASS (`rc=0`)
- SELinux: `Enforcing`
- firewalld: `active`
- HAProxy: `active`
- HAProxy MainPID: `1267` (rollback precheck와 동일)
- listener `10.1.93.109:6443`: LISTEN (`rc=0`)
- nft tables: `inet firewalld`만 수집되어 Stage B `p1lb_*` table 부재
- backend `k8s-control01/02/03`: 모두 `UP/L4OK`

판정: `FIELD_ROLLBACK=PASS`.

## 수집 보정 이력

초기 post-check 수집 시 터미널의 `set -u`/프롬프트 변수 및 멀티라인 paste가 깨져 부분 수집이 발생했다. 시스템 설정을 다시 변경하지 않고 기존 수집 디렉터리를 확인했으며, 누락된 `BACKENDS.rc`를 read-only `show stat` 재조회 결과로 보완하고 `BACKENDS.txt`를 함께 재생성한 뒤 `SHA256SUMS`와 archive를 다시 생성했다.

따라서 이 archive는 최초 깨진 임시 archive가 아니라 **보정 완료 후 재패키징된 최종 바이트**다. rollback 자체의 수행 시각은 `RECEIPT_LINKAGE.txt`에 별도 연결한다.

## 무결성

- original archive size: `1454` bytes
- original archive SHA-256: `92ab525c60455fb169ff05aa09912c686ab49c4b5d12572ccddb8ad14da77e0f`
- sidecar: archive SHA와 일치
- archive regular files: `15`
- internal `SHA256SUMS`: `14/14 MATCH`
- tar path traversal / symlink / hardlink: 없음
- 기본 private-key/Bearer/client-key-data/password-assignment marker scan: hit 없음

## 범위 한계

이 collection은 FIELD_ROLLBACK과 직후 상태만 증명한다. 다음을 의미하지 않는다.
- reboot persistence PASS
- P1-LB-01 final acceptance
- LB-A-01/P1-K8S handoff 완료
- ticket closure

다음 Gate는 별도 승인된 `REBOOT_PERSISTENCE`다.
