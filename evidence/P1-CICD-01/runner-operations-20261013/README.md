# P1-CICD-01 — Runner 운영 반영과 과거 packet 정리

2026-10-13 KST. CODEX_ASSISTED. 사용자 이권욱의 후속 착수, 회차 실행자 담당·500분 유보 채택 및 정확한28개 파일 삭제 허용에 따른 실제 기록이다.

## PR81·증적209 병합 후 운영 반영 — 2026-10-13 KST

@supreme33-kr 사용자 이권욱의 후속 착수와 운영 입력 확정에 따라 아래까지 수행했습니다. **제2운영자 공급·인증·회수 실습 요건은 충족, 알림 설정은 활성화, 전체 O02와 #61은 실제 알림 수신 및 기존 잔여 확인 전까지 OPEN**입니다. 같은 실습·완료 CI를 다시 요구하지 않습니다.

### 1. 제2운영자 실습 반영

- [본인 수행 회신](https://github.com/321Team/infra-ansible/issues/61#issuecomment-6136928532)과 Run38330170015/Attempt1/Job115077894860, source `874dc8bb052cfe3295fb79038872c785bbcc2592`, Runner63, 시각·archive·정리 결과를 대조했습니다.
- 이재환 직접 로그인·sudo·A/B helper 실행·serve 관측·정상 정리와 본인 PC 원본 수신은 실습 근거로 수용합니다. 이권욱/Codex의 준비·helper·증적 대조 지원 및 실제 발생하지 않은 복구 인수는 구분합니다.
- [PR81](https://github.com/321Team/infra-ansible/pull/81) merge `ec15dcbd022942add199a8f4718c0f88105e880e`, [증적209](https://github.com/321Team/fds-project-evidence/pull/209) merge `ee6c295ae6445f1b96876bf50c92b8c61d15812d`. 증적209 승인은 편입 범위이며 전체 O02 인수 승인으로 확대하지 않습니다.

### 2. 확정된 알림 운영과 실제 적용

- 수신자 `supreme33-kr,GWONUK`, 장기 대기 기준10분, 기존 schedule 매일 KST09:07~23:37/30분 간격.
- 이재환 점심·근무 외에 실제 Ansible 작업을 하면 **해당 회차 실행자가 수동 queue-watch·감시 실패 확인·기존 팀 카카오톡 전달을 맡습니다.** 회차 시작 시 실행자를 기록합니다. 작업이 없는 시간의 상시 당직을 신설하지 않습니다. 카카오톡 자동 전송을 구현한 것은 아닙니다.
- 사전검증 [Run38339279651](https://github.com/321Team/infra-ansible/actions/runs/38339279651), merged main `ec15dcbd...`, Job115106404173 `dry-read SUCCESS`(11:56:21~11:56:33 KST), notify Job `SKIPPED`. 관측 `NO_ALERT / DRY_RUN_NO_COMMENT`, 활성 Run0. artifact11786755671 ZIP SHA256 `814a78e7f16fc00385cee3a930ea22eadd9c556f08659a326d0df5324f1814db`와 내부 JSON/sidecar 대조 완료.
- **11:59:08 KST `ANSIBLE_QUEUE_ALERT_ENABLED=true` 적용·읽기 대조 완료.** 기존 CI 변수·조직 비용 설정·Runner·서버 정책은 변경하지 않았습니다. 아직 실제 장기 대기 알림 게시와 사람의 수신 확인은 없으며 다음 업무상 필요한 Job에 연결합니다. 야간 schedule 공백·지연/누락은 기존 런북의 한계로 유지합니다.

### 3. 비용 기준

11:50:08 KST Actions Billing은 Linux803분, 순 청구0달러. Free 조직2,000분에서 계산상1,197분 잔여이며 사용자가 **다른 CI500분 유보**를 채택했습니다. 이후 실행·다른 저장소 사용과 보고 지연을 반영해야 합니다. 조직의 Actions0달러·추가 사용 차단 설정은 유지하며500분을 자동 강제하는 기능은 아닙니다.

일일 운영 점검과 새 대량 CI 시작 전 잔여량에서500분·다음 확인 전 계획된 CI/감시 사용량·보고 지연 여유를 빼고, 여유를 확인하지 못하면 알림부터 false로 중지해 기존 수동 관측으로 전환합니다. 실제 Job이1분을 넘으면14일420분 예측을 넘길 수 있습니다. 현 자원 회수기간10/26 종료 시 중지·원본 보관 확인도 남깁니다(workflow 자동 만료 없음).

### 4. 과거 packet28개 정리 완료

사용자가28개 미사용·동시 변경 및 token 발급/전달 배제·정확한 파일 삭제를 허용했습니다. ansible01 UID1000, 같은 host/boot, 정확한28개 경로의 inode/device/size/mtime/ctime/owner/mode/link를 대조했습니다. MOCK7건·실제 읽기 전용 대조를 통과했고, 실행 직전 활성 regression0/등록Runner0/컨테이너0/runner.py 없음 확인 뒤 **12:03:52 KST까지28개만 삭제 및 독립 사후 부재 확인**했습니다.

비밀 내용·token값/hash를 읽거나 복사하지 않았고 새 token 발급·재공급은 없습니다. 파일 삭제와 서버측 credential 만료·폐기는 다른 판정이며 개별 token 만료를 검증했다고 주장하지 않습니다. CI81에서 이미 삭제된 관리자 packet의 정확 경로를 사후 복원한 것도 아닙니다. 다음 실제 공급 helper에 삭제 경로·사후 부재 기록을 남기는 비차단 보완은 유지합니다.

### 남은 완료조건

1. 다음 실제 업무의 장기 대기에서 감시 Run/댓글 → 담당 수신 시각·회신 → queue-watch 판단 → 필요한 공급/CI/정리 연결. 알림을 만들기 위한 완료 Job 재실행 없음.
2. 그 증적 검토 후 O02의 알림 부분 및 #61 잔여 AC 판정. C01 실효 공유/NTFS 권한 등 별도 미확인 사항을 이번 결과로 완료 처리하지 않음.
3. 운영 중 사용량 확인·500분 유보 중단 기준·종료 시 알림 중지와 원본 보관 인계.

새 공통 Lead GO·Phase2 조건을 추가하지 않았습니다. CODEX_ASSISTED.


## 증적 범위·검증

- 이전 CI81 원본/본인 수행 회신은 병합된 증적209를 참조하며 이 묶음은11:50 이후 운영 반영의 추가 원본이다. 기존 sealed 경로·AC 정본·예외 목록은 변경하지 않는다.
- 사전검증 Actions 원본 ZIP은 재압축하지 않았다. API digest·내부 JSON sidecar와 대조했다. dry-read SUCCESS와 notify SKIPPED를 분리한다. 활성화 후 schedule 성공과 실제 댓글 게시·사람 수신은 이 묶음에서 아직 검증하지 않았다.
- STATIC: 삭제 helper 구문. MOCK: 정상 읽기·정확 대상 삭제·뒤쪽 대상 불일치시 전체 중단·symlink/hardlink 거부·unlink 직전 변경 중단·부분 오류 영수증7건. 합성 삭제 수는 실제 서버 삭제가 아니다.
- RUNTIME: 같은28개에 대한 실제 lstat 대조·비삭제 실행·사용자 허용 뒤 삭제·독립 사후 부재 확인. 경로별 stdout/rc/시각과 metadata collector·실행 source를 결속한다. 원격 stdin 입력은 token이 아닌 메타데이터다.
- 실행 source의 SHA는 로컬 Python에서 `read_text()` 후 전달한 LF UTF-8 바이트 기준이다. Windows 로컬 원파일의 CRLF 해시와 혼동하지 않는다.
- GitHub Billing과 variables 원본은 비밀 API가 아니다. PAT·등록 token·token파일 내용/hash는 수집하지 않았다. 값 형식으로 보이는 비밀패턴을 한정 검사하고, 이를 모든 민감정보 부재 보장으로 확대하지 않는다.
- 과거 packet 삭제는 파일 위생 정리다. 서버측 개별 token 만료/폐기를 판정하지 않는다. CI81의 삭제된 관리자 packet exact 경로 누락도 사후 복원하지 않는다.
- 새 Runner·credential·Job 재실행·운영 playbook·Harbor/Phase2 작업 없음. 독립 증적 REVIEW·MERGE 대기이며 이번 게시로 전체O02/#61을 닫지 않는다.
- 현재500분 유보는 수동 운영 중단 기준이다. 사용자 입력만으로 자동 예산 차단이 구현됐다고 하지 않는다. 자동 날짜 만료도 없다.

각 원본 수집 시각은 `*.receipt.json`과 결과 JSON에 있다. GitHub 원본14일 보존과 운영 증적 보관 인수를 구분한다. 기존 회수기간10/26까지 보관 기준을 이어가되 원본 자동 삭제를 지시하지 않는다.
