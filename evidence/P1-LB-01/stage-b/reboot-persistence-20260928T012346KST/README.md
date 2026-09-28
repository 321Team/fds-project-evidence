# P1-LB-01 REBOOT_PERSISTENCE — 2026-09-28 KST

책임 티켓: `321Team/fds-project-baseline#9`  
Evidence PR: `321Team/fds-project-evidence#60`

## 판정

`REBOOT_PERSISTENCE=PASS`.

승인된 범위에서 `k8s-api-lb01` 정상 reboot 1회 후 LB 상태와 LB 경유 Kubernetes API를 read-only로 재검증했다.

### LB-side
- boot id: `7bc515b7-9f95-48b6-82b8-81d46fee14ce` → `60e3c690-729a-49ae-92d3-c18a63c95f2c`
- boot start: `2026-09-28 01:23:46 KST`
- helper/sudoers absent
- SELinux `Enforcing`
- firewalld/haproxy `active + enabled`
- `.109:6443` LISTEN
- `p1lb_*` 없음
- control01/02/03 모두 `UP/L4OK`

### API-side
경로: `ansible01 -> k8s-control01(10.1.93.102) -> 10.1.93.109:6443`.
- collector: `API_PRECHECK_READY`
- identity: `kubernetes-admin`
- Node 6/6 Ready
- `/readyz=ok`
- route source `.102 / ens160`
- configuration change/fault injection 없음
- collector/helper Git blob이 reviewed source `infra-lb@2a7ff5b457e49cf6cfdfbcf3374224f120e735d3`와 일치

## 원본 무결성

- LB archive: `cf06c2799a540b818da19bf60c8f8f1041e01e0d01e3a597846aa7ae9296d611`, 1708 bytes, internal 16/16 MATCH
- API archive: `eb30f27c6355fd86dffe4402cc146f710053ce4eebd686d2779b5c8321354028`, 16986 bytes, internal 20/20 MATCH
- 두 archive 모두 unsafe path/link/special 없음, 기본 민감정보 marker scan hit 없음

`JOURNAL_BOOTS.txt`는 현재 boot 1개만 포함하므로 이전 boot는 pre-reboot receipt와 연결한다.

이 collection은 independent review, final acceptance, LB-A-01/P1-K8S handoff 또는 ticket closure를 자동 승인하지 않는다.
