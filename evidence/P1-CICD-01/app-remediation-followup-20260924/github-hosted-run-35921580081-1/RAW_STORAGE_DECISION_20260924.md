# 원본 artifact 임시 보관 결정 (2026-09-24)

대상: artifact 10777267517 `candidate-images-bbe349c8815ed2ade3de87a1b312221c34f4361b-1.zip`, 278,490,138 bytes, SHA-256 `22c0952ccafa9dc5d65506f821e5c125179d9bd4b7bcbfcd193dda36d5415eb8`.
결정: 이권욱(P1-CICD-01 Lead, 증적 저장소 관리자), 2026-09-24.

## 결정

증적 정책은 1MB를 넘는 원본을 Git 대신 팀이 접근할 수 있는 저장 위치에 두고 그 URI를 기록하도록 한다. 이 원본은 [raw-archive-receipt-20260924.json](raw-archive-receipt-20260924.json)에 기록된 cicd-runner01 경로를 **프로젝트 기간 중 2026-10-31까지 임시 보관 위치로 허용**한다.

| 항목 | 내용 |
|---|---|
| 위치 | `cicd-runner01:/home/server01_cicd-runner/evidence-raw/app-remediation-followup-20260924/github-hosted-run-35921580081-1/candidate-images-bbe349c8815ed2ade3de87a1b312221c34f4361b-1.zip` |
| 허용 기한 | 2026-10-31 |
| 적용 범위 | 이 원본 한 건. 다른 증적이나 정책 전반의 예외가 아니다 |
| 조건 | 위치의 파일을 바꾸거나 지우지 않는다. Runner 재구성·정리 작업에서 이 경로를 보존하고, 없어지면 그 사실을 이 폴더에 새 기록으로 남긴다 |
| 기한 전 조치 | 정식 팀 보관 위치로 옮기고, 새 URI와 수신 측 SHA-256 대조 결과를 새 기록으로 추가한다 |
| 기한 경과 시 | 옮긴 기록이 없으면 이 원본은 "팀 접근 가능 보관"으로 인정하지 않는다 |

GitHub artifact는 2026-09-30T21:18:11Z에 만료된다. 그 뒤에는 이 서버 사본이 팀이 접근할 수 있는 유일한 사본이다.

## 검토 독립성

원본 수신·해시 대조는 리뷰어 이하영이 수행했다. 확인한 사람과 승인하는 사람을 나누기 위해 이재환을 리뷰어로 추가한다.

## 판정 영향

이 결정은 원본 보관 위치만 다룬다. CVE 판정(API HIGH 44·CRITICAL 0, BLOCK)과 APP BLOCK·Runtime AC 1/10·Delivery NOT_VERIFIED는 바꾸지 않는다. HIGH/CRITICAL은 예외 없이 해결해야 하며, 해결 결과는 새 Build/Scan 회차의 증적으로 따로 제출한다.
