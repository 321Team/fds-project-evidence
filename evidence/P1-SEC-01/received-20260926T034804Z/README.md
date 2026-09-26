# P1-SEC-01 Gate 2 원본·보안 후속 수집본 (2026-09-26)

Record ID: **P1-SEC-01** ([baseline #19](https://github.com/321Team/fds-project-baseline/issues/19)). 대상 Issue: [#34](https://github.com/321Team/fds-project-evidence/issues/34). 앞 수집회차: [received-20260924T081821Z](../received-20260924T081821Z/RECEIPT_REVIEW.md)(작성자 서술 기록, 원본 미수신).

| 항목 | 값 |
|---|---|
| 원본 | `p1-sec-01-originals-20260926T033752Z.tar.gz`, 5,967 bytes |
| SHA-256 | `e41c7307f92743dde3e7c0800f993e082750574a553ed9390a0276a5a70407f1`. 같은 폴더 `.sha256` sidecar와 일치 |
| 수집 | k8s-control01, root, 2026-09-26 03:37:52–03:37:53 UTC (12:37 KST) |
| 수집 도구 | [`tools/collect-p1-sec-01-originals.sh`](https://github.com/321Team/fds-project-evidence/blob/b839a5f44bbd3f1f38c5b1071e4210fe541da39a/tools/collect-p1-sec-01-originals.sh) v1.0, SHA-256 `1a48e5e3a2a67b65d452095edae0b1dd2e5546d21d9fb64a0f78e9696a721c5e`([PR #44](https://github.com/321Team/fds-project-evidence/pull/44)). 실행 전 control01에서 `sha256sum --check` OK |
| 전달 경로 | control01 → ansible01(`scp`, `sha256sum --check` OK) → WinSCP → 작업 PC. 전송용 ZIP `0__260926.zip`(SHA-256 `f80b2b8f…cf87f7`)에서 두 파일을 꺼냈다. ZIP은 편입하지 않는다 |
| 수신 시각 | 2026-09-26T03:48:04Z |
| 수집·제공 | 이하영(P1-SEC-01 Lead). 수집기 작성·편입 정리는 Claude Code 보조 |

## 수신 검증

- sidecar 일치. 압축 내부 19개 파일, 내부 `SHA256SUMS` 전부 일치. 절대경로·`..`·링크 없음.
- 비밀정보 검색: 개인키·password/token 대입·`postgresql` URL·`ENC_KEY` 값·40자 이상 base64 문자열 0건(이미지 digest 제외). 암호화 설정의 `secret:`은 `<REDACTED>`로 수집됐다.
- 압축을 다시 하거나 내용을 고치지 않았다. 폴더 `SHA256SUMS`는 이 README·원본·sidecar를 고정한다.

## Issue #34 1번 — 원본 대응

| 요청 | 결과 | 한계 |
|---|---|---|
| Gate 2 원본 로그 6개 | `/root/gate2-final-evidence/logs/` 6개 모두 존재. 9/22 문서의 SHA-256과 **6/6 일치**(`01-gate2-logs-verify.txt`, check_exit_code 0). mtime 2026-09-22 10:02–10:12 KST | `06-history-cleanup-confirmed.txt`는 명령 출력이 아니라 작성자 진술 2줄이다 |
| etcd raw 조회 | 전체 Secret 6개 모두 `k8s:enc:secretbox:v1:key1:` 접두어(`11-etcd-secret-prefix.txt`). CP 3대 kube-apiserver 모두 `--encryption-provider-config` 반영(`10`) | **2026-09-26 재조회**다. 9/22 당시 `enc-test-secret` 조회 출력은 원본 로그 6개에 없고, 이번에도 수신되지 않았다 |
| GNP·HEP | `nodeport-30080-allow` generation 1, 생성 2026-09-22T02:11:55Z, spec이 9/22 문서와 같다. worker HEP 3개 `fds.example/role=worker`(`20`~`22`) | 수집 시점 상태. 적용 당시 `-o yaml` 출력은 아니다 |
| transaction-api·fds-engine 배포 | 두 Deployment 모두 2/2, Harbor digest 고정 이미지(`30`·`31`) | 수집 시점 상태 |

## Issue #34 2번 — 보안 후속에 쓸 수 있는 관측 (판단 아님)

- **etcd 키**: 키 이름은 여전히 `key1`, `encryption-config.yaml` mtime 2026-09-22 09:33 KST다. **9/22 이후 키 교체는 없었다.** control01 `/root`·`/home/server02` history에 현재 키 값과 같은 문자열·`ENC_KEY=` 줄은 0건이다(`40`). control02·03은 이번에 조회하지 않았고 9/22 진술(`06`)만 있다. 세션 대화 기록의 노출은 history 정리로 해소되지 않는다.
- **DB Secret**: `transaction-api-db-credentials`는 2026-09-22T03:51:21Z 생성, resourceVersion `1098502`다(`32`). 같은 날 03:28Z에 생성된 `harbor-pull-secret`이 `1094787`이므로, 이 값은 생성 직후 시기의 것으로 보인다. 그렇다면 **Secret은 9/22 생성 이후 바뀌지 않았다.** 9/25 `kubectl patch` 결과 `patched (no change)`([P1-DB-01 기록](https://github.com/321Team/fds-project-evidence/issues/34#issuecomment-5832659134))와도 맞는다. 이 Secret은 비밀번호가 노출된 그 작업에서 만들어졌다. 따라서 **현재 DB 비밀번호가 9/22 노출값과 같을 가능성이 높다.** resourceVersion 비교에 의한 추정이며 값 대조는 하지 않았다.
- **GNP**: 저장소 밖 GNP가 9/22 적용 그대로 유지되고 있다(generation 1).
- **Harbor Robot TTL**: 이번 수집 범위 밖이다.

이 편입은 원본 보존이다. P1-SEC-01·P1-K8S-01·ICR의 AC 체크, Gate, 티켓 상태는 바꾸지 않는다.
