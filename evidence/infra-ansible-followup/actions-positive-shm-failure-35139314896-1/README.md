# 격리 Actions 정상 시험1차 — 환경 실패와 수정

[Run35139314896 / Attempt1](https://github.com/321Team/infra-ansible/actions/runs/35139314896)은
2026-09-16T19:39:08Z~19:40:20Z에 Runner ID4에서 실제 Job을 수행했고 failure로 종료했다.
이전 queued 기록은 실행 전 상태이며 현재는 완료/실패다.

## 판정

| 항목 | 확인 결과 |
|---|---|
| 입력·artifact 무결성 | 서버 외부/내부 manifest, artifact ZIP digest·396행, fixture231행 일치 |
| 호스트·격리 | 전용비sudo계정·SELinux Enforcing·rootless, 격리14개 true |
| 실제 실행 | exact checkout 성공, 두 엔진32개 syntax rc0 |
| fixture | baseline 각 PASS0/FAIL0/ERROR14, matrix14변형 모두 ERROR14 |
| 직접 원인 | 두 원본 regression.log: multiprocessing 초기화 중 /dev/shm Errno30 Read-only file system |
| artifact | 업로드 성공, 원본397파일 ZIP 보존; 저장소 제한으로 실보존7일(요청14일) |
| 로컬정리 | Runner컨테이너·proxy·workspace REMOVED |
| GitHub등록정리 | ID4/name 부재 별도 확인 필요; 기존 ID3 증적 승계하지 않음 |
| 정상/결함 인수 | 정상 FAIL_ENVIRONMENT, 결함시험 미착수; 기능회귀 결함탐지 성공 아님 |

source는2750634766862d7fe19479acacc4259ee8315061,
event/Workflow SHA는7f2cb2b2684db412b5dd499729d38cb8364014ec다.
Job과서버증적의Runner ID/name을대조했다. Check head SHA는별도조회하지 않았다.

## 코드 수정 및 다음 실행

코드작성전에 IPC_FAILURE_REVIEW.md를기록했다.
[PR19 수정commit4da96621fd05a4943b76ca32b860a5779ec65e00](https://github.com/321Team/infra-ansible/commit/4da96621fd05a4943b76ca32b860a5779ec65e00):
Runner만 private IPC와64MiB /dev/shm tmpfs(rw,nosuid,nodev,noexec)를사용하고
공유메모리mount4개 및 실제Python fork/spawn semaphore·자식통신을토큰읽기전검사한다.
실패하면prepare PASS/등록을차단한다. 루트읽기전용·네트워크·권한·자원제한은유지했다.

정책37·등록13·IPC경계7=57개로컬테스트및Python IPC probe통과.
수정Podman/실서버prepare와수정Actions는아직미실행이다.
새image/bundle/PREPARED바인딩이필요하므로v1.2영수증을수정/재사용하지않는다.
관리자ID4부재조회와v1.3토큰없는prepare증적을확인한후정상Actions를재시험한다.
이시점에새토큰발급·Actions재실행·결함시험·병합·운영apply를하지않았다.

실행ZIP SHA256 및 원본증적·API조회·Job로그·선별결과를함께보존했다.
actions/extracted/SHA256SUMS는원본ZIP전체의manifest이며선별추출폴더만으로검증하는목록이아니다.
원본전체검증은보존한ZIP의397파일을안전하게해제하여수행했다.
REGISTRY_SHA256SUMS는기존행을보존하고이수집경로의파일만추가한다.
