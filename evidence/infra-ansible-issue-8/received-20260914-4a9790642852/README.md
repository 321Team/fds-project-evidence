# Issue #8 새 오프라인 환경 실행 증적 — 2026-09-14

기술 검토 결과 **PASS_FRESH_OFFLINE_FIXTURES_VERIFIED**. 사용자가 2026-09-14 이 87개 파일의 비공개 증적 저장소 등록·별도 PR 생성·이하영님 리뷰 요청을 명시적으로 승인했습니다. 독립 리뷰·코드/증적 병합은 아직 미완료입니다.

- 구현 [PR #16](https://github.com/321Team/infra-ansible/pull/16), 추적 [Issue #8](https://github.com/321Team/infra-ansible/issues/8).
- 시험 코드 HEAD `d2d46bd95ece3935373303187ef47cfc5e3e2eb7`, tree `214191ff55bf70b7f03837ecf2f549332e081209`.
- 사용자 제출 실행 경로 `/tmp/issue-8-offline-qSPCHwDz`, Linux x86_64 / glibc 2.39 / Python 3.12.14.
- 2026-09-14 12:42:08~12:44:35 UTC (21:42:08~21:44:35 KST). 검토 PC의 새로운 Ansible 실행으로 대체하지 않았습니다.

## 리뷰 시작점

| 항목 | 확인 결과 | 원본 |
|---|---|---|
| 전체 | 5단계·runner exit=0 | [KIT_RUN](original/evidence/results/KIT_RUN.json), [RECEIPT](original/evidence/RECEIPT.json) |
| 새 환경 | 두 venv, 설치 8개 명령 exit=0, pip 25.2 / 엔진별 9개 의존성 고정 | [설치 원문](original/evidence/prepare-installation), [RUNTIME](original/evidence/RUNTIME.json) |
| 단위시험 | 43/43 PASS | [로그](original/evidence/results/unit-tests/stderr.log) |
| SSH guard | baseline 엔진별 14/14, 12개 결함 변형 검출, 196개 관찰 재대조 | [MATRIX](original/evidence/results/guards-results/MATRIX.json) |
| 구조화 결과 | 58/58 = 실제 CLI 32회 + 파생 입력 26개 | [MATRIX](original/evidence/results/contract-results/MATRIX.json) |
| DNS 정규화 | 두 엔진 2/2 PASS, localhost changed=0 | [2.16.19](original/evidence/results/dns-2.16.19), [2.21.3](original/evidence/results/dns-2.21.3) |

[RUNTIME_AUDIT](RUNTIME_AUDIT.json)은 현재 GitHub HEAD 48개 소스 blob을 대조하고 그 판정기로 제출 원문을 재검토한 결과입니다. 전체 압축본의 guard 196개 관찰, 구조화 판정 58개, report 원본 참조 해시 128개, 설치 명령·의존성·DNS 결과를 대조했습니다. 음성 사례의 FAIL/ERROR/REVIEW_REQUIRED는 기대 결과입니다.

## 출처와 편입 범위

- 전체 압축본 `issue-8-evidence.tar.gz`: 356,771 bytes, SHA256 `4a97906428522dc9668ed9b9d65c742607df8125bbbbe57f3b99f3470f0f0748`.
- 실행 키트 SHA256 `b3914ebbffa1f19cdf619b090be4edb10b711db74039bc40441d05523ea4b42c`; 독립 verifier SHA256 `951c8bb9ed7a1c9019c43ca95e59e9ef36d86ec2ced65d23f8441a70662b734d`.
- 전체 711개 파일, 상위 710개·results 669개·contract 229개 manifest 해시 모두 일치. [수신 감사](RECEIPT_AUDIT.json).
- Git 편입은 핵심 원문 **81개**와 이 안내·감사·출처표입니다. 전체 711개나 708개를 편입했다고 주장하지 않습니다. [SOURCE_SELECTION](SOURCE_SELECTION.json)에 원본 경로·크기·SHA256·Git 경로를 연결했습니다. 이 폴더는 `REVIEW_SHA256SUMS`로 검증합니다.
- 등록 승인: 사용자는 원문 81개와 검토 자료 등 총 87개를 비공개 `321Team/fds-project-evidence`에 등록하고 별도 증적 PR 생성·이하영님 리뷰 요청까지 진행하는 범위에 대해 **“승인”**으로 명시적으로 동의했습니다. 이 폴더와 출처표가 승인된 범위이며 생략 원문의 추가 전송이나 운영 적용은 포함하지 않습니다. 이 등록 승인으로 독립 코드·증적 리뷰를 대체하지 않습니다.
- 전체 압축본·sidecar와 추출 원문은 사용자 Desktop 및 검토 작업공간에 보존했습니다. 팀 공용 전체 압축본 보관 URI/GitHub Release 바이너리 게시는 미등록입니다. 전체 원문 재감사는 보존 압축본이 필요합니다.
- 제한적 개인키·토큰·운영 공개키 재료 검사 검출은 0개입니다. fixture 문자열은 운영 키가 아닙니다.

## 한계와 후속

pip의 `--no-index --require-hashes --only-binary` 및 새 venv의 로컬 wheel 처리 로그를 확인했습니다. 독립 네트워크 패킷 추적은 없습니다. clean checkout과 전체 소스 해시 검사는 고정 verifier가 실행 전후 강제하며 별도 git status 콘솔은 없습니다.

이번 실행은 localhost fixture 전용입니다. 실제 6대 읽기 재실행·운영 apply·운영 엔진 전환·기존 운영 checkout main 반영은 포함하지 않습니다. #7의 실제 6대 16/16은 별도 수신 회차입니다.

이하영님(@hayeounglee)의 코드·증적 독립 리뷰 및 병합 후 #8 종결 여부를 판정합니다. #6/#7/P1-ANS-01 Done·PR #4 Closed 유지. 후속은 #5 CI → #9이며 이번 결과를 CI/운영 전환 PASS로 확대하지 않습니다.
