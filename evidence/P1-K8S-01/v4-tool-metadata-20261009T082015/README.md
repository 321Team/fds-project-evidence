# P1-K8S-01 — v4 배치 도구 메타데이터 보완

CODEX_ASSISTED · 수집/준비 이권욱 · 독립 검토 요청 이하영. **2026-10-09 수신 PC 기록 08:20:15~08:21:27 KST**, 호스트 기록 08:20:17~08:21:28 KST에 5대 고정 경로45개를 읽었다. PC·호스트 시각을 각각 보존하며 이번에 시계 동기화 오차를 검증하지 않았다. 정확한 호스트별 시각은 `analysis.json` 및 수신 원본의 시작/종료 시각을 따른다.

**READONLY 수집 완료 / 배치 정합화·복귀 NOT RUN / REVIEW PENDING.** 파일 bytes는 00:00 회차와45/45 동일하며 승인 소스와28개 일치·17개 불일치가 유지됐다. 새 수집은 [증적174](https://github.com/321Team/fds-project-evidence/pull/174)의 관측을 보완하고 [정합화 준비 PR78](https://github.com/321Team/infra-kubernetes/pull/78)의 실행 전 입력 일부를 채운다. 이 자료를 배포 GO나 AC 인수로 사용하지 않는다.

## 관측 결과

| 호스트 | 승인 소스 일치/불일치 | 실제 SELinux type | 로컬 정책 기본 type |
|---|---|---|---|
| control01 | 8 / 1 | usr_t | usr_t |
| control03 | 5 / 4 | usr_t | usr_t |
| worker01 | 5 / 4 | user_home_t | usr_t |
| worker02 | 5 / 4 | usr_t | usr_t |
| worker03 | 5 / 4 | usr_t | usr_t |

- 전체45개 수집 `COLLECTED`, 읽기 전후 metadata/xattr 안정, 일반 파일·nlink1, uid0/gid0/mode0750. 숫자 ACL은 모두 `user::rwx / group::r-x / other::---`; `system.posix_acl_access`, `security.capability`는 모두 ENODATA(ABSENT). 선택한3종 xattr 외 전체 xattr의 부재를 확인한 것은 아니다.
- 5대 모두 `/sys/fs/selinux/enforce=1`. 전체 실제 문맥 user는 `unconfined_u`, `matchpathcon -n`의 정책 기본 문맥 user는 `system_u`다. **전체 문맥 문자열은45개 모두 기본값과 다르고, type 차이는 worker01의9개**다. 나머지36개를 전체 문맥 일치라고 쓰지 않는다.
- worker01은 교체 후보4개뿐 아니라 보존할5개에서도 type 차이가 관측됐다. 다른 호스트와의 차이만으로 장애/AVC/유입 원인을 단정하지 않는다. 정책 기본값은 현재 호스트 정책의 경로 기본값이며 팀이 승인한 교체·복귀 문맥과 같다는 보장이 없다. Lead가 보존 또는 별도 정정 범위를 결정해야 한다. `restorecon`/`chcon`은 실행하지 않았다.
- 각 호스트 부모4경로(`/opt`, `/opt/fds`, 패키지 root, code)의 uid/gid/mode/선택 xattr 및 filesystem readonly flag를 기록했다. readonly flag0은 실제 쓰기 성공이나 가용 공간·복귀 가능성의 증명이 아니다. 부모 ACL 전체는 수집하지 않았다.

## 수집 범위·권한·안전성

기존 `fds-ansible01` → 정상 `svc_ansible` SSH → `sudo -n python3 -` 경로. 호스트키 엄격검증·기존 키 사용, 새 권한/인증 예외 없음. 실행된 수집기 원본은 각각 `receipts/<kind>-<host>/collector.py`에 있다. 이 순수 조회 수집기는 사전 독립 리뷰를 받지 않았으며 **REVIEW=NOT PERFORMED (Pre-check)** 로 식별한다. 승인 소스 `b4303f2...`는 비교 대상 도구의 버전이고 이 신규 수집기의 리뷰 버전이 아니다.

고정 호스트/euid/00~09시 시간 gate, 고정9경로, 부모 실경로·일반파일·링크 확인, 파일당2MiB 미만, O_NOFOLLOW/O_NOATIME 읽기를 적용했다. 배치 도구를 import/실행하지 않았으며 원격 파일 저장·staging·백업·파일 교체·정책 재적용·서비스 명령·트래픽 시험은 하지 않았다. `getfacl`은 파일당3초 한도, 별도 `matchpathcon -n` 회차도 파일당3초 한도다. 기대 문맥 조회는 metadata 회차보다 약1분 뒤이며 두 회차를 atomic한 단일 스냅샷으로 취급하지 않는다. 두 회차 사이 정책 변경 배제는 별도 입증하지 않았다.

## 출처·재현성·무결성

- `receipts/` 10회 × collector/stdout/stderr/invocation4개: 실행 입력 bytes, 받은 stdout bytes, stderr, SSH 명령·KST·rc·해시를 그대로 보존한다. 수신 stdout은 서버 메타데이터의 JSON 투영본이며 파일 내용/백업 사본은 포함하지 않는다. 원본 도구 bytes는 서버에서 해시 계산에만 읽었다.
- receipt10회 rc0·stderr0, collector와 stdout SHA256 **20/20 일치**. 해시 일치는 수신 무결성이고 독립 진위 검토나 동작 성공은 아니다.
- 비교 입력 `inputs/COMPARISON-0000.json`은 증적174 HEAD `fa75b46067585e1899496f2abb69e6facc13d1d5`의 `evidence/P1-K8S-01/v4-readonly-comparison-20261009T000026/COMPARISON.json` Git blob과 byte 일치한 사본이다. 원 회차를 변경하지 않았다.
- 오프라인 재현: 이 폴더에서 `python3 analyze_k8s_metadata.py .` 출력과 `analysis.json`을 대조한다. 수집기 재실행은 별도 승인된 시간·대상/코드 버전으로 수행할 후속 작업이며 현재 고정 시간 gate를 지우지 않는다.
- `SHA256SUMS`가 이 회차 파일을 포괄하고 루트 대장에는 해당 manifest를 추가한다. 코드/JSON/숫자 ACL만 편입하며 암호·키·토큰/도구 파일 본문은 포함하지 않는다.

## 남은 단계

worker01 type 차이와 전체 context user 차이의 처리 기준, 실제 도구 호출 주체·동시 사용 배제, 검증된 백업, 명시적 교체 대상/실행자/복구 담당/창 GO가 남아 있다. 관측 metadata를 임의 승인값으로 바꾸지 않는다. 다음 배포 시 hash/link/context/ACL은 다시 확인한다. control02·운영 정책·전체 AVC·기능/PortMatrix·AC4 인수는 이 수집 범위 밖이다. 리뷰는 사용자 지시대로 작업창 종료 후 회수한다.
