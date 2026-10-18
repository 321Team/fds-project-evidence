# Ansible #9 — 실제 엔진 선택·복귀와 NTP precheck 증적

CODEX_ASSISTED · 2026-10-18 KST · Record ID P1-ANS-01.
**로컬 통합 발행 후보이며 이 자료의 Git 게시·독립 리뷰·병합은 미실행이다.** 중앙의 [실행 결과 댓글](https://github.com/321Team/infra-ansible/issues/9#issuecomment-6249035973)과 원문 증적의 저장소 편입은 구분한다.

## 두 회차와 실제 판정

| 회차 | 실제 결과 | 한계 |
|---|---|---|
| 19:27:45~55 legacy | 후보2.21.3 CLI4 rc0, precheck rc2, 기본2.16.19 복귀 CLI4 rc0, 소유 tmp/cp 정리 | 6대 모두 legacy include guard에서 중단. precheck PASS 아님 |
| 19:56:33~54 paired | 기존 paired precheck1회 rc0, 6대 changed0/unreachable0/failed0, migrated/would_change=false | 새 migration/apply/전역 엔진 전환·#9 전체 인수 아님 |

두 회차 모두 source `0d58598d8a3ce77ccd7eaa9e1dfba820b0a436ea`와 기존 후보 venv를 사용한다. 첫 실패 뒤 실제 schema2 paired 형식 및 기존 승인 upstream을 입력에 결합했다. guard·helper·role·운영 설정을 수정하지 않았다. 과거 실패 원문은 그대로 남겼다.

paired control01은 ok23, 나머지5대는 ok22다. tracking 형식/유한값/Leap Normal, chronyd active를 실제 확인했다. node verdict의 kubelet도 loaded/active이며 Kubernetes Ready 검증으로 확대하지 않는다. main/drop-in/schema2 baseline18파일의 전후 SHA·owner/mode/크기, source11파일 및 runtime-vars가 일치한다.

이번 precheck에서 100ms·client source·source upstream 집합 assert는 조건상 생략됐다. 저장된 단일 관측값은 기대와 부합하지만 60초×6·reboot·sync-loss 또는 해당 별도 AC 전체 합격이 아니다. 설정을 적용하지 않아 원격 baseline 복원은 하지 않았다. parser/Ansible 전달 임시 파일과 controller 증적 쓰기는 있었으며 “모든 쓰기0”이라고 표현하지 않는다.

## 편입 목록과 출처

- `originals/legacy/`: 19:27 회차의 보호 원본37파일. 후보/복귀 CLI 출력·경로·rc와 실패 로그 포함.
- `originals/paired/`: 19:56 회차의 보호 원본64파일. 전후6대 파일 해시/신원, plan/node verdict/recap, source/runtime-vars, claim·정리 포함.
- `provenance/`: 각 중앙 실행 intent/result 및 1회 원본 회수 claim/receipt/index. 이 기록을 서버의 업무 결과와 구분한다.
- `inputs/`: 실제 실행에 결합된 기존 입력 bytes. 과거 작성 시점의 후보/미실행 문구는 바꾸지 않았으며 실제 수행 상태는 위 두 회차 원본을 따른다.
- `executed-source/`: 당시 실행한 호출 스크립트 보존본. **재실행용 실행 허용이나 새 운영 도구가 아니다.** 기존 root/claim과 시간·boot 전제는 그 회차에만 적용된다.
- `analysis/`: 기술 판독 파생 JSON. 사람 독립 승인/최종 인수가 아니다. 당시 로컬 상대경로를 유지했으며 이 후보의 실제 파일 대응은 `PUBLICATION_COPY_MAP.json`에서 확인한다.
- `PUBLICATION_COPY_MAP.json`: 원본 경로·종류·크기·SHA와 선택/제외 범위.
- `SHA256SUMS`: 이 수집회차에 포함되는 파일의 SHA. 해시 일치는 바이트 무결성이며 시험 PASS나 담당자 수령의 대체가 아니다.

원본101파일의 합계는90,964bytes이다. base64 전송 envelope는 같은 원문을 중복하므로 편입하지 않았고 회수 영수증의 envelope SHA는 보존했다. root baseline 본문·키·token·비밀번호는 포함하지 않는다. 사용자·호스트·내부 경로는 실행 추적용 메타데이터다.

정확 입력 SHA는 `ad2ef8749403de92bda060f9d51f1fb65862d842ab87be60f826fe0490dad6f4`이며 `originals/paired/runtime-vars.json`과 같다. 그 입력이 참조하는 paired binding SHA는 `3caeca53b268e76b351f6514a490b690618782ca1f059715d472433a6ce17b48`이다. 실행 스크립트 SHA는 legacy `1ff51e28ceae6358fcda63bb7da3706ccb0e46bc2d640b3fed0f43b3b28ffeb3`, paired `9f9b0ca55eafa22571a6134757eeb326568e689dda46030134b550e5b4996697`이다.

## 기존 완료 증적과 최종 잔여

[PR243](https://github.com/321Team/fds-project-evidence/pull/243)의 역할185·PR87 CI295/구문78/fixture7·회수 원본은 **재포장·복사·재시험하지 않았다.** [병합된 고정 회차](https://github.com/321Team/fds-project-evidence/tree/417dbdec9f0dade9260f95c3894c7df6bc519722/evidence/P1-ANS-01/infra-ansible-issue-9-role185-20261016)를 재사용한다. worker02 DNS 실제 회차·기존 MON verify·공개 CLI/Gate0 결과도 기존 각각의 범위에서 유지한다.

소유 controller tmp/cp는 두 회차 모두 정리 및 회수 시 부재 확인. 기존 lock·입력·증적은 보존하며 대상 서버의 모든 원격 임시 파일 부재를 주장하지 않는다. 이번 선택은 child-only이며 기본 엔진·기존 운영 checkout을 바꾸지 않았다.

남은 것은 기존 공유17 담당자 직접 열람 회신, 기존 AC에 대한 실제 caller/Collection/6대 전환 시점 증적의 최종 연결 및 범위를 명시한 운영 인수다. 생략된 NTP assert를 실행했다고 쓰거나 185 격리 시험을 운영 전체 apply로 바꾸지 않는다. 정상 서비스 변경을 위한 시험·새 공통 Lead GO·Phase2 작업은 추가하지 않는다.

중앙이 다른 완료 결과와 통합 발행할 때 새 수집회차와 registry 한 줄만 편입한다. 기존185/PR243·다른 회차·sources/sealed는 변경하지 않는다. 이 후보의 검토·게시가 완료되기 전에는 PUBLICATION=COMPLETE로 표시하지 않는다.
