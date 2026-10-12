# P2-ROSA-01 — infra-rosa PR36 PG-03 admission 수집기 MOCK 시험 원본 (2026-10-11 KST)

- 책임: [infra-rosa#6](https://github.com/321Team/infra-rosa/issues/6) (P2-ROSA-01 Sub-task 4/6, PG-03) · 소스 [infra-rosa PR #36](https://github.com/321Team/infra-rosa/pull/36)
- 시험 대상 소스: infra-rosa `5585754bcd9bf9cbc6ee855fd8099533cce7273f` (브랜치 `p2-rosa-01/pg03-portable-scc-check`). 이 코드는 리뷰 진행 중이며 아직 승인·병합되지 않았다.
- 실행자·위치: 이하영, 개인 AWS CloudShell (Amazon Linux 2023, kernel 6.1.188-233.385.amzn2023.x86_64, Python 3.13.15, git 2.50.1)
- 실행 시각: 2026-10-11 약 22:39 KST (묶음 파일 생성 13:39 UTC 기준)
- 이 폴더는 CloudShell에서 이 저장소로 직접 git push했다. 중간 PC를 거치지 않았다.

## 무엇을 시험했나
가짜 `oc`(시험 파일이 임시 폴더에 만드는 스크립트)로 수집기의 판정·중단·무쓰기를 확인했다. **실제 OpenShift·ROSA·클러스터·AWS API에는 접속하지 않았다.**

| 시험 | 명령 | RC | 결과 |
|---|---|---:|---|
| PR36 수집기 MOCK 37건 | `bash precheck/portability/tests/pg03-mock.sh` (KEEP=1) | 0 | `PASS: 37 cases; no write verbs; target check before API; structured admission verdicts` |
| W0 기존 시험 | `bash precheck/portability/tests/input-contract.sh` | 0 | PASS 2줄 (`out/input.stdout`) |

두 시험의 stderr는 0바이트다. 격리 조건으로 `env -i PATH=/usr/local/bin:/usr/bin:/bin HOME=<run>/home TMPDIR=<run>/tmp`를 썼다. AWS 자격증명과 git 전역 설정은 상속하지 않았다.

## 파일
| 파일 | 내용 |
|---|---|
| `pg03-mock-5585754.tgz` | 원본 묶음(재압축 없음). `out/`: 두 시험의 stdout·stderr·rc. `tmp/`: MOCK 37건 임시 로그(가짜 fds-msa fixture 포함, 파일 1,589개) |
| `pg03-mock-5585754.tgz.sha256` | 묶음 SHA-256 `eb1b14773c76bda5b478722304e81ba2191ddcb5e20a7624573e7448a26b1634` |
| `SHA256SUMS` | 이 폴더 파일 해시 |

내부 파일 목록은 `registry/ARCHIVE_CONTENTS.json`에 있다.

## 판정 범위
`MOCK=PASS(37+input-contract) / REAL_OC=NOT_RUN / SHARED_OCP=NOT_RUN / ROSA_RUNTIME=NOT_RUN / CI(infra-rosa)=NOT_RUN / SOURCE_REVIEW=PENDING / PG03=HOLD`

수집기 자체의 판정 로직 시험 결과다. ROSA restricted-v2 admission 실측, PG-03 해소, 실제 SCC·UID·기동 PASS가 아니다. Phase 1 서버·설정은 변경하지 않았다.

## 민감정보
가짜 응답·fixture·시험 로그만 있다. 자격증명·kubeconfig·토큰은 없다. MOCK fixture git 커밋의 작성자는 `fixture@example.invalid`다.
