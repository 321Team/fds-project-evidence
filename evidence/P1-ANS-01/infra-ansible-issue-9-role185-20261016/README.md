# 역할185 격리 실행·회수 증적 — 새 수집회차 후보

책임 티켓: [infra-ansible #9](https://github.com/321Team/infra-ansible/issues/9), Record ID P1-ANS-01.

**로컬 증적 편입 후보다. 아직 GitHub 게시·독립 리뷰·병합·최종 인수를 하지 않았다. 원본 archive의 팀 접근 URI도 미확정이다.** 기존 회차 원본은 바꾸지 않았다.

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
- [대용량 원본 위치](ARCHIVE_LOCATIONS.json): 완료 회차48,148,480B·공급29,132,800B·이전 실패 원본의 SHA와 로컬 위치를 연결했다. **storage_uri=null은 미확정**이다. 공유 경로 제안은 실제 배치·권한 검증 또는 새 예외 승인이 아니다. 원본 재압축·Git 직접 추가·Release 업로드를 하지 않았다.

이번 `SHA256SUMS`는 이 새 수집회차에 실제 편입되는 파일만 포괄한다. 내부의 과거 manifest는 원래 수집 범위를 그대로 가리키므로 전체 archive 또는 PUBLICATION_COPY_MAP과 함께 해석한다. 복사 시 기존 receipt의 기대 hash와 바이트를 대조했으며 시험을 다시 실행하지 않았다.

## 기존 실패와 수정의 추적

08:50 실패는 읽기 전용 rootfs에서 fixture의 기본 `~/.ansible/tmp` 사용 및 부분 결과 보존 부족이다. 격리 통제를 완화하지 않고 fixture5파일의 전용 tmp/cfg·실제 모듈 preflight·하위 rc/원시 출력/부분 집계 보존을 수정했다. 완료 회차의 cfg77개·tmp154개0700·MON명령 영수증80개는 기존 감사 결과로 연결한다. 로컬 감사에서 NTP observed_sha256의 비교 대상을 잘못 잡았다가 바로잡은 이력도 `derived/runtime/audit-local-corrections/`에 보존했다. 원본과 서버 실행은 바꾸지 않았다.

## 편입 완료조건

원본 archive의 허용 보관 URI·팀 접근/보존 조건과 실제 배치 후 hash 대조를 연결하고, 민감정보·원본 출처·해시·실행 판정·AC 대응에 대한 기존 증적 저장소 독립 리뷰를 받는다. 1MB 초과 archive는 Git에 넣지 않는다. 현장·정책·Phase2 변경은 없다. PR 병합은 #9 종결 또는 운영 전환을 자동 의미하지 않는다.
