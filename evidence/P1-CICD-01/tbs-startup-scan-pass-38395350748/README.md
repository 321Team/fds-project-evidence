# 수정본 TBS — 두 이미지 기동·Scan PASS, 2026-10-13

이권욱 / CODEX_ASSISTED. **[Run38395350748/Attempt1](https://github.com/321Team/infra-cicd/actions/runs/38395350748)은 Test/Build/격리 이미지 기동/Scan을 통과했다.** Push·Deploy·업무 APP/E2E/DB 인수는 하지 않았다. 이전 실패를 소급 PASS로 바꾸지 않는다.

## 승인·실행 기준

- [새 실행안](https://github.com/321Team/fds-project-baseline/pull/168#issuecomment-6145055790), [사용자 승인](https://github.com/321Team/fds-project-baseline/pull/168#issuecomment-6145117622): 새 Run1회, 10/13 21:10~21:20 KST 실제 시작, 10/14 00:35 KST 수집·정리 종료 상한. 실패 시 자동 재실행 금지, Push·Deploy 제외. 이번1회는 소진했다.
- [Job115289040431](https://github.com/321Team/infra-cicd/actions/runs/38395350748/job/115289040431): **21:10:28~21:12:08 KST**, success. 서버 receipt21:10:33.453~21:12:02.444와 GitHub 시각을 구분한다.
- 실행 CICD main `147f760298dd4a683ea58f2a887483769352b97d`, [PR78](https://github.com/321Team/infra-cicd/pull/78) 독립 승인 HEAD `7ebf101b88814498f7390a2c7afb2a5b9fd9c96e`와 tree 동일, [main CI](https://github.com/321Team/infra-cicd/actions/runs/38393360302) SUCCESS. APP `affbc69beef9967f7977d09a6fec14f7fb6c0e94`와 기존 두 앱을 유지했다.
- config SHA256 `72eb52594048aa713ade12621f4545def0395f3f1603adec7bab3385b24f13e3`, workflow SHA256 `40a5dcd56b0bb6feb816bb297eb27bb747524181e914dcf514d614492ace2982`. 바뀐 실행 파일은 inspect `.Id`→`.ID` 수정뿐이며 보안/격리 기준을 완화하지 않았다.
- Runner `cicd-runner01/server01_cicd-runner` UID1000/rootless Podman6.1.0. 직전21:09 home/공급0700·Worker0·약47GiB 가용, 공급 manifest `6ab02000437a7b5f7d3c99e5202d40b663056a998018a1894360c58de68b73d4` 일치. Token 만료11/12는 사용자 확인, Secret updated20:03:38은 metadata, 실제 source fetch는 이번 exit0으로 각각 구분한다.

## 관측 결과와 한계

| 단계 | 실제 결과 |
|---|---|
| Source/handoff | 전용 소스 인증 exit0, 승인 Source Commit 일치, HANDOFF PASS |
| 시험 | engine Unit16 + API Contract20 + engine Contract15 = **51 PASS**. API Unit은 기존 APP Source별 승인에 따른 NOT_APPLICABLE |
| Build/save | 두 이미지 모두 PASS, archive/config/manifest identity 결속 |
| 실제 기동 | 두 이미지 모두 UID10001/GID999·read-only·network none·mount 없음. entrypoint/CMD 유지. API7개/engine5개 파일 실제 읽기 |
| listener/probe | 두 앱 모두 업무 `/livez`200, 업무 `/metrics`404, 전용 `/metrics`200, 전용 `/livez`404 |
| 취약점 검사 | fresh Trivy DB 준비 PASS, 두 이미지 scan exit0·HIGH0/CRITICAL0 |
| 정리 | 각각 자기 CID remove exit0·후속 ps 비어 있음·cleanup REMOVED, 수집 시 Worker0 |
| Push/Deploy/업무 인수 | NOT_EXECUTED / NOT_VERIFIED |

이 결과로 해당 두 후보 이미지의 비루트 파일 읽기와 제한된 실제 기동·포트 분리 성공을 확인했다. DB readiness·거래 저장/조회·운영 NetworkPolicy·Kubernetes Runtime·HA·APP/E2E·DB 최종 인수는 별개다. `DB_PREFLIGHT=PASS`는 **Trivy 취약점 DB 준비**이며 업무 DB 검증이 아니다. scan receipt의 `source_approval=NOT_VERIFIED`는 standalone scanner의 경계이고, source 승인 결속은 상위 handoff/build 및 기존 APP27 승인으로 다룬다. LOW/MEDIUM 부재나 모든 취약점0을 주장하지 않는다.

## 원본·수신 검증

서버 원본 `/home/server01_cicd-runner/FDS_CICD_AppWorkflow.3_geu2kf`와 실제 checkout은 보존했다. `run-38395350748/`에는 선별 수신한 원본 receipt/manifest/로그와 GitHub 메타데이터·로그가 있다. 원본 바이트를 변경하지 않았다. `VALIDATION.json`은 수신 바이트·Run/코드/입력/시간·receipt/hash·probe/정리/Scan 결속의 로컬 대조 결과다.

추가 순수 읽기에서 실제 checkout의 delivery/trivy Python77파일을 병합 Git blob SHA256과 대조한 뒤 기존 `app_evidence.check(Local(...))`를 실행했다. `EVIDENCE_CHECK=PASS`, `BINDING=COMPLETE`, `RAW_PAYLOAD_CHECK=LOCAL_BYTES`, 원본87개 검증을 확인했다. 이는 원본 연결/바이트·이미지 구조·보고서 판정 대조이며 새 TBS 실행이나 인수 승인 자체가 아니다. 원본 출처에 대한 독립 증적 리뷰는 별도다.

두 OCI archive·상세 Scan report·Trivy DB 본체는 Runner에만 보존하고 Git에 복사하지 않았다. 실제 보고서 내용은 출력하지 않고 hash/크기와 판정만 수집했다. 원본 manifest는 이 미편입 payload도 가리키므로 Git 사본만으로 모든 서버 원본을 다시 확인할 수 없다. 서버 검증 기록 `runtime-evidence-check/stdout.json` 및 수집 receipt를 사용한다. 두 cidfile은 rm 뒤 부재이며 receipt와 create/remove 원본에 같은 CID가 보존돼 있다.

수집기는 **PURE_READ_PRECHECK / REVIEW=NOT PERFORMED (Pre-check)**다. 기존 strict SSH·UID1000 범위에서 정해진 파일/metadata/hash만 읽었으며 설치·서비스/계정/보안 통제 변경은 하지 않았다. argv·대상·시각·rc·collector SHA256·출력 hash는 각 수집 폴더 receipt에 있다. `tbs_control.py`/`run_snapshot.py`는 이번 로컬 실행 이력 사본이며 증적 폴더에서 재실행하지 않는다. 별도 공개나 새로운 Secret 값·token hash 수집은 없다.

## 후속

`NEXT_PUSH_HANDOFF.json`에 실제 생성된 두 이미지와 Run/receipt/hash를 연결했다. 이것은 관측 결과 인계이며 실행 가능한 Push 승인 record가 아니다. 다음은 기존 절차대로 fresh Push 입력·Robot 권한/만료/임시 credential 수령·회수 조건·Harbor 비중첩과 새 회차/시간창을 확정하고, 기존 Push workflow의 fresh Scan/원격 digest 대조를 수행하는 것이다. TBS 승인에 Push·Deploy를 포함하지 않았다.

PR78·증적215·216·실행 카드168은 병합 상태다. 이번 **새 증적**은 Draft·독립 REVIEW/MERGE 대기이며 자동 병합·티켓 종결은 하지 않는다. 이후 Deploy→최소 HA/복귀→최종 앱 회귀→DB 판단, W4 NOT_MEASURED·DR 종결 한계·C01 기술 ACL 미검증은 유지한다.
