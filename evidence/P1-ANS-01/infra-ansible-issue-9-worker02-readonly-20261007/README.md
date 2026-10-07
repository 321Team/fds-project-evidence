# Issue9 worker02 — 키 복원 읽기 사전검증 원본

CODEX_ASSISTED. 책임: https://github.com/321Team/infra-ansible/issues/9.

사용자가 2026-10-07 19:14:10 KST 기존 worker02 콘솔에서 server06의 sudo/root로 실행했다. Codex는 실행 전 번들 배치/해시/구문 확인, 실행 후 기존 svc_ansible SSH와 읽기 전용 sudo cat으로 증적 압축본과 sidecar를 회수했다. 새 SSH 경로·키·권한을 만들지 않았다.

## 소스와 실행 연결

- source: `ef5adb773ff696a60bd5a055a35c7a40c4c4b2ec` ([PR72](https://github.com/321Team/infra-ansible/pull/72)).
- 독립 코드 승인: [이재환 review5440695498](https://github.com/321Team/infra-ansible/pull/72#pullrequestreview-5440695498). 이 승인은 코드 병합용이고 운영 GO가 아니다. 이번 읽기 실행은 사용자의 권장안 착수 지시 및 실제 콘솔 실행에 따른다.
- CI: Run37601736031 / Job112727478104 SUCCESS. 이를 field 결과로 전용하지 않았다.
- inspector SHA256: `affa67f1509c62f08270f33e266291f014dbcd717f10ea6e42a372700d594727`.
- 전달 번들 SHA256: `9f8bbc2321e71c8f3313d2f022b34953328c3ff5fc31fca3cc049814fe3d2746`. root의 새 폴더로 복사 후 archive hash와 루트 SHA256SUMS 5항목, source manifest3항목을 검증했다. 리뷰의 manifest 이름/상대경로 메모는 이 실제 검증으로 해소했다.
- 실제 도구 명령: `python3.12 -I -B tools/inspect-worker02-key-recovery.py --read-only`. 호스트/UID0/Python3.12.14/시각/명령/source는 original/context.txt. wrapper는 collection 전용이며 승인된 inspector의 원본을 수정하지 않는다.

## 관측과 판정

`RC=0`, `UNCHANGED_NO_RESTORE_NEEDED`, destination_drift=[]다. backup/target 모두 SHA256 b7923e8c646b7a7dd2ccba1ac48ddf02d264780db9100317644dcf87216cc834, uid/gid1001:1001,0600,unconfined_u:object_r:ssh_home_t:s0,정규 single-link132bytes로 관측됐다. 기존 receipt의 목적지 값에서 추정한 것이 아니라 양쪽을 각각 실제 읽었다.

실제 Linux FD·getxattr·SELinux Enforcing·고정경로/부모 검사 및 두 snapshot이 이 회차에 통과했다. 이는 모든 거부/경쟁 조건의 현장 재시험이 아니다. 백업 dev64768과 대상 dev64770은 다르므로 미래 복원안에서는 목적지 파일시스템의 stage·교체 조건을 따로 검토해야 한다.

현재 관측 기준 복원 불필요. 키/권한/SELinux 설정은 변경하지 않았다. restore_ready=false, runtime_go=false, concurrent_writer_exclusion=NOT_ESTABLISHED. 실제 쓰기 복원·fresh SSH·새 wrapper Runtime·운영 엔진 전환·Issue9 전체 AC/종결은 미완료다. 읽기 atime 및 새 증적 폴더 생성은 설정 변경과 구분한다.

## 원본 보존과 검증

서버 원본: `/root/issue9-preflight.FnHrLRwn/worker02-readonly-evidence.tar.gz`.
원래 압축 바이트를 재압축하지 않고 같은 이름 sidecar와 함께 보존했다. SHA256 `fb7802859fe45e2c49fac945272ff27e604f695ac5b8f4e946f195ec54c0cdb6` 일치, 내부 manifest6/6 일치. original/ 7파일(내부 manifest 포함)은 압축 원본에서 바이트 그대로 복사했다. 빈 stderr도 원본으로 보존한다. 키 내용·개인키·토큰·암호는 포함하지 않는다.

폴더 SHA256SUMS는 편입 시 작성한 목록이며 원본 original/SHA256SUMS와 구분한다. 압축 내부 파일 목록은 registry/ARCHIVE_CONTENTS.json에 등록한다. VERIFIED_FIELD_RESULT.json은 수신 검증 결과, STAGING_RECEIPT.json은 실행 전 배치 기록(FIELD NOT_RUN 당시 상태)이다. 과거 상태를 사후 덮어쓰지 않았다.

다음: 독립 증적 편입 검토. 정상 키를 시험 목적으로 변경하거나 이번 읽기를 반복하지 않는다. 검토된 새 wrapper Runtime 및 운영 전환은 별도 실행 조건/승인에 따른다. 이 PR은 이슈 종결·서버 변경·코드 승인·병합을 요청하지 않는다.
