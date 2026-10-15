# O01 AC07·Probe223 수행 원본 수신 편입

2026-10-15 KST · 수행 이재환(CLAUDE_ASSISTED), 수신·검수 이권욱 지원(CODEX_ASSISTED).

**편입 범위:** AC07 1차 원본6개와 AC07 정정 확인·Probe223 후속 원본13개, 이전 검토자의 수신/대조 기록이다. 수신·검수는 완료됐고 이 PR의 독립 편입 리뷰·병합은 별도다. 새 Runtime·전체 O01 인수·Critical 문서 결함0·DOC Freeze를 선언하지 않는다.

## 읽는 순서

1. [출처·파일별 SHA256](SOURCE_INDEX.json) → [AC07 수행 양식](received/ac07/O01_AC07_RESULT.md) → [후속 수행 양식](received/probe223/O01_PROBE223_RESULT.md).
2. 각 received 폴더의 원본 stdout/stderr/meta와 보조 스크립트를 확인한다. UTF-16LE·BOM·CRLF·빈 파일을 포함해 원본 바이트를 보존했다. 원본에 현재 승인 문구를 삽입하지 않았다.
3. [AC07 수신 기록](review/ac07/RECEIPT.json)·[기존 검수](review/ac07/VALIDATION.json), [Probe223 수신 기록](review/probe223/RECEIPT.json)·[기존 검수](review/probe223/VALIDATION.json)를 대조한다. helper-replay 출력은 검토자 PC의 이전 대조 결과이며 수행자의 추가 실적이 아니다.
4. 아래 정정·판정 경계와 [O01 대응표](O01_COVERAGE.md)를 읽는다. 원본의 대기 상태·결함 후보는 작성 시점 기록이다.

## 수행과 확인 범위

| 회차 | 확인된 기록 | 제한 |
|---|---|---|
| AC07 1차 | 수행 보고09:44:13~09:50:52, verifier09:49:24~25 rc0·stderr0 B. OFFLINE_CONSISTENCY=PASS, Manifest116·SSAR25(allow6/deny19)·GET2 | OS/Python/Git/HEAD/status는 양식 보고값. 별도 raw 환경·status 로그 미수신. 서버 SSAR/GET·토큰 발급 재실행 아님 |
| AC07 정정 확인 | 10:34:45~10:37:44, infra-cicd PR85 merge0b0412a2의 D1~D5 확인·남은 문제 없음 보고 | 브라우저 판독은 수행자 보고, AC07 verifier 재실행 없음 |
| Probe223 | 10:37:44~10:39:05, 고정43e26384·Manifest·Python·status 출력, verify10:39:05 rc0·stderr0 B, HTTP_PROBE_RUNTIME_PASS_WITH_RECORDED_OBSERVATION_LIMITS | 이재환은 기존 PR223·K8S86 리뷰 참여자. 이번은 재확인이며 신규 초견 실적·새 독립 승인 아님 |

검토자는 앞선 검수에서 Manifest116/108개·봉인117/109파일 불변을 대조하고 보조 탐색 스크립트 출력 일치를 확인했다. 이번 편입에서는 원본19개를 기존 RECEIPT 및 공유 경로와 다시 대조했다. 이번 저장소 편입 검사와 과거 오프라인 검수·원래 서버 Runtime의 시각을 구분한다.

## 원본 후보의 후속 처분

- D1 SSAR13↔25·D2 초기 PR61/실측 PR82·D3 증적 사본 상대 링크는 [PR85 병합본](https://github.com/321Team/infra-cicd/blob/0b0412a293dfb00fa1437d484ca012d1a4898412/docs/o01-ac07-reading-notes-20261015.md)에서 보완했다. D4 봉인 당시 대기 상태와 이후 승인·인수를 분리했고 D5 두 리뷰 사본 SHA256 동일성을 안내했다. 수행자 후속 양식에서 D1~D5 확인을 받았다.
- Probe223 시각 후보: receipt 종료09:52:03.669644 KST와 worker02 원 PID 종료 관측09:52:04.267843 KST의 표시값 차이는0.598199초다. 양식의 ‘ansible01 기록’은 조정 PC 측 receipt와 중계 ansible01을 구분해야 한다. 봉인 receipt의 Windows SSH 명령 및 [현존 로컬 transport 참고본](review/read_transport.reference.py)이 이 해석의 근거다. 참고본은 실행하지 않으며, 당시 동일 소스였음을 봉인 Manifest로 입증하지 못한다.
- 당시 양측 clock offset·동기화 상한·원인은 미확인이다. control01/edge01 chrony 기록을 조정 PC/worker02 오차 증거로 사용하지 않는다. ‘초 단위 오차 가능’을 허용 오차로 확정하지 않는다. 같은 worker02 hold의 wall81.785631초·monotonic 약81.785639초는 부합하고 기존 verifier는 receipt 종료와 worker 이벤트 선후를 비교하지 않는다. 전역 시각 순서·지연을 검증한 결과는 아니다.
- [PR177 시각 기준 보완](https://github.com/321Team/fds-project-baseline/blob/5e8756c2129d1fbbca8bc83b81ac285101c44f39/governance/handoffs/o01-ac07-correction-probe223-20261015/PROBE223_SESSION.md)을 따른다. 원본 시각·Manifest는 보정하지 않았다.
- AC07 양식의 자연 만료는 명목 만료 시각과 실제 만료 거부 관측을 구분한다. Probe223 원 출력의 PENDING/APP NOT_RUN/DB/W4는 당시 상태다. 해당 원본을 수정하거나 이 편입만으로 다른 AC의 현재 인수를 판정하지 않는다.

## 검증·보관·중단 기준

독립 검토 환경은 기존 evidence 저장소의 이 PR 고정 HEAD 로컬 checkout이다. Python3·Git으로 수신 원본19개와 SOURCE_INDEX/RECEIPT의 해시, 이 폴더 SHA256SUMS, 루트 REGISTRY 연결을 확인한다. 저장소 루트에서 `python -I -B tools/check-evidence-layout.py --base origin/main`을 사용한다. 정상 기준은 파일/Manifest/대장 일치, 경로 오류0, 기존 증적 변경·삭제0이다. 해시/입력 불일치 시 편입을 중단하고 새 수정 커밋으로 사유를 남긴다. 운영 파일·참고 transport·수집기는 실행하지 않는다. 원본을 고쳐 일치시키지 않는다.

기존 검수: [AC07 접수](https://github.com/321Team/fds-project-baseline/issues/24#issuecomment-6181949828), [후속 검수](https://github.com/321Team/fds-project-baseline/issues/24#issuecomment-6182570583). 이 수신 편입에는 공유폴더 ACL·수행자 PC 원격 조사·새 서버 접속·Secret 값·권한 변경이 포함되지 않는다.
