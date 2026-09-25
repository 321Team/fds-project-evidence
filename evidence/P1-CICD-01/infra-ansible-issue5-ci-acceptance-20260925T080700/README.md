# Issue #5 일반 Workflow 정상/고의 결함 CI 인수 — 2026-09-25

관련: [infra-ansible #5](https://github.com/321Team/infra-ansible/issues/5), [PR47](https://github.com/321Team/infra-ansible/pull/47)(정상 후보, HEAD `c6ba5f87711acc3eeeba12c13c72cedd09d178f8`, hayeounglee 독립 코드 리뷰 APPROVED), [PR51](https://github.com/321Team/infra-ansible/pull/51)(고의 결함 후보, TEST ONLY / DO NOT MERGE, HEAD `1408583cdbf6cc257c996dc96d66de6e9c8ec670`). 담당자가 실제 cicd-runner01/ansible01에서 토큰 발급·1-job ephemeral Runner `serve`를 두 차례 실행했고, 이 세션(Claude Code)이 GitHub API·Job 로그·제출된 로컬 증적을 직접 대조했다. 이 편입 자체의 독립 검토는 아직 없다.

## 판정

**정상 후보 실제 Actions PASS / 고의 결함 후보 실제 Actions FAIL — 모두 확인.** Runner 실등록·일반 CI Run 자체는 처음으로 실제 실행됐다. 운영 apply·엔진 전환·Issue #5 최종 AC·PR47 병합은 이 편입에 포함하지 않는다.

| 항목 | 정상 후보(PR47) | 고의 결함 후보(PR51) |
|---|---|---|
| source HEAD | `c6ba5f87711acc3eeeba12c13c72cedd09d178f8` | `1408583cdbf6cc257c996dc96d66de6e9c8ec670` |
| Run / Attempt | [35889332032](https://github.com/321Team/infra-ansible/actions/runs/35889332032) / 2 | [36109856584](https://github.com/321Team/infra-ansible/actions/runs/36109856584) / 1 |
| Job / Check ID | 107987104433 | 107990615364 |
| 실행 시각(UTC) | 07:39:13–07:46:13 | 08:02:13–08:07:10 |
| GitHub 결론 | `completed` / `success` | `completed` / `failure` |
| syntax(2엔진×22 playbook=44) | 44/44 rc0 | 44/44 rc0(`harden_svc_ansible_key.yml` 포함) |
| fixtures | `PASS_FRESH_OFFLINE_FIXTURES`(unit-tests·guards·contract·dns×2 전부 rc0) | `FAIL`, 실패 지점 `fixtures/guards` — unit-tests만 rc0 이후 실패 |
| Artifact | `ansible-ci-35889332032-2-c6ba5f8...`, 475,395 bytes, digest `sha256:6bf6bdd5...` | `ansible-ci-36109856584-1-1408583c...`, 318,458 bytes, digest `sha256:83a6db5b...` |
| 로컬 host_rc | 0 | 0 |
| 로컬 bundle_sha256 | `e2fbefffa01b8a0f401cd4623b497944d0e41264ad13343d42ff2b272707d5c6` | 동일 |
| 세션 정리(로그 직접 확인) | `runner-remove`→`runner-absent`, `proxy-remove`→`proxy-absent` | 동일 |

## 확인한 사실과 근거

- **GitHub API 직접 조회**(이 세션): 위 Run/Job/Check ID, 결론, 시각, source SHA, artifact 메타데이터(`GITHUB_SNAPSHOT.json` 참고).
- **Job 로그 원문 직접 확인**(이 세션, `get_job_logs`): 두 Run 모두 workflow가 출력한 `CI_RESULT` JSON 요약을 로그에서 읽었다.
  - 정상 후보: syntax 44/44 rc0, fixtures 5단계(unit-tests/guards/contract/dns-2.16.19/dns-2.21.3) 전부 rc0, `status: PASS_FRESH_OFFLINE_FIXTURES`.
  - 결함 후보: syntax 44/44 rc0(결함 patch는 값만 바꿔 구문 자체는 유효), unit-tests rc0, 그 다음 `fixtures.status: FAIL`, 에러가 정확히 `.../result/fixtures/guards`를 가리킴. 체크아웃·설치·구문·unit-test는 전부 정상이었고 guards 단계에서만 실패했다는 점에서 환경 오류 패턴과 다르다.
- **제출된 로컬 증적**(`received/normal-pr47/`, `received/negative-pr51/`, 각 `ansible-actions-runner-evidence.tar.gz` + `.sha256`): 외부 sha256 sidecar 일치 확인, 내부 `SHA256SUMS` 각 15/15 파일 일치 확인(이 세션이 직접 추출·검증), `HOME_RUN_RESULT.json`의 `host_rc:0`·`bundle_sha256` 일치 확인, `dedicated-run.log`에서 `STAGE=runner-remove`→`runner-absent`, `STAGE=proxy-remove`→`proxy-absent`, `STATUS=SESSION_ENDED_REQUIRES_CI_REVIEW`를 grep으로 직접 확인(정상/결함 각각).
- `docs/ci/patches/intentional-count-defect.patch`가 그대로 적용됐음을 PR51의 diff(1파일 +1/-1)로 확인.

## 한계 — 이 편입에서 확인하지 못한 것

1. **artifact ZIP 내부 바이트 미확인.** 이 세션의 egress 프록시 정책이 Azure Blob(`productionresultssa6.blob.core.windows.net`) 다운로드를 CONNECT 403으로 차단해, 두 artifact 모두 GitHub가 보고한 digest/size만 확인했고 내부 파일을 직접 열어보지 못했다.
2. **결함 5개 조합 개별 확인 미완료.** `ACTIONS_ACCEPTANCE.md`가 요구하는 `one_plain/one_restricted/two_plain/two_restricted/mixed` 개별 불일치 확인은 artifact 내부 guards 로그에 있어 위 1번과 같은 이유로 못 했다. `fixtures/guards` 단계 FAIL이라는 위치 정보까지만 확인했다.
3. **Runner ID/name 관리 API 등록 부재 재확인 미수행.** 과거 ID5/ID6 방식(관리 API로 실제 등록 목록에서 부재 확인)을 이번 두 세션에 대해 하지 않았다. 로컬 `dedicated-run.log`의 `runner-absent` 로그만 근거다.
4. **저장소 Variables 실시간 재조회 미수행.** `ANSIBLE_CI_ENABLED=true`였음은 두 Job이 `skipped`가 아니라 실제 실행됐다는 결과로부터의 추론이며, 이 세션이 Settings 화면/API를 직접 재조회한 것은 아니다.
5. 위 항목 1~3은 리뷰어가 직접 서버·artifact에 접근해 보완할 수 있다.

## 다음 절차

1. 이 편입의 독립 검토(hayeounglee 요청).
2. 가능하면 리뷰어가 artifact ZIP을 직접 받아 위 한계 1·2를 보완.
3. Runner ID 관리 API 등록 부재 재확인(정상/결함 각 세션).
4. Lead(GWONUK)가 실제 결과를 근거로 Issue #5 AC와 PR47 수동 병합 여부를 판단. PR51(TEST ONLY)은 병합하지 않고 close한다.

## 단계 구분

| 단계 | 이번 결과 |
|---|---|
| STATIC / 수신 검증 | 제출 증적 원본·내부 manifest 대조 완료(정상/결함 각 15/15) |
| CI | 정상 Run success, 결함 Run failure — 둘 다 실제 GitHub Actions 실행 |
| RUNTIME(로컬) | 두 세션 `host_rc:0`, `bundle_sha256` 승인값 일치, 세션 정리 로그 확인 |
| ARTIFACT 내부 | 미확인(위 한계 1·2) |
| REVIEW | 이 편입의 독립 검토 아직 없음 |
| MERGE / AC | PR47 병합·Issue #5 AC·운영 apply 모두 아직 없음 |
