# P1-SEC-01 — Gate 2 Runtime 실행 기록 수신 검토 (2026-09-24)

판정: **작성자 실행 기록(서술)의 참고 사본으로 편입. 원본 로그는 미수신이다.** [baseline #10](https://github.com/321Team/fds-project-baseline/issues/10)(P1-K8S-01)과 [#14](https://github.com/321Team/fds-project-baseline/issues/14)(ICR-D-NET-01-01)의 AC가 이 문서를 근거로 인용하지만, 문서는 infra-kubernetes의 병합되지 않은 PR 브랜치에만 있었다. AC 판정·Status는 바꾸지 않는다. 문서 스스로 "최종 승인이 아니며 독립 Reviewer 검토를 거쳐야 한다"고 적고 있다.

## 수신 정보

| 항목 | 값 |
|---|---|
| 출처 | `321Team/infra-kubernetes` 커밋 [`2d35809313c70731c58d210b37ef29ed0a300883`](https://github.com/321Team/infra-kubernetes/blob/2d35809313c70731c58d210b37ef29ed0a300883/docs/evidence/P1-SEC-01/GATE2_RUNTIME_EXECUTION_20260922.md)의 `docs/evidence/P1-SEC-01/GATE2_RUNTIME_EXECUTION_20260922.md` |
| 커밋 작성 | hayeounglee, 2026-09-22 12:54:44 +0900 |
| 소속 | infra-kubernetes [PR #7](https://github.com/321Team/infra-kubernetes/pull/7)(열림, HEAD `c9ec46d`)과 PR #21(닫힘, 미병합)의 이력. infra-kubernetes main에는 없다(2026-09-24 확인) |
| 사본 | `source/GATE2_RUNTIME_EXECUTION_20260922.md` — 바이트 그대로. SHA-256 `1167ceb67017a7d516fb7abc3d1826a57a4de483731c20ce7e7b8dbeaddd89ae`, Git blob `0f020fbfadd40905e06dca602df24fa761f42b3c`(PR #7 HEAD의 같은 경로와 같은 blob) |
| 수신 시각 | 2026-09-24T08:18:21Z |

## 문서 성격

- 실행자가 쓴 서술 기록이다. 명령 출력 원본은 포함하지 않는다.
- 원본 로그 6개는 "k8s-control01의 `~/gate2-final-evidence/logs/`에 보관"한다고 적혀 있고, 수집 시점 SHA-256이 문서에 있다. **이 6개 파일은 수신되지 않았다.** 받으면 문서의 SHA-256과 대조할 수 있다.
- 문서 안에 실제 키·비밀번호 값은 없다(문서 스스로 명시, 이번 검색에서도 발견되지 않음).

## 문서가 스스로 적은 미해결 보안 후속 (상태 미확인)

| 항목 | 문서 내용 | 확인 대상 |
|---|---|---|
| etcd secretbox 키 노출 | 키 값이 CP 3대 shell history와 작업 세션 대화 기록에 평문으로 남음. control02/03 history 정리 로그(`06-history-cleanup-confirmed.txt`)가 있다고 적힘. control01 정리와 키 로테이션 여부는 적혀 있지 않음 | P1-SEC-01·P1-K8S-01 Lead |
| **DB 비밀번호 노출** | `transaction-api-db-credentials` 생성 과정에서 DB 비밀번호가 세션 대화 텍스트에 평문으로 노출. "P1-DB-01 Lead에게 로테이션 요청 권고" | P1-DB-01 Lead 이재환 |
| Harbor Robot TTL | `robot$fds-ci` duration 60일, 정책 30일과 불일치 | P1-HBR-01 Lead |
| 저장소 밖 GNP | `nodeport-30080-allow` GNP를 클러스터에 직접 적용, 저장소 파일 미반영 | P1-SEC-01 Lead |

## 미수신 원본 (제출 요청 대상)

1. `~/gate2-final-evidence/logs/` 6개 파일(문서의 SHA-256과 대조)
2. etcd raw 조회 결과(`k8s:enc:secretbox:v1:key1:` 접두어 확인) 출력
3. `nodeport-30080-allow` GNP `-o yaml` 출력과 HEP 라벨 조회 결과
4. transaction-api·fds-engine 배포 상태 조회 출력

## 이번에 하지 않은 것

- 클러스터·Harbor·DB 조회, 키·비밀번호 로테이션, AC 체크 변경, infra-kubernetes PR #7 수정
