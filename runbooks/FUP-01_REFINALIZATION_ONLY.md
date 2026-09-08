# FUP-01 Refinalization 원본 전용 수집 v1.0

기준일: 2026-09-08. 상태: **도구 준비·로컬 검증 완료 / 서버 실행·Refinalization 원본 수신 대기**.

## 1. 이번 후속 범위

Rollback 상태 JSON 5대는 이미 수신·해시 검증됐다. 이번에는 `ansible01`에 보관된 Refinalization 원본만 찾는다. Ansible·SSH·네트워크 호출이 없는 로컬 Python 수집기다. 원본 내용·이름·권한을 수정하지 않고 새 결과 폴더만 만든다. 파일 읽기로 access time은 달라질 수 있어 atime 보존을 주장하지 않는다.

찾을 SHA-256:

```text
db7da7eae13c1b07e6b073003a23229e76f3a86f6903a66ac9a2cf522f84395d
```

근거는 [승인 대상 Commit의 CR 변경 기록](https://github.com/321Team/infra-ansible/blob/507d8882a04f53640b07251bcc234b7d6ee81c09/docs/change/CR-P1-ANS-01-01.md)이다. 정확한 원본 파일명은 이 기록에 없다. 증적 [Index 원본](https://github.com/321Team/fds-project-evidence/blob/fe673449c820fb0b988e0357148e6cdb0c152a35/evidence/CR-P1-ANS-01-01/received-20260907T063705Z/EVIDENCE_INDEX.md)에도 별도 Refinalization 파일명은 없다. 이름이 비슷하거나 문서 본문에 해시가 적혀 있는 것만으로는 원본으로 인정하지 않는다.

기존 보관 문서의 Refinalization·재최종화·CR 식별자와 기대 해시를 조회했지만 이번 조회에서는 원본을 확보하지 못했다. 조회 실패는 모든 보관소에서의 유실을 입증하지 않는다.

## 2. 다운로드와 배치

아래 두 파일을 같은 디렉터리에 둔다. GitHub Private 저장소는 로그인한 화면에서 해당 Commit의 Raw 파일로 내려받을 수 있다. 토큰을 명령문이나 대화에 입력하지 않는다.

- [collect-fup01-refinalization.py](../tools/collect-fup01-refinalization.py)
- [FUP01_REFINALIZATION_SHA256SUMS](../tools/FUP01_REFINALIZATION_SHA256SUMS)

WinSCP 등으로 `/home/server01_ansible/fup-refinalization-tools/`에 전송한다. 파일 이름을 유지하고 텍스트 내용을 편집하지 않는다. Linux Python 3 표준 라이브러리만 사용하며 패키지 설치·sudo·Ansible 환경 로딩은 필요 없다.

## 3. 원본 경로를 모를 때 실행

`ansible01`의 `server01_ansible` 일반 계정에서 아래를 실행한다.

```bash
(
  set -eu
  umask 077
  cd /home/server01_ansible/fup-refinalization-tools
  sha256sum --check FUP01_REFINALIZATION_SHA256SUMS
  collection_rc=0
  python3 ./collect-fup01-refinalization.py \
    --search-root /home/server01_ansible \
    --include-archives || collection_rc=$?
  case "$collection_rc" in
    0) printf '원본 해시 일치 후보 발견: 결과 패키지 검토 필요\n' ;;
    2) printf '지정한 검색 범위에서 미발견: 출력된 진단 패키지 제출\n' ;;
    3) printf '검색 제한 또는 읽기 오류 존재: 출력된 진단 패키지 제출\n' ;;
    *) printf '수집기 실행 오류: rc=%s\n' "$collection_rc" >&2; exit "$collection_rc" ;;
  esac
)
```

스크립트가 시작되지 않았거나 사용법·계정 확인에 실패하면 `ARCHIVE=` 출력이 없다. 이 경우 수신 패키지가 생성됐다고 간주하지 말고 오류 출력을 제출한다.

검색은 명시한 홈 경로로 한정한다. 숨김 경로·심볼릭 링크·특수 파일·중첩 압축은 제외하고, 일반 텍스트 확장자·확장자 없는 파일·Refinalization 관련 이름을 검사한다. ZIP/tar/tar.gz는 디스크에 풀지 않고 내부 텍스트를 검사한다. 일반 파일·압축 멤버 8 MiB, 압축파일·gzip 해제 tar 128 MiB, 읽기 합계 512 MiB, 항목 수 20,000의 상한이 있다. 초과·읽기 오류는 보고서의 `issues`에 기록되며 미발견을 전체 유실로 바꾸지 않는다.

## 4. 원본 또는 별도 보관 경로를 알 때

기존 경로를 다음 명령의 값으로 지정한다. `--search-root`는 반복 지정할 수 있고 기존 파일 1개나 ZIP/tar.gz도 받을 수 있다.

```bash
python3 ./collect-fup01-refinalization.py \
  --search-root '/확인된/기존/보관/경로' \
  --include-archives
```

위 경로는 입력 예시이며 실재 경로가 아니다. 읽기 불가를 해소하려고 원본의 chmod/chown을 변경하지 않는다. 별도 Windows Downloads 등에 보관돼 있다면 당시 원본 파일 또는 원래 압축파일을 그대로 첨부하는 방법도 가능하다.

## 5. 결과 제출과 판정

콘솔의 `ARCHIVE=`와 `SIDECAR=`에 출력된 **이번 실행의 정확한 두 파일**을 첨부한다. 이전 결과 폴더를 가리킬 수 있는 와일드카드는 쓰지 않는다. 두 파일이 있는 폴더에서 다음과 같이 외부 해시를 확인한다.

```bash
sha256sum --check FDS_FUP01_Refinalization_Result_v1.0.tar.gz.sha256
```

| 상태 | 의미 | 다음 처리 |
|---|---|---|
| `MATCH_FOUND_REVIEW_REQUIRED` | 기대 해시와 동일한 바이트 발견 | 원본·출처·읽기 전후 메타데이터·내부 Manifest 검토 후 편입 |
| `NOT_FOUND_IN_SCOPE` | 설정된 필터·범위에서 미발견 | 보고서 제출 후 다른 당시 보관 위치 확인 |
| `SEARCH_INCOMPLETE` | 읽기 오류·크기 제한 등으로 검색 불완전 | 보고서의 `issues`로 필요한 범위만 보완 |

일치 파일이 여러 곳에 있어도 같은 바이트는 하나만 보관하고 모든 발견 위치를 기록한다. 일치 바이트는 `originals/refinalization-original.bin`으로 보존하고 원래 파일명·절대 경로 또는 압축 멤버명·압축 해시를 `SEARCH_REPORT.json`에 연결한다. 바이트 정규화·줄바꿈 추가·문서 재작성은 없다. 미발견 결과에는 원본 파일을 만들지 않고 검색 보고서와 Manifest만 포함한다.

보고서의 `source_stat.before/after`는 수집기에서 관측한 dev/inode/size/mode/uid/gid/mtime/ctime이다. 이는 사용자 실행 수집 결과이며 Codex가 서버에서 독립 측정한 것처럼 기록하지 않는다. 강한 Private Key·Token 패턴에 걸린 일치 파일은 편입하지 않는다. 알려진 패턴 검사는 완전한 비밀정보 탐지를 보장하지 않으므로 결과는 Private 수신 경로에서 검토한다.

## 6. 로컬 검증과 Gate

로컬 fixture 10/10 PASS: 이름이 달라도 해시로 판별, CRLF·마지막 줄바꿈 보존, 중복 원본 처리, 유사 이름 불일치, 링크·숨김·누락 경로, ZIP/tar 원본 읽기, 경로 이탈·링크 거부, 크기·압축 해제 상한, 손상 압축, 미발견 시 원본 미생성, 출력 sidecar·내부 해시, 읽기 중 변경·비밀정보 차단을 확인했다. 운영 서버에서의 실행 결과는 아직 없다.

- FUP-01: Rollback 수신 검증 완료·Refinalization 대기 유지.
- FUP-02: 기존 정합성 보완·독립 검토 대기 유지. 재수집 요구 없음.
- 기존 Done·완료일·원 승인·병합 이력과 다른 SFTP 후속 상태 유지.
- FUP-01 수신 항목 확보 후에도 독립 편입 검토와 이권욱의 최종 병합 승인은 별도다.
- finalize·rollback·apply·키 변경·Bootstrap·Tag/Release 작업은 이 수집기에 없다.

원본이 실제 유실된 경우에도 새로 작성한 문서를 과거 원본으로 대체하지 않는다. 유실 범위와 당시 해시 참조를 보존한 별도 예외 판단이 필요하다.
