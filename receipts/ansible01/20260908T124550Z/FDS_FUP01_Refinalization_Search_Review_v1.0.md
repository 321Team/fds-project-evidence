# FUP-01 Refinalization 검색 결과 수신 검토 v1.0

- 수집 보고서 시각: 2026-09-08 21:45:50 KST
- 수신 검토 시각: 2026-09-08 21:49:26 KST
- 검토 결과: **제출 패키지 무결성 PASS / Refinalization 원본 미발견·미수신**
- FUP-01 상태: **Rollback 원본 수신 검증 완료 / Refinalization 보관 위치 확인 대기**

## 검증한 사실

| 항목 | 확인 결과 |
|---|---|
| 패키지 | `FDS_FUP01_Refinalization_Result_v1.0.tar.gz`, 1,243 bytes |
| 외부 SHA-256 | `ab55227d39bd1ced4474a3d7dfade613aa7cb2dc98a7d2c6839d35c1af14a207`, 첨부 sidecar와 일치 |
| 내부 Manifest | `SEARCH_REPORT.json` 1/1 일치, Manifest 자체는 자기 해시 제외 |
| 내부 파일 | 검색 보고서와 Manifest, 총 2개. Refinalization 원본 없음 |
| 경로·유형 | 일반 파일 2개, 중복·경로 이탈·링크 없음 |
| 수집기 식별 | 보고서의 수집기 SHA-256이 배포본 `82036ab647de267a2846e4c0ab0eb5bb3d80f7652d445d1fba1ba795e1d72eb3`과 일치 |
| 보고 상태 | `NOT_FOUND_IN_SCOPE`, `matches=0`, `issues=0` |
| 비밀정보 검사 | 수신 텍스트에서 강한 Private Key·GitHub Token·AWS Key·Bearer 패턴 없음. 모든 비밀정보의 부재를 보증하는 검사는 아님 |

원본 검색 보고서와 내부 Manifest는 바이트 그대로 보존했다. 원본 압축파일을 다시 만들거나 내부 기록을 수정하지 않았다. 수신 바이트·원본 경로 매핑은 [SOURCE_PACKAGE.json](SOURCE_PACKAGE.json), 검토 판정은 [RECEIPT_VERIFICATION.json](RECEIPT_VERIFICATION.json)에 연결한다.

## 검색 결과의 의미와 한계

[수집기 원본 보고서](SEARCH_REPORT.json)는 `ansible01`의 `server01_ansible` 계정에서 `/home/server01_ansible`을 검색했고 압축 내부 검사도 켰다고 기록한다. 보고된 탐색 항목은 1,154개, 읽기 바이트 합계는 4,565,205 bytes다. 탐색 항목에는 디렉터리·압축 멤버 등이 포함되므로 일반 파일 1,154개를 모두 검사했다는 의미로 바꾸지 않는다.

`issues=0`, `search_complete_within_filters=true`지만 숨김 경로·링크 24개와 비대상 62개를 제외했다. 필터 밖 파일, 다른 사용자 홈, Windows PC, 별도 보관소, 중첩 압축 등의 부재는 입증하지 않는다. 보고서에는 생략된 각 경로 목록이 없어 어떤 제외 경로에 원본이 있을지도 판단할 수 없다.

이름 기반 후보 2개는 다음과 같다. 둘 다 이번 배포 도구이며 찾는 과거 기록이 아니다.

| 이름 후보 | 보고된 SHA-256 | 판정 |
|---|---|---|
| `FUP01_REFINALIZATION_SHA256SUMS` | `306e78d2e56ae01cf85d9785bcd4e9fc920fb6a6ee491feff4e130b1e1254b17` | 수집기 검증용 해시 목록 |
| `collect-fup01-refinalization.py` | `82036ab647de267a2846e4c0ab0eb5bb3d80f7652d445d1fba1ba795e1d72eb3` | 이번 배포 수집기 |

수집기 해시·계정·검색 범위·전후 stat은 사용자 제출 보고서 기반이다. 이번 패키지에는 실행 코드 원본이나 모든 파일의 탐색 원시 로그가 없어 실제 실행 전체를 독립 재현·인증한 것으로 기록하지 않는다. Codex의 운영 서버 직접 접속·설정 변경·Runtime 시험은 없다.

## 남은 원본과 다음 조치

기대 Refinalization SHA-256:

```text
db7da7eae13c1b07e6b073003a23229e76f3a86f6903a66ac9a2cf522f84395d
```

이 값은 [승인 당시 CR 변경 기록](https://github.com/321Team/infra-ansible/blob/507d8882a04f53640b07251bcc234b7d6ee81c09/docs/change/CR-P1-ANS-01-01.md)에 남아 있으나 정확한 파일명은 그 기록에 없다. **기대 해시를 인용한 문서 자체는 해당 원본을 대신하지 않는다.**

1. 같은 홈 경로를 같은 필터로 반복 검색하지 않는다. 이미 검증된 Rollback 5대도 재수집하지 않는다.
2. 당시 Refinalization 기록을 작성·내려받아 저장한 위치를 확인한다. Windows 다운로드·별도 증적 폴더 등은 확인 가능한 후보이며 실제 보관 위치로 확인된 것은 아니다.
3. 당시 원본 파일, 해당 원본을 포함한 기존 압축파일, 또는 바이트를 조회할 수 있는 고정 참조를 제출한다. 정확한 다른 보관 경로를 확인한 경우에만 전용 수집기의 `--search-root`를 그 경로로 지정한다.
4. 원본이 실제 유실됐다면 유실 범위·검색 결과·당시 해시·승인 기록을 보존한 별도 예외 판단이 필요하다. 본 검토는 유실을 확정하거나 예외를 승인하지 않는다. finalize 재실행·사후 문서 재작성으로 과거 원본을 대체하지 않는다.

## 상태 통제

- FUP-01은 원본 확보 전 종결하지 않는다. 검색 결과 수신 완료와 원본 수신 완료를 구분한다.
- 기존 Rollback 원본 5/5 수신 검증 및 보고 기반 권한 확인 범위는 유지한다.
- FUP-02는 이번 신규 증적이 없으므로 기존 정합성 보완·독립 검토 대기 상태를 유지한다.
- 기존 CR Done·완료일·원 승인·병합 이력, SFTP 기술 후속 완료, 다른 Gate는 그대로 보존한다.
- 증적 PR #1은 Draft·독립 편입 검토 대기다. 최종 병합·Bootstrap·Tag/Release는 수행하지 않았다.
