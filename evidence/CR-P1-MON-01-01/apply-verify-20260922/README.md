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

infra-ansible `claude/sharp-rubin-2qrz67`, commit [`da7f2cc`](https://github.com/321Team/infra-ansible/commit/da7f2ccd52ee407e61376d11375a1361f076f112) 기준 실행. `cr_mon_proxy_allowed_clients`를 [fds-project-baseline#74](https://github.com/321Team/fds-project-baseline/issues/74)에서 실측한 Worker 3대(`10.1.93.105`/`.107`/`.108`)로 확정한 뒤 실행했다.

## 결과 요약 (모두 `rc=0`, `tree=clean`)

| 단계 | changed | 결과 |
|---|---|---|
| precheck | 0 | PASS |
| apply_check_diff (`--check --diff` 드라이런) | 0 | PASS |
| apply (실제 적용) | 8 | PASS |
| apply_idempotency (즉시 재실행) | 0 | PASS — 러너 자체의 idempotency 자동 검증 통과 |
| verify (독립 실행) | 0 | PASS |

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
