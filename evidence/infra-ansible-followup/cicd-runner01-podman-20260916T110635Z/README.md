# cicd-runner01 r3 실제 실행 수신 검토 — 2026-09-16

**판정: PASS_LOCAL_REVALIDATION.** 사용자가 서버에서 실행해 제출한 원본을 검토했다. 수신 검토자가 서버에서 대신 실행한 결과가 아니다. 이전 sudo 판단·호스트 PATH·이미지 entry 접근 문제를 지난 뒤 두 Ansible 엔진의 지정된 구문/localhost 회귀가 완료됐다. 이번 수신 검토에 따른 코드 변경이나 동일 소스 재실행은 필요하지 않다.

## 실행과 소스 식별

- 실행 UTC: 2026-09-16 11:06:35.263931 ~ 11:13:59.636053. KST 20:06:35 ~ 20:13:59, 약 7분 24초.
- 호스트 cicd-runner01, 전용 계정 `ansible-verify` UID1001. 기존 로그인 계정 `server01_cicd-runner` UID1000의 홈으로 원본과 결과를 수집했다.
- PR17 소스: `169571801d1b0cee0ba75137380149a48d6b56dd`.
- PR18 소스: `d5147ebff0febbb8ab2afca28fe64d68301e033c`.
- HOME/HOST/CONTAINER/원래 RUN_RESULT의 결과는 모두 `PASS_LOCAL_REVALIDATION`. 호스트·컨테이너 종료 0, OOMKilled false, 해당 CID 정리 `REMOVED`/rc0.
- r3 Containerfile SHA256: `241d5febda6f288e1d938d4e84d65eeb12bc92fac42ac540a1f24f2a8edfce00`.
- r3 entry SHA256: `011cbe789bfaaa2b77d7225c6c39163635be35911a0aea627f73043031fa8727`. 배포한 r3 바이트와 일치한다.
- 실제 이미지 ID: `sha256:6c175e1fc8143f9ddbc3d8d9f883565f6d844850a14c728732ca7e89a0efd409`.

## 실제 검증 범위

| 항목 | 결과 | 해석 |
|---|---:|---|
| 격리 검사 | 13/13 | UID/GID1000, CPU2, 메모리4GiB, PID512, capability0, no-new-privileges, seccomp/SELinux, 네트워크 lo만, root/kit 읽기 전용·work 쓰기 가능 |
| 사전점검 | 7/7 | Python3.12.14, 필요 도구·venv, 로컬 IPC 생성 포함 |
| 구문 검사 | 32/32 | 정확한 16개 경로 × 엔진2, 원문 EXIT_CODE0 |
| 단위시험 | 56/56 | stderr의 실행 개수·OK 및 EXIT_CODE0 대조 |
| Guard | 14변형 기대결과 일치 | 두 엔진 합계196개 하위 관찰. 의도된 실패/오류 검출 포함 |
| Callback 계약 | 58개 기대결과 일치 | localhost 별칭의 실제 CLI32개 + callback 변조 fixture26개 |
| DNS | 2/2 | 두 엔진의 실제 localhost 명령 exit0 |
| Egress 2.16.19 | 45/45 기대결과 일치 | localhost CLI/task와 중단 복원 모형 |
| Egress 2.21.3 | 45/45 기대결과 일치 | localhost CLI/task와 중단 복원 모형 |

수신 검토는 PASS 문자열뿐 아니라 고정 소스에서 도출한 정확한 시험 집합, 엔진별 기대 exit/status, 단위시험 원문, callback 원본 artifact 해시와 fixture의 원본 연결, egress 45개 case 집합과 rc를 대조했다. 집계 RUN_RESULT와 별도 결과 파일도 일치한다. 두 egress 실행 모두 source_dirty=false다.

이미지 빌드의 모든 단계는 **캐시를 재사용**했다. 따라서 이번 image-build.log가 새 `--self-test` 실행의 stdout을 증명한다고 해석하지 않는다. 실제 컨테이너에서는 entry가 UID1000으로 실행되어 격리·사전점검·전체 지정 시험을 완료했다. 앞선 제작 환경의 실제 UID 시험2개 차단 기록도 소급해서 PASS로 변경하지 않는다.

## 원본과 무결성

- 사용자 첨부명: `ansible-podman-evidence.tar(2).gz`, sidecar `ansible-podman-evidence.tar.gz(2).sha256`. 내려받기 접미사만 다르며 sidecar의 정식 파일명은 `ansible-podman-evidence.tar.gz`다.
- [수신 원본 압축](input/ansible-podman-evidence.tar.gz): 499,685바이트, SHA256 `194e0fc6c79dc81800fe9d2495340639c7e7ff8043153251dd82218af98adfbd`.
- [수신 sidecar](input/ansible-podman-evidence.tar.gz.sha256)는 원문 그대로 보존했다.
- 내부 원래 호스트 압축 SHA256: `d28d62cb897954c8be9c5a96328401d989ef31f5e9b33534b935a6d4ecc3a20d`.
- 바깥 압축 regular file17개, 내부 호스트 압축1033개. 경로 안전성·중복·파일 유형을 검토하고 포함 바이트·집합·sidecar 및 중첩 manifest16개를 대조했다. 원래 preflight/run 압축과 펼쳐진 사본도 일치한다.
- CI ARTIFACT_SCOPE에 명시된 module-cache 파일3개는 원래 수집 범위에서 제외됐다. 포함 파일의 해시는 모두 확인했지만, 제외되어 없는3개 파일의 바이트 자체를 확인했다고 주장하지 않는다.
- 각 egress 하위 SHA256SUMS는 생성 코드상 바로 아래 파일만 열거한다. 중첩 `state/original-squid.conf`는 상위 전체 manifest에 포함되어 검증됐다.
- `selected-original/`은 편의를 위한 원본 파일의 바이트 동일 사본이다. 전체 원문은 input 압축에 보존했다. 이 회차 SHA256SUMS는 README·검토 결과·선별 원문·압축/sidecar를 포함한다.

검토 집계: [RECEIPT_REVIEW.json](RECEIPT_REVIEW.json). 실행 집계: [HOME_RUN_RESULT](selected-original/home/HOME_RUN_RESULT.json), [HOST_RUN_RESULT](selected-original/host/HOST_RUN_RESULT.json), [RUN_RESULT](selected-original/result/RUN_RESULT.json). 상세 계약/guard/DNS/egress 로그는 원본 압축에서 확인한다.

## 남은 인수 조건

이번 결과는 실제 격리 서버의 **구문·localhost fixture/CLI 회귀**다. 실제 Squid/firewalld/SSH 운영 동작이나 실습망 readonly 검증을 완료한 것으로 확장하지 않는다. GitHub Actions는 `NOT_RUN`이며 관련 CI_RESULT의 GitHub/Runner 식별 필드는 null이다. 운영 apply·엔진 전환도 수행하지 않았다.

1. Runner의 infra-ansible 저장소 접근, labels/group, 격리·정리 조건에 대한 확인과 승인.
2. 승인된 Runner에서 정상 입력과 의도적 오류 입력의 실제 Actions 실행, 대상 SHA·check·artifact 확인.
3. PR17·18 코드와 PR13 증적의 독립 리뷰 및 별도 병합 판단.

수신 시 PR17·18·13은 모두 Draft/open/unmerged다. PR17·18의 review 목록은 비어 있고, PR13의 기존 COMMENTED 리뷰는 이번 새 회차 승인으로 간주하지 않는다. Issue5 인수 조건 전체 완료나 운영 착수 승인으로 표시하지 않는다. 이전 FAIL·환경 차단 기록은 유지한다.

사용자 지침을 유지한다: **증적은 기존 로그인 계정 홈에 생성하고, 코드 변경 전 딥리뷰한다.** 이번 변경은 증적 편입과 진행 기록 갱신이다.
