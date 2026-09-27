# P1-K8S-01 / infra-kubernetes PR #39 (9100/10250 GNP 수정) 검증 증적 — 2026-09-27

[fds-project-baseline#10](https://github.com/321Team/fds-project-baseline/issues/10) HEP/GNP AC 항목 중 "9100/10250 실패 조치" 관련, [infra-kubernetes PR #39](https://github.com/321Team/infra-kubernetes/pull/39) 병합본을 Worker 3대(k8s-worker01/02/03)에 실제 적용한 뒤 수행한 집행·차단·회귀·reboot 지속성 검증 결과.

## 출처와 수신

| 항목 | 값 |
|---|---|
| 원본 위치 | `k8s-control01`(`10.1.93.102`), 실행자 이하영(K8S/SEC Lead) |
| 수집 형태 | 사용자 제출 ZIP `icr39-evidence-20260927.zip`, SHA-256 `2eadb7c66315f34b5185e0d90215f10ff4de6c460784fc55240369a3a823cd56` |
| 전달 경로 | control01 → 사용자 로컬 → Claude Code 세션 업로드 |
| 수신 | 2026-09-27 KST |
| 편입 작성 | Claude Code 세션 (AI 보조) — 아래 "검토 상태" 참고 |

## 무결성

편입 ZIP 내부의 `SHA256SUMS`(제출자가 control01에서 생성) 기준 15개 파일 전체 `sha256sum -c` **OK** 확인. 이 폴더의 `SHA256SUMS`는 편입 시점에 동일 내용으로 재생성했다. 비밀번호·토큰 값·개인키·dockerconfigjson 패턴 검사 결과, `imagePullSecrets`/`automountServiceAccountToken` 등 필드·리소스 참조만 확인되고 실제 credential 값은 없음.

```bash
sha256sum --check SHA256SUMS
```

## 파일

| 파일 | 내용 | 확인한 사실 |
|---|---|---|
| `icr39-final-matrix.txt` | probe Pod 간 9100/10250 TCP 연결 매트릭스 (2026-09-27 12:18 KST) | CP(`probe-cp01`)→9100 3대 전부 TIMEOUT(차단, 정상), CP→10250 3대 전부 OK(기존 허용 유지), Worker 간(`probe-w01/02/03`) 9100·10250 전부 OK |
| `k8s-worker0{1,2,3}.gnp.yaml` | 적용된 GlobalNetworkPolicy 전체 spec | 9100/10250 ingress가 "다른 Worker 2대"만 source로 허용 — PR #39 설계와 일치 |
| `probes-ifnp.yaml` | 검증용 probe 리소스 정의 | Namespace/Pod/Service, `imagePullSecrets: harbor-pull-secret` 참조(값 아님) |
| `reboot-w0{1,2,3}-{before,after}.txt` | Worker 3대 각각 reboot 전/후 probe 매트릭스 | 노드별 before/after 내용 바이트 동일. 파일 mtime은 실제 재부팅 소요(약 5분~1시간16분) 만큼 차이 — 별도 캡처 확인됨(re-run이 아닌 동일 파일 복사가 아님) |
| `targets.json` / `targets-after-reboot.json` / `targets-after-w03.json` | Prometheus active targets 스냅샷 3회 | 3개 파일 모두 target 20/20 |
| `icr39-regression-20260927-1216.json` | `regression.py` 실행 로그(kubectl 명령별 argv/rc/stdout/stderr) | 기록된 명령 전부 rc=0 |

## 검토 상태

이 편입은 **AI 세션의 자체 대조**(zip 해시, 내부 SHA256SUMS, target 개수, 민감정보 패턴, matrix 내용)이며, `governance/EVIDENCE_POLICY.md`가 요구하는 **독립 검토(작성자·실행자 본인 또는 AI 보조 점검이 아닌 별도 리뷰어)** 는 아직 없다. 병합 전 최소 1인의 독립 검토와 이권욱 확인이 필요하다.

## 참고

- 관련 코멘트: [issue #10 #issuecomment-5852855859](https://github.com/321Team/fds-project-baseline/issues/10#issuecomment-5852855859), [#issuecomment-5852872058](https://github.com/321Team/fds-project-baseline/issues/10#issuecomment-5852872058)
- 복구(T19 `rollback-node`)와 CP 3대 reboot은 K8S Lead 판단으로 이번 편입 범위에서 제외, 별도 작업창으로 후속 처리한다. 이 폴더의 증적은 그 범위만 다룬다.
- 이 결과는 실행 기록 편입이며, AC 인수·티켓 종결 판정은 K8S Lead가 별도로 한다(EVIDENCE_POLICY "단계 구분" 참고).
