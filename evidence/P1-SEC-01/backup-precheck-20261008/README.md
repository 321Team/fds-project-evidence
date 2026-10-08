# Backup v2.1 fresh precheck — 2026-10-08 00:41 KST

baseline #19 [수집 착수](https://github.com/321Team/fds-project-baseline/issues/19#issuecomment-6041322079).
사용자가 IF-06B 정책 수집과 Backup #71 다음 사전검증을 모두 직접 진행하도록 요청했다.
GWONUK / CODEX_ASSISTED. 이 폴더는 기존 evidence #146의 프로그램 버전 수집 이후 별도 1회 precheck이다.

## 실행·관측

- 코드: infra-kubernetes #71 `1b5470e8c9902e7561dbe56fa9129bcf45ba7bb3`.
  실행 전 독립 APPROVED 5444464361와 exact-head CI SUCCESS 확인. 미병합 후보의 고정 전체 번들을 사용.
- 경로: PC → ansible01/server01_ansible → control01/svc_ansible + 기존 sudo/root.
  기존 키·StrictHostKeyChecking 유지. 새 계정/권한/설정 변경 없음.
- 서버 작업 폴더: `/root/sec19-backup-precheck.fhEI3gT9`.
- 결과: `p1-sec01-ac05-restore-precheck-20261007T154101Z.LAIzk6`.
- 시작 2026-10-07T15:41:01Z, 종료 15:41:02Z (KST 10/8 00:41:01~02).
  단조 정수 초 elapsed=0은 원문 그대로이며 UTC timestamp와 함께 해석한다.
- **precheck rc0 / PRECHECK_RESULT=OK**, SSH wrapper/수신 rc0.
- 전후 정확한 6노드 Ready. snapshot root:600 및 고정 SHA 일치.
  etcd/etcdutl/etcdctl 모두 3.6.8, 고정 hash/운영 exe 일치.
  endpoint health rc0, 시험 포트 미사용, 운영 listener와 도구 가용성 확인.
- 원본 etcd health 문구는 `successfully committed proposal`이다. health 조회를 수행했지만
  snapshot restore·임시 etcd 기동·애플리케이션 데이터 변경 명령은 실행하지 않았다.
- storageVersion=3.6.0은 precheck의 **기대값 기록**이다. 이번에 snapshot status를
  실행해 저장 형식을 다시 관측한 것이 아니다. 실제 status/복원본 비교는 run 단계 잔여다.

## 증적·무결성

archive 97개 일반 파일(코드·전달 source.tar·노드 조회·precheck 결과·내부 tar/sidecar 포함).
코드 SHA256SUMS 17/17, 결과 SHA256SUMS 60/60을 수신 bytes로 대조했다.
서버가 만든 precheck 결과 tar와 디렉터리가 함께 있다. 최상위 전달 tar는 SSH stream을
그대로 수신한 파일이며 sidecar는 **로컬 수신 SHA**이다. 서버 저장 최상위 tar hash라고 주장하지 않는다.
wrapper는 실제 전송 입력이며 embedded source.tar는 고정 git archive이다.
snapshot/Secret/인증키 내용은 수집하지 않았다. SHA 일치와 precheck 판정은 구분한다.

## 상태·후속

BACKUP_PRECHECK=PASS / RESTORE_RUNTIME=NOT_RUN / STORAGE_STATUS_LIVE=NOT_RUN.
이 결과만으로 Backup RUN GO·AC-05 인수·#19/Phase1 Close를 승인하지 않는다.
현장 시험 담당 이하영 유지. 다음 RUN은 고정 SHA/번들, precheck 경로, fresh gate,
별도 비중첩 실행창과 복구 조건을 결속해 판단한다. Probe는 기존 d6866187 전체 번들을 유지한다.
IF-06B 원본은 별도 SSH 인증 차단으로 아직 미수집이며 이 archive에 포함됐다고 표시하지 않는다.
