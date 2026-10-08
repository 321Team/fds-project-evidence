# Backup v2.1 fresh precheck + 격리 Runtime — 2026-10-08

## 승인·담당·범위

사용자가 “백업 프리체크 우리가 해주고 런타임도 하자”고 직접 지시했다.
GWONUK/CODEX_ASSISTED가 기존 ansible01→control01/svc_ansible+sudo/root 경로에서 실행했다.
기존 이하영 담당의 이번 1회 실행을 GWONUK 측으로 전환한 것으로, 다른 역할을 재배정하지 않는다.
[#19 한정 GO6041971580](https://github.com/321Team/fds-project-baseline/issues/19#issuecomment-6041971580):
01:15~01:45 KST 창, latest start01:25, fresh precheck 후 격리 Runtime1회, 자동 재시도 없음.

source #71 `1b5470e8c9902e7561dbe56fa9129bcf45ba7bb3` 전체 번들.
독립 APPROVED5444464361 및 exact-head CI SUCCESS 확인 후 미병합 후보의 격리 시험으로 실행했다.
코드 병합·운영 etcd 복원·AC 인수·Issue/Phase1 Close 완료가 아니다.

## 실제 결과

- control01 작업 폴더 `/root/sec19-backup-runtime.8w9vw8oS`.
- 새 precheck `p1-sec01-ac05-restore-precheck-20261007T161647Z.M63owL`, rc0/OK.
- Runtime `p1-sec01-ac05-restore-run-20261007T161647Z.mTDvTy`.
  **2026-10-08 01:16:47~51 KST**, rc0/ALL_STAGES_OBSERVED=yes/cleanup_failed=0.
- 원본과 복원본 snapshot status: **revision3287996 / keys620 / storageVersion3.6.0** 일치.
  원본 HASH48214e62, 복원본246cec98는 코드의 비판정 참고값으로 보존했다.
- 임시 etcd health 정상, header revision3287996, live key count620.
  Secret 집계 total7/secretbox7/not_secretbox0. 값은 pipe 안에서 집계하며 증적에 저장하지 않았다.
  encryption prefix 집계이며 Secret 복호화/애플리케이션 소비 성공을 주장하지 않는다.
- 임시 etcd는 별도 network/PID namespace의 loopback23790/23800으로 실행됐다.
  code 호출/내부 rc/namespace listener·host namespace 시험 포트 부재를 확인했다.
- exact test data-dir 프로세스 없음, 생성 작업 디렉터리 삭제 확인.
  운영 snapshot SHA `8ace820ca29488fc5ef8eb46d424a58ef6e0dbbba03f6d0f851f929e6e771e2f` 전후 동일,
  운영 listener 동일, 운영 endpoint health 사후 rc0.
- 전/시작직전/사후 노드6대 Ready를 원본에서 재검증했다. fds-app Pod와 EndpointSlice
  투영 기준선 전후 동일. 이 비교는 관측하지 않은 모든 서비스의 무중단을 보증하지 않는다.
- 시작 시 시험 script process/기존 restore work 항목 없음, 다른 알려진 작업은 코드/MOCK/리뷰
  준비 상태로 대조했다. 현재 실행의 전용 flock을 사용했으나 모든 외부 작업을 잠그지는 않는다.

## 원본·검증·한계

archive231파일. 코드 manifest17/17, 새 precheck60/60, run100/100 일치.
서버 내부 precheck/run tar의 sidecar와 원본 디렉터리 bytes도 대조했다.
서버 출력 completion EXIT_CODE=0·sealcheck 성공과 실행 결과를 함께 확인했다.
summary의 PROVISIONAL/SEAL_STATUS=PENDING 문자열만으로 최종 판정하지 않았다.

최상위 tar는 SSH stream 수신 bytes이며 sidecar는 로컬 수신 SHA다.
서버에 저장된 최상위 tar SHA라고 표현하지 않는다. runtime-wrapper.sh는 실제 실행 입력이며
고정 git archive를 내장한다. snapshot 원본·작업 DB·Secret 값·인증키는 archive에 넣지 않았다.
wrapper 원본에서 출력된 postcheck rc만 의존하지 않고 노드 Ready/기준선/각 raw rc를 재대조했다.

이번 fresh precheck는 실행 직전 확인이며, 앞선 증적#149의 00:41 precheck를 대체·삭제하지 않는다.
이번 성공은 이 고정 snapshot의 격리 복원/관측·정리 결과다. 운영 member 복원/DR 전환,
Secret 복호화, APP 정상 동작, AC-05 전체 인수로 확대하지 않는다. Probe는 실행하지 않았다.

**PRECHECK=PASS / ISOLATED_BACKUP_RUNTIME=PASS_WITH_SCOPE / CLEANUP=PASS / POSTCHECK=PASS**.
독립 증적 리뷰·병합·AC 인수는 별도다. 원본과 실패 이력은 모두 보존한다.
