# P1-CICD-01 고의 Unit 실패 Runtime — 2026-10-14

CODEX_ASSISTED · 실행/수집 이권욱 · **의도한 실패 관측 및 전후 이미지 유지 확인. 증적 독립 검토·AC04 수용 대기.**

## 실행과 승인

- 코드: [infra-cicd PR79](https://github.com/321Team/infra-cicd/pull/79), 최신 HEAD `d0031e183406104368f4fd7855ec0453d1063ad4`의 [이하영 독립 승인](https://github.com/321Team/infra-cicd/pull/79#pullrequestreview-5511591881), 09:22:03 KST 병합 `7171b0a3d636c3a15c78131b89bec4739cb6f49b`. 두 tree 동일.
- 사용자의 별도 실행 지시: “리뷰 확인 후 차단사항 없으면 병합하고 착수”. 앞서 제시한 PR79의 고정 Unit 실패 시험 **새 1회**에 적용했다. 코드 리뷰를 Runtime GO로 확대하지 않았다. [범위 기록](execution/USER_AUTHORIZATION.json).
- [Run38490368352](https://github.com/321Team/infra-cicd/actions/runs/38490368352), Attempt1, Job115613871822, cicd-runner01 / `server01_cicd-runner` UID1000. dispatch 09:28:24, 프로그램 09:28:33~09:28:50 KST. GitHub와 프로그램 결과는 **FAILURE / rc1**로 보존한다.
- 입력 config SHA256 `72eb52594048aa713ade12621f4545def0395f3f1603adec7bab3385b24f13e3`, APP `affbc69beef9967f7977d09a6fec14f7fb6c0e94`, 공급 manifest `6ab02000437a7b5f7d3c99e5202d40b663056a998018a1894360c58de68b73d4`.
- source-read Secret 값은 조회/수집하지 않았다. 새 Robot/Kubernetes Token 발급, Push, Deploy, Harbor 재시작, VM/호스트 전원 변경은 실행하지 않았다. 새 Run 자동 재시도·같은 Run rerun도 없다.

## 실제 결과

| 확인 항목 | 원본과 판정 |
|---|---|
| 사전 builder | [archive 읽기](collection/builder-read/stdout.json): 승인 archive/config hash 일치, PATH의 `/usr/bin/python3.13` regular file 0755. 추출/실행 없이 사전 존재 점검 |
| 기존 앱 Unit | [fds-engine Unit](originals/build-scan/fds-engine-unit-0.log) **16 passed**, step rc0. transaction-api Unit N/A는 승인 config의 기존 범위 |
| 고정 추가 Unit | [실제 assertion](originals/build-scan/unit-negative-start.log) `P1_CICD_INTENTIONAL_UNIT_FAILURE`, `Ran 1 test`, `FAILED (failures=1)`, step rc1 |
| 후속 차단 | [TBS 원본](originals/build-scan/result.json): `COMMAND_FAILED:unit-negative-start`, `EXPECTED_FAILURE_OBSERVED`, `images={}`. Contract/Build/save step 없음, Scan 디렉터리·새 앱 이미지 archive 없음 |
| 컨테이너 회수 | create/identity/cleanup-identity/remove의 CID·name·label·image 대조, removed ps 결과 empty. `e07e6af5749fac5c1075b17852a3a44fe9fa54369160dd79e524fc365e90e73d`만 제거 |
| 앱 이미지 유지 | 사전 09:27:01 / 사후 09:29:05 GET. 두 Deployment UID/generation/spec hash/image 동일, 각각 Ready3. 6개 Pod UID/imageID/containerID/restartCount 동일. Service/EndpointSlice도 동일 |
| 잔존·비중첩 | Worker0, Runner online/idle, 기존 Push claim4개 hash 동일. 실행 직전 active CICD Run0, 이후 해당 시간대 다른 CICD Run 없음. 사전·사후 Harbor strict TLS health200 / 8 healthy |

[VERIFICATION.json](VERIFICATION.json)에 두 앱 digest, Pod별 비교, 실행·판정 범위를 기록했다. 전후 관측은 두 시점의 유지 증거이며, 관측 사이 모든 순간의 무변경을 증명한다고 확대하지 않는다.

## 원본·수신·검증

- 서버 원본: `/home/server01_cicd-runner/FDS_CICD_UnitNegative.eb8ljt_m`. **원본 66개**를 바이트 그대로 수신했다. [수신 메타데이터](COLLECTION_METADATA.json)의 각 해시와 step log SHA, app→build/handoff SHA 및 서버 SHA256SUMS를 모두 대조했다.
- `originals/`는 원본, `collection/`은 읽기 수집기·명령/계정/시각/수집기 hash/rc·전후 관측, `github/`는 API 수신 metadata/Run log, `execution/`은 승인·dispatch·Source CI 이력이다. 원본에 사후 판정 문구를 삽입하지 않았다.
- 조회 수집기는 **REVIEW=NOT PERFORMED (Pre-check)**. 기존 SSH 계정으로 GET/파일 읽기만 수행하고 새 수신 파일은 이 PC에 기록했다. 앱 상태 조회만 control01의 기존 `sudo -n` 경로를 썼으며 시험 프로그램은 정상 Runner UID1000에서 실행했다.
- 첫 회수는 Podman 제거 뒤 `container.cid` 파일이 남아 있다는 수집기 가정 때문에 중단됐다(`collection/raw-result`, rc1). 파일 부재만으로 회수 성공을 판단하지 않고 원본 identity/remove/ps 로그의 같은 CID를 대조하여 두 번째 읽기 수집에서 66개를 회수했다(`collection/raw-result-02`, rc0). Runtime 재실행은 없었다. 전송용 base64 JSON은 PC에 보존하고 이 PR에는 디코딩된 원본·전송 SHA·수집 메타데이터를 편입했다.
- 각 회차 [SHA256SUMS](SHA256SUMS)와 루트 REGISTRY에 연결한다. 해시 일치는 무결성 점검이며 AC 인수와 구분한다. `python verify.py`로 원본 연결·Unit 결과·전후 상태 및 회차 해시를 다시 확인할 수 있다.

## Source CI 이력과 한계

PR HEAD CI38488903891은 676건 통과했다. 병합 직후 [CI38489765233](https://github.com/321Team/infra-cicd/actions/runs/38489765233) Attempt1은 기존 `test_process_timeout_terminates_process_group`의 SIGKILL 직후 `/proc` 상태 비교에서 `R != Z`로 실패했다. 해당 시험 파일은 PR79에서 바뀌지 않았고, **동일 코드의 실패 작업만 1회 재실행한 Attempt2는 676건 통과**했다. 두 CI 원본 로그를 보존했다. 스케줄링 시점에 따른 경쟁으로 의심하지만 원인 확정/안정화 완료로 보고하지 않는다. Runtime 시험의 재실행과도 구분한다.

이번 결과는 승인 앱 Unit 뒤에 고정 stdlib Unit을 추가한 **실패 처리 경로**를 검증한다. 앱 기존 Unit 코드를 변조한 시험은 아니다. Workflow에는 downstream Push/Deploy Job 자체가 없으므로 실제 GitHub `skipped` Job 증적으로 표시하지 않는다. **후속 미호출·새 이미지 미생성·전후 배포 이미지 유지**가 입증 범위다.

증적 편입 REVIEW/MERGE와 이 범위의 AC04 최종 수용은 대기다. P1-CICD-01 전체 Done, `DELIVERY_GATE=PASS`, Phase1 종료로 확대하지 않는다. 다음 순서는 AC05 기존 취약점/스캐너 오류 원본과 당시 이미지 유지 증거의 누락 대조, 이후 AC07/08 권한·Token, AC09 승인 digest 복귀, 전체 Delivery/E2E 인수다. 별도 실제 변경 시험의 범위는 그 단계에서 확정한다.
