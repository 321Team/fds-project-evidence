# DEC-P2-REG-01 — Harbor Robot 계정 목록 UI 읽기 전용 확인 (2026-10-08 약 16:07 KST)

- 대상 이슈: [321Team/infra-rosa#10](https://github.com/321Team/infra-rosa/issues/10) (원티켓 [DEC-P2-REG-01 — fds-project-baseline#42](https://github.com/321Team/fds-project-baseline/issues/42) Sub-task 2/4, AC-2 Credential 부분·AC-1 principal 입력, 테스트 전략 추적 TS08)
- Lead 전달 코멘트: [infra-rosa#10 6054561333](https://github.com/321Team/infra-rosa/issues/10#issuecomment-6054561333)
- 이 폴더는 D22 결정의 **입력 증적**이다. D22 최종 결정·IF-19·WBS 갱신은 Decision Lead(이권욱) 소관이며 이 편입으로 확정하지 않는다.

## 수집 정보

| 필드 | 값 | 근거 |
|---|---|---|
| ENV | P1 기존 Harbor (`10.1.93.54:443`) | 화면 |
| 관측 시각 | 2026-10-08 약 16:07 KST | 아래 「관측 시각」 |
| 실행 호스트 / 도구 | `k8s-control01`(`10.1.93.102`, Harbor 443 guard 허용 출발지)의 Firefox → Harbor UI, 로그인 `admin` | 실행자 보고, 화면 우상단 `admin` |
| 화면 | 관리 › 로봇 계정 (목록, 1-3 of 3) | 화면 |
| 조작 | 조회만. 생성·편집·secret 갱신·삭제 없음 | 실행자 보고 |

## 파일

| 파일 | SHA256 |
|---|---|
| `screenshots/harbor-robot-accounts-list-20261008.png` (214,791 bytes) | `ea26fe233f052f07ad32998a0b83d4699642176d830bfe6f19be4a8f17db9b04` |

**원본 구분:** 이 PNG는 실행자가 Claude Code 대화창에 붙인 이미지를 세션이 저장한 파일(PC 파일 시각 2026-10-08 16:07:37)을 바이트 그대로 복사한 것이다. 실행자 PC의 사진·바탕화면·다운로드 폴더에서 별도의 캡처 원본 파일은 찾지 못했다. 대화창 붙여넣기 과정의 재인코딩 여부는 확인할 수 없으므로, 화면 내용의 증적이며 캡처 도구 원본 파일과 바이트 동일하다고 주장하지 않는다.

## 관측 결과 (화면 내용)

3개 계정 모두 활성화(녹색), 시스템 권한 `없음`, 프로젝트 `1 프로젝트`.

| 이름 | 생성 시간(화면) | 만료 시간(화면, 남은 시간) | 만료 계산(생성+TTL) | 설명(화면) |
|---|---|---|---|---|
| `robot$fds-ci` | 26. 8. 28. AM 10:33 | 18d 18h 25m | 2026-10-27 약 10:33 (60일) | (없음) |
| `robot$push` | 26. 9. 18. PM 5:16 | 10d 1h 9m | 2026-10-18 17:16 (30일) | Python3 베이스 이미지 등록용 (fds-ci와 별도) |
| `robot$worker` | 26. 9. 16. PM 5:02 | 8d 0h 55m | 2026-10-16 17:02 (30일) | P1-HBR-01 / IF-10 Worker Pull 전용 계정. k8s-worker01/02/03이 fds/test 이미지를 Pull할 때 사용. Push 권한 없음(D-SEC-01/D19에 따라 Runner(fds-ci)와 자격증명 분리). TTL 30일 정책 적용 |

## 관측 시각

화면에 시계가 없어 남은 시간에서 역산했다. `robot$worker` 10-16 17:02 − 8d 0h 55m = 10-08 16:07, `robot$push` 10-18 17:16 − 10d 1h 9m = 10-08 16:07로 두 값이 같고, 대화창 첨부 파일 저장 시각 16:07:37과도 맞는다. `robot$fds-ci`는 TTL 60일 가정 시 같은 시각과 1분 이내로 맞는다(TTL 60일은 화면에 없는 해석).

## 판정 범위

| 항목 | 판정 | 비고 |
|---|---|---|
| worker 만료 10-16 / push 만료 10-18 (보고값) | 실제 값과 일치 | 생성+TTL 계산과 남은 시간 역산이 서로 맞음 |
| `robot$worker` 재생성 여부 | 재생성 없음 | 생성 시간이 [10-01 캡처](../../P1-HBR-01/lead-runtime-20260930-20261002/README.md)와 같음 |
| secret 갱신 여부 | **확인 불가** | 목록 화면에 나타나지 않음 |
| 프로젝트별 권한 상세 | **이번에 열지 않음** | worker는 10-01 캡처 기준 `fds` 한정 1권한. push·fds-ci 상세는 미확인(목록상 각 1프로젝트) |
| Runner push principal | 설명란 기준 `robot$fds-ci` | 설명 문구에 의한 해석. Runner 설정 파일로 대조하지 않음 |

## 민감정보 점검

화면에는 계정 이름·상태·생성/만료 시각·설명만 있다. Robot secret·token·비밀번호는 화면에 없고 저장하지 않았다. 내부 주소·호스트 이름이 포함되어 저장소 접근 범위를 따른다.

## 경계

- Harbor·Robot 설정 변경이나 rotation은 수행하지 않았다(P1-HBR-01, [baseline#13](https://github.com/321Team/fds-project-baseline/issues/13) 소관, 10-12~13 계획).
- 이 편입은 독립 검토 전이며, 검토·병합이 DEC-P2-REG-01 AC 완료나 D22 판정을 뜻하지 않는다.
