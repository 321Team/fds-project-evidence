# 역할185 격리 실행·회수 증적 — 새 수집회차 후보

책임 티켓: [infra-ansible #9](https://github.com/321Team/infra-ansible/issues/9), Record ID P1-ANS-01.

**증적 편입용 Draft 후보이며, 이 문서 작성 시점에는 증적 GitHub 게시·독립 리뷰·병합·최종 인수를 하지 않았다. 원본 archive의 공유 보관 URI와 중앙 복사 결과를 연결했으며, 개별 reviewer의 실제 읽기는 PENDING이다.** 기존 회차 원본은 바꾸지 않았다.

## 현재 판정

2026-10-16 17:09:25.953~17:13:51.387 KST, cicd-runner01의 ansible-verify 격리 컨테이너에서 고정7묶음 **185/185 PASS, FAIL0, SKIP0**. source `affaad6b1a31d680164d9e3d5ef5d2a9d3fce95a`, tree `2563bcea5ceee3543451e96ac76011ef05e486bf`, session `p1-role-cc7e9fc7dd9049a4`.

MON2.16.19/2.21.3 각45, NTP legacy48/flow25/serial1/transport2/wrapper19다. 준비11명령은 사례 수에 합산하지 않는다. create/start/rm 각1 rc0, stop/force0. 17:17:55.927 KST 사후 읽기에서 동일 저장소 정확 CID 부재·실행기0·읽기 오류0을 확인했다. 상세: [기존 최종 판정](derived/runtime/FINAL_RESULT.json), [기존 원본 대조](derived/runtime/EVIDENCE_AUDIT.json).

이 결과는 Linux 격리 localhost/files/parser의 실제 실행과 모의 서비스 관측 범위다. 운영 MON/NTP 서비스·외부 네트워크/시간·운영 엔진 전환·GitHub CI·전체 #9 AC 인수가 아니다. NTP legacy/wrapper의 기존 기록 형식을 MON 명령 영수증 형식과 같다고 주장하지 않는다.

## 자료 구분과 원본 보존

- `originals/server/`: 수집한 서버 원본의 선택 사본. `kit/`는 당시 실행 소스·입력의 보존 사본이며 새 운영 배포 코드가 아니다. `__COLLECTION_READ_RECEIPT__.json`만 수집기 파생 기록이다.
- `originals/operator/`: 사용자 TTY에서 수집한 출력12개 원본 사본.
- `derived/runtime/`: 기존 실행 판정·원본 대조·수집·회수/사후조회 기록. 당시 상대경로는 당시 원본 폴더 기준으로 보존했다. 이 디렉터리의 과거 FINAL_BINDING은 이번 편입 목록이 아니다.
- `pre-runtime-history/`: F1/F2 수정·표적 STATIC/MOCK 이력. 당시 미실행/대기 상태를 사후 편집하지 않았다. 현재 실제 결과는 위 최종 판정으로 구분한다.
- `executed-source-external/stage_supply.py`: 공급물 밖의 당시 staging 코드 사본. 운영 설치·새 실행 허용 대상이 아니다.
- `prior-failure/`: 08:50 회차의 실패·정확 회수 원본/기존 판정. 당시 source32f8d21, tarf019e7ea에서 첫 MON 실패로185 미충족이었으며 이력을 PASS로 고치지 않는다.
- [선택 사본 목록](PUBLICATION_COPY_MAP.json): source 경로·바이트·SHA·자료 종류와 제외 사유. 모든 원본3446개+수집 파생1개를 Git에 모두 넣었다고 주장하지 않는다. Git 객체DB·binary/wheel/cache 및 비UTF8 바이트는 원래 archive에 보존했다.
- [대용량 원본 위치](ARCHIVE_LOCATIONS.json): 21:07:08~21:07:12 KST 중앙 단회 복사의 정확 UNC와 원본3개·hash4개 길이/SHA를 연결했다. 7파일 총107,950,706B, 오류/삭제/덮어쓰기/재시도0이며 source_changed=false다. 기존 원본을 재압축·편집·삭제하지 않았고 Git archive 추가·Release 업로드도 없다. 접근은 사용자 승인인원 한정 확답(USER_ATTESTED), 기술 실효 ACL은 NOT_VERIFIED, reviewer 실제 읽기는 PENDING_AFTER_COPY다. 보존은 프로젝트 종료일까지이며 10/26·10/28 중 날짜는 미확정, 자동 삭제·연장은 허용하지 않는다.
- [공유 보관 실행 결과](storage-transfer/stdout.json), [실행 영수증](storage-transfer/RECEIPT.json), [중앙 대조](storage-transfer/CENTRAL_VERIFICATION.json), [사용자 결정 기록](storage-transfer/STORAGE_USER_DECISION.json)은 완료된 복사에서 나온 원본 사본이다. 이 연결 작업에서 공유 읽기·복사·해시 대조를 재실행하지 않았다. 기존 PUBLICATION_COPY_MAP은 당시3337개 선택 사본 목록으로 보존하고, 이번 추가4개 원본은 ARCHIVE_LOCATIONS의 출처/해시와 갱신 SHA256SUMS로 결속한다.

이번 `SHA256SUMS`는 이 새 수집회차에 실제 편입되는 파일만 포괄한다. 내부의 과거 manifest는 원래 수집 범위를 그대로 가리키므로 전체 archive 또는 PUBLICATION_COPY_MAP과 함께 해석한다. 복사 시 기존 receipt의 기대 hash와 바이트를 대조했으며 시험을 다시 실행하지 않았다.

## 기존 실패와 수정의 추적

08:50 실패는 읽기 전용 rootfs에서 fixture의 기본 `~/.ansible/tmp` 사용 및 부분 결과 보존 부족이다. 격리 통제를 완화하지 않고 fixture5파일의 전용 tmp/cfg·실제 모듈 preflight·하위 rc/원시 출력/부분 집계 보존을 수정했다. 완료 회차의 cfg77개·tmp154개0700·MON명령 영수증80개는 기존 감사 결과로 연결한다. 로컬 감사에서 NTP observed_sha256의 비교 대상을 잘못 잡았다가 바로잡은 이력도 `derived/runtime/audit-local-corrections/`에 보존했다. 원본과 서버 실행은 바꾸지 않았다.

## 편입 완료조건

원본 archive의 허용 보관 URI·사용자 접근/보존 조건·중앙 배치 후 hash 대조는 연결됐다. 개별 reviewer의 실제 파일 읽기와 민감정보·원본 출처·해시·실행 판정·AC 대응에 대한 기존 증적 저장소 독립 리뷰는 아직 미완료다. 사용자 접근 확답·중앙 기술 대조를 독립 사람 승인으로 표시하지 않는다. 1MB 초과 archive는 Git에 넣지 않는다. 현장·정책·Phase2 변경은 없다. PR 병합은 #9 종결 또는 운영 전환을 자동 의미하지 않는다.

## PR87 실제 병합·CI·회수 후속 연결 — 2026-10-17

[infra-ansible PR87](https://github.com/321Team/infra-ansible/pull/87)은 10/16 23:33:30 KST에 merge `b3557dfb7691b9904bd84701da70f14b4ee0d485`로 병합됐다. 코드 HEAD `625731f3d45c21b4e0b0f1e328cc9800dd953fff`의 tree `2563bcea5ceee3543451e96ac76011ef05e486bf`는 위 역할185 실행 source와 동일하다. 과거 준비 문서의 OPEN/CI 대기는 당시 이력으로 보존한다. 10/17 06:19 KST GitHub 읽기에서 실제 병합을 재확인했다.

[CI38887094714](https://github.com/321Team/infra-ansible/actions/runs/38887094714) attempt1/job116927361826은 실제 job 23:23:22~23:31:58 KST에 unit295 PASS·skip0, core2.16.19/2.21.3 syntax 각39, fixture7단계 rc0을 기록했다. workflow의 앞선 run_started_at은 큐 대기 시각이며 실제 job 시작과 구분한다. 역할185 전체 재실행이나 운영 적용 결과가 아니다. [CI 원본 결과](pr87/ci-original-entries/CI_RESULT.json), [unit 원본 출력](pr87/ci-original-entries/unit-tests.stderr.log), [job 원본](pr87/job-final.json)을 연결했다.

23:32:54.596227 KST 회수 관측에서 해당 등록 Runner·컨테이너·Runner 프로세스·양쪽 packet 파일 잔여0을 확인했다. 서버 측 token 철회는 주장하지 않는다. [완료 기록](pr87/COMPLETION.json), [회수 관측](pr87/CLEANUP_OBSERVATION.json), [실제 병합 대조](pr87/merge-verification/MERGED_RESULT.json), [선택 사본 출처/해시](pr87/SOURCE_MAP.json)를 참조한다. 이번 연결에서 시험·CI·서버 조회·archive 재검증은 수행하지 않았다.

새 CI ZIP(515,688B, SHA `f8e3498a280120ad9faa3ef83d7602a1409dc710899a603c9e8533ef18496781`)과 host tar.gz(6,353B, SHA `af591a28d94966dd425ba2f3fb6d0e6d84312c7360f13dad86b98c3b03e35203`)는 기존 로컬 원본을 보존 중이다. **이 두 파일의 공유 보관 인계는 미완료**이며 위 기존7파일 receipt에 포함되지 않는다. GitHub artifact12052452535의 만료는 10/23 19:25:07 KST로 프로젝트 종료 보존을 대신하지 않는다. [PR87 연결·보관 구분](pr87/PR87_LINKAGE.json)을 참조한다. 원본 ZIP/tar를 이 PR에 추가하거나 재압축하지 않았다.

PR87 코드 리뷰를 이 증적 PR의 독립 리뷰로 재사용하지 않는다. 증적 reviewer 원본 읽기·독립 심사는 PENDING이다. 운영 엔진 전환·역할별 실제 apply/rollback·6대 비교·#9 전체 인수는 미완료로 유지한다. 기존7파일 공유와 새 CI 원본 보관의 상태를 구분한 Draft 게시 준비이며, Harbor 진행 여부를 게시 선행조건으로 추가하지 않는다.
