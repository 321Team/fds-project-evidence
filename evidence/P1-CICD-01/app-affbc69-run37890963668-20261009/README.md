# P1-CICD-01 — affbc69 실제 Test→Build→Scan 및 증적 인계

2026-10-09 KST · CODEX_ASSISTED · 이권욱. **지정 Source/Run의 Test→Build→Scan PASS**. [Run37890963668](https://github.com/321Team/infra-cicd/actions/runs/37890963668) / Attempt1 / Job113691566243 / Runner2(cicd-runner01). Job14:56:22~14:57:50 KST(1분28초).

## 실행 조건과 결과

- 사용자 단독 창13:20~17:00. 사용자가 별도 질문에 **“Test→Build→Scan 1회 승인”**으로 회차 승인했다. 15:30 이전 시작·16:20 미완료 시 취소 판단·17:00 내 결과/잔존 확인, Harbor Push·배포 제외 조건. [실행 기록](https://github.com/321Team/infra-cicd/issues/11#issuecomment-6075229741). 코드 리뷰를 Runtime GO로 확대하지 않았다.
- CICD main `c9eff5fb2e50a690818a3e67347ab4a1bfc88f51`, APP Source `affbc69beef9967f7977d09a6fec14f7fb6c0e94`, config SHA256 `72eb52594048aa713ade12621f4545def0395f3f1603adec7bab3385b24f13e3`. [CICD73](https://github.com/321Team/infra-cicd/pull/73) 승인·병합 및 [APP 입력 확정](https://github.com/321Team/infra-cicd/issues/11#issuecomment-6074515472), [공급 배치 증적189](https://github.com/321Team/fds-project-evidence/pull/189)을 연결한다. 증적189 독립 편입과 이번 Runtime은 별도 단계다.
- 정상 server01_cicd-runner/UID1000, 공급125파일·config hash 재대조, 공간/기본 실행 컨테이너0, GitHub 대기/실행0, Runner online/idle 확인 후 main workflow를1회 dispatch했다. 실제 Run/Attempt/HEAD 일치.
- fds-engine Unit16/Contract15, transaction-api Contract20 PASS(원 로그 종료 요약은 private-store-check.stdout). API Unit은 해당 Source의 APP 확정 NOT_APPLICABLE이며 시험 PASS 수에 넣지 않는다.
- 두 이미지 Build 및 Scan PASS, HIGH0/CRITICAL0. 모든 심각도 취약점0 또는 모든 보안 AC 완료를 뜻하지 않는다. 이미지 manifest/config/archive/report digest는 SUMMARY.json과 수집 archive의 scan receipt에서 확인한다.
- 이번 Run 전용 Trivy DB DownloadedAt05:57:39Z(14:57:39 KST), NextUpdate10/10 01:16:59Z(10:16:59 KST). 서버 수집기가 원 검사 시각의 DB freshness·hash를 검증했다. 과거 cache의 PASS를 재사용하지 않았다.

## 원본과 수신 검증

원 실행 디렉터리 `/home/server01_cicd-runner/FDS_CICD_AppWorkflow.57rithja`를 검토된 같은 main의 app_evidence.py collect로 검사했다. `EVIDENCE_CHECK=PASS / BINDING=COMPLETE / SOURCE_BINDING=MATCH / RECORDED_APP_WORKFLOW=PASS / RAW_PAYLOAD_CHECK=LOCAL_BYTES`.

원 archive `/home/server01_cicd-runner/app-evidence-37890963668-12rymtkl/collection/app-evidence.tar.gz`, SHA256 `9dd174dafbbb0f8f198288e5bb7a747948cec97bff86b251db56eeffa6a56ff2`. 재압축 없이 수신·sidecar·내부receipt hash 대조. JSON receipt6개와 manifest1개만 포함하며 raw logs/Source/images/wheels/DB/report 본문은 제외돼 서버에 보존한다.

수신 측 ansible01에서 동일 main 도구와 **절대경로**의 archive/외부 expected로 verify rc0. `RAW_PAYLOAD_CHECK=NOT_INCLUDED_SERVER_RECORD_ONLY`: 수신 단계는 생략된 원본을 직접 재검사하지 못하며 서버 기록과 허용 metadata를 대조한다. `SOURCE_APPROVAL=NOT_INDEPENDENTLY_VERIFIED`는 검증 도구의 범위이며 사람의 APP/config/이번회차 승인은 위 근거를 따로 연결한다.

## 종료·보존·후속

14:59 실행 프로세스0·workflow lock 해제·기본 및 이번 Run 전용 VFS store 컨테이너0, GitHub Runner2 online/idle 확인. 원본·이미지 store는 증적/후속 인계를 위해 보존했다. 광범위 삭제/prune/reset/서비스 재시작은 하지 않았다. 보존을 자원 삭제 완료로 표현하지 않는다.

보존된 Windows 수신 메타데이터 일부는 CRLF이며 diff whitespace 경고가 있을 수 있다. hash는 원 bytes 기준이다. GitHub 원 job.log는 PC 비공개 수신 경로에 보존하고 이 PR에 편입하지 않는다. 허용 메타데이터·archive에 한정된 토큰/개인키 패턴 검사는 전체 비밀정보 부재의 보증이 아니다.

PUSH=NOT_EXECUTED / DEPLOY=NOT_EXECUTED / DELIVERY_GATE=NOT_VERIFIED. 독립 증적 리뷰·병합·운영 업무 포트 /metrics404 실측·배포 회귀·전체 AC 인수는 별도다. Harbor 자동기동은 타 세션 범위를 유지한다.
