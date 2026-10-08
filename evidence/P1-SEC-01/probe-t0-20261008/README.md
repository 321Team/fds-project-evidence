# 격리 Probe 1회 T0 실패·정리·수정 후보 — 2026-10-08 KST

실행/수집/코드 수정 이권욱(GWONUK), CODEX_ASSISTED. 독립 리뷰·AC 판정은 별도다.
[작업창 조정 기록](https://github.com/321Team/fds-project-baseline/issues/19#issuecomment-6049479655).
사용자 현재 창 비중첩 확인 및 권장안 전체 착수 지시에 따라 기존14:00 계획의 1회를 앞당겼다.
새 창09:15~10:00/착수한계09:35이며 이 회차로 소진했다. 14:00 자동 재실행은 없다.

### 실행 창 기록의 시각 관계 — 리뷰 후 보완

원 GO의 창은 14:00~15:00이었다. 실제 시각은 아래와 같으며 staging·precheck는
창 조정 코멘트 게시 전에 실행됐다. 사용자 착수 지시와 비중첩 확인을 당시 진행 근거로
사용했지만, 이를 SEC Lead의 사전 동의나 단톡 공지 완료의 증거로 대신하지 않는다.

| 단계 | 2026-10-08 KST | 출처 |
|---|---|---|
| stage 호출 | 09:15:11.264258 | drivers/stage-invocation.json |
| fresh precheck 시작 | 09:15:45.748659 | server-originals/precheck.result.json |
| 창 조정 코멘트 게시 | 09:16:25 | 위 GitHub 코멘트 created_at |
| run-launch 호출 | 09:16:44.292903 | drivers/runlaunch-invocation.json |
| run 실제 시작 | 09:16:45.000727 | server-originals/run.result.json |

따라서 창 조정 게시를 staging·precheck 이전 승인으로 표현하지 않는다. SEC Lead의
사전 인지·동의 및 시작 전 단톡 공지는 **미확인**, 사후 확인 요청은 별도 이슈에 남긴다.
실행 driver는 사전 독립 리뷰 없이 사용됐으며 이번 증적 리뷰는 사후 검토다.
다음 재시험은 새 source/driver를 리뷰 범위에 넣고, 실행자와 다른 사람이 사전 GO와 창을
기록하도록 준비한다. 이 보완은 과거 실행의 승인 상태를 소급 변경하지 않는다.

## 실제 결과

| 단계 | 결과 |
|---|---|
| source | 승인 `d6866187ae32af286cd5d9c651cdcb4d706f5f59` 전체14파일, 원 manifest13/13, Git blob14/14 동일 |
| fresh precheck | 09:15:45.748659~09:15:46.222563 KST, rc0/PRECHECK_RESULT=OK/cleanup0/seal OK |
| run | 09:16:45.000727~09:18:16.384967 KST, **rc3**, T0 Ready 미도달 |
| 직접 원인 | 고정 a7093136 이미지에 `/venv/bin/python3` 부재. runc가 해당 경로 stat ENOENT를 기록 |
| T1/T2/T3 | **NOT_RUN**. readiness/liveness 파일 주입 전 중단 |
| 정리·기준선 | 시험 Pod/Service 각각 UID 조건 삭제·NotFound, cleanup_failed0, 운영 Pod/EndpointSlice diff0, 6노드Ready |
| 사후 독립 조회 | 같은 run label의 Pod/Service0, 해당 Pod UID 이벤트 회수. 시험을 다시 실행하지 않음 |

운영 앱·정책·이미지·보안 설정은 변경하지 않았다. 운영 API Pod의 전체 환경값·Secret은 수집하지 않았다.
이 시험은 격리 exec Probe의 기동 단계에서 실패했다. 실제 APP HTTP Probe AC 성공/SEC 인수로 표시하지 않는다.

## 출처와 실패 해석

실행 위치: `k8s-control01`, 기존 ansible01→svc_ansible sudo 경로. 원본 디렉터리
`/root/sec01-probe-20261008-98hudpso`와 source/run 출력은 보존한다. 본 회차 실행자는 GWONUK이며
기존 SEC Lead 이하영의 책임이나 독립 리뷰 담당을 변경하지 않는다.

원 실행은 T0의 restartCount1→2→3을 계속 기다리다 단계 말미 `Pod 조회 실패/시간 초과`로 abort했다.
그래서 정상 timeout 분기의 describe/events 수집이 실행되지 않았다. 그 원문을 보존하고 별도
`post-readonly.json`에서 해당 UID 이벤트를 회수해 실제 원인을 연결했다. 일부 삭제 응답의
deletionTimestamp는 종료 시각이 아닌 API가 설정한 유예 만료시각이다.

`drivers/imageread.json`은 09:20:03 KST Worker01의 같은 digest 운영 컨테이너를 읽기 조회한 결과다.
프로세스 인수 `python run.py`, exe `/usr/local/bin/python3.12`, `/venv/bin/python3` 부재,
`/usr/local/bin/python3 -> python3.12`를 확인했다. 현재 앱 저장소 apko Dockerfile 경로를
이 과거 실행 이미지와 같은 것으로 취급한 가정이 잘못됐음을 정정한다. 파일 존재/실행 중 exe 관측이
수정 후보의 시험 Pod 보안 조건 전체에서 실행 성공을 보증하지는 않는다.

## 수정 후보와 잔여

[infra-kubernetes PR74](https://github.com/321Team/infra-kubernetes/pull/74),
HEAD `a617a2f505a2ecea4f6b7337871341c87a3caaed`:
실제 고정 이미지의 interpreter 경로, T0 restart 즉시 중단, 최초 Pending 상태 처리,
abort 시 최대30초의 Pod/UID 이벤트 진단과 기존 정리 지속. 실패 경로 예산22분.
로컬 Git Bash MOCK35/35 및 [Linux CI35/35·Bash 구문 SUCCESS](https://github.com/321Team/infra-kubernetes/actions/runs/37707638781/job/113085715017)
(09:25:36 KST)다. 당시 새 소스는 REVIEW/MERGE 대기였다. 10/8 11:39:47 KST
PR74 병합을 재확인했으며, 후보의 현장 RUNTIME은 여전히 NOT_RUN이다.
실제 서버의 승인본은 수정하지 않았고 새 번들을 재시험하지 않았다.

다음은 병합 source와 리뷰된 driver의 새 고정 전체 번들·시작 조건·별도 1회 창 확정 → T0부터 재시험이다.
과거 GO를 수정 후보에 자동 적용하거나 정상 APP/보안 통제를 바꿔 우회하지 않는다.

## 바이트 보존·검증

- `server-originals/`는 원격 바이트 그대로다. 원격102파일의 크기/mode/SHA는 `RECEIPT.json`에 있다.
- 원 precheck/run의 봉인 검증기를 수신본에 적용해 둘 다 verify=OK를 확인했다.
  리뷰 보완으로 원 archive 2개와 원 sidecar 2개를 `server-originals/`에 바이트 그대로 추가했다.
  수신 receipt SHA/크기 및 sidecar 대조, archive 내부 파일 20개/41개와 기존 추출본의
  바이트 동일성을 확인했다. 재압축하지 않았고 `registry/ARCHIVE_CONTENTS.json`에 목록을 등록했다.
  현재 서버를 재조회한 결과가 아니라, 최초 수신 메타데이터와 보존된 로컬 원본의 재대조다.
- `drivers/`에 실제 전달/실행/회수/사후 관측 소스·명령·시각·종료 코드를 보존한다.
- `ci-run.json`/`ci-log.txt`는 **수정 후보**의 CI다. 실패한 현장 소스의 Runtime 결과와 구분한다.
- `python3 analyze.py`는 원본 hash와 종료/기준선/이벤트/진입점 대응을 오프라인 재검산한다.
- collection SHA256SUMS/루트 대장은 편입 바이트를 검증한다. hash·CI 성공은 AC 인수를 대신하지 않는다.
