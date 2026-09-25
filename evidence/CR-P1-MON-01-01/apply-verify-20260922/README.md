# CR-P1-MON-01-01 Squid Apply/Verify 실행 증적 — 2026-09-22

2026-09-22 `ansible01`(`server01_ansible`)에서 실제 대상 `egress-proxy01`(`10.1.93.56`)에 대해 실행한 CR-P1-MON-01-01(Alertmanager Egress 프록시) apply/verify 결과.

- [precheck 로그](20260922T193722+0900_4770_precheck.txt)
- [apply 드라이런(apply_check_diff) 로그](20260922T194200+0900_5016_apply_check_diff.txt)
- [apply 실제 적용 로그](20260922T194200+0900_5016_apply.txt)
- [apply 재실행(idempotency 검증) 로그](20260922T194200+0900_5016_apply_idempotency.txt)
- [독립 verify 로그](20260922T194417+0900_5914_verify.txt)
- [증적 무결성 검사 로그](20260922T194429+0900_6104_integrity_check.txt)
- [원본 EVIDENCE_INDEX.md](EVIDENCE_INDEX.md)
- [원본 SHA256SUMS](SHA256SUMS)

infra-ansible `claude/sharp-rubin-2qrz67`, commit [`da7f2cc`](https://github.com/321Team/infra-ansible/commit/da7f2ccd52ee407e61376d11375a1361f076f112) 기준 실행. `cr_mon_proxy_allowed_clients`는 [fds-project-baseline#74](https://github.com/321Team/fds-project-baseline/issues/74)의 Pod 배치·taint 확인과 담당자 동의에 따라 Worker 3대(`10.1.93.105`/`.107`/`.108`)의 후보 주소로 확정했다. 이를 proxy가 관측한 post-SNAT 주소 3개 전체의 실측으로 확대하지 않는다(2026-09-23 표현 정정).

## 결과 요약 (모두 `rc=0`; 작업 트리 상태는 단계별 구분)

| 단계 | tree | changed | 결과 |
|---|---|---|---|
| precheck | dirty | 0 | PASS — 실행 결과이며 clean 소스 검증은 아님 |
| apply_check_diff (`--check --diff` 드라이런) | clean | 0 | PASS |
| apply (실제 적용) | clean | 8 | PASS |
| apply_idempotency (즉시 재실행) | clean | 0 | PASS — 러너 자체의 idempotency 자동 검증 통과 |
| verify (독립 실행) | clean | 0 | PASS |

### 2026-09-23 KST 정정 — precheck 작업 트리 상태

기존 요약의 “모두 `tree=clean`”은 원본 로그와 다른 표기여서 위와 같이 정정한다.

- [precheck 원본](20260922T193722+0900_4770_precheck.txt)의 시작 기록은 `2026-09-22T19:37:22+09:00`, `commit=da7f2ccd52ee407e61376d11375a1361f076f112`, **`tree=dirty`**다. 종료 `rc=0`과 `changed=0`은 유지한다. 당시 미커밋 변경의 내용은 이 로그에 없으므로, precheck가 해당 commit의 변경 없는 소스만 실행했다는 증거로 사용하지 않는다.
- 이후 `apply_check_diff`, `apply`, `apply_idempotency`, `verify` 원본은 같은 commit과 **`tree=clean`**을 기록한다. 이 단계들의 기존 실행 결과는 유지하며, 앞선 precheck까지 소급해 clean으로 판정하지 않는다.
- 이번 정정은 저장소 설명 문서에 한정한다. 원본 로그 6개, `EVIDENCE_INDEX.md`, 수신 원본의 `SHA256SUMS` 및 과거 승인 이력은 변경하지 않는다. 서버 재실행이나 서비스 인수·AC 판정 변경을 수행한 기록이 아니다.

verify 노드 검증치(`Print CR-P1-MON-01-01 node verdict`):

```json
{
  "squid_active_state": "active",
  "squid_load_state": "loaded",
  "allowed_domain_probe_status": "200",
  "denied_domain_probe": "DENIED_AT_CONNECT",
  "kubelet_regression": "NONE"
}
```

## 범위 한정

- 위 allowed/denied 프로브는 `egress-proxy01` 자체에서 실행한 curl 테스트다. 실제 Alertmanager Pod(워커 노드)에서 프록시를 경유한 end-to-end 요청 검증은 이 증적에 포함되지 않는다.
- Rollback 경로는 이번에 실행하지 않았다(정상 완주 시나리오이므로 불필요).
- 이 증적은 인프라 측 apply/verify PASS를 기록한 것이며, 서비스 인수·운영 endpoint 인계 수락과는 별개다.

관련: [fds-project-baseline#74](https://github.com/321Team/fds-project-baseline/issues/74) (실행 결과 보고 [코멘트](https://github.com/321Team/fds-project-baseline/issues/74#issuecomment-5775166527)), [#75](https://github.com/321Team/fds-project-baseline/issues/75) (endpoint 인계 [코멘트](https://github.com/321Team/fds-project-baseline/issues/75#issuecomment-5775168220)).

이 디렉터리에서 `sha256sum --check SHA256SUMS`로 등록 파일을 검사할 수 있다(로컬 사본 및 `fds-project-evidence` 사본 모두 재검증 완료).
