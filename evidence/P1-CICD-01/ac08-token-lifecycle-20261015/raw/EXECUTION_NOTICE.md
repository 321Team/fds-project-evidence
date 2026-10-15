## AC08 실행 착수 기록 — 2026-10-15 KST

사용자/Lead 이권욱이 하버 서버 사용 가능을 확인하고, CICD PR83 병합 후 “착수”를 지시했습니다. 독립 코드 리뷰와 별도로 이번 AC08 실행 범위를 기록합니다. CODEX_ASSISTED.

- 코드: PR83, 검토 HEAD `4043d975fdcd72aa38e2dca5e57e00ebc7ecbd70`, merge `c373f1d7a8e6e84548180839098c34e9a1262eef`. 이하영 독립 승인, PR CI729개 및 병합 CI38659948197 PASS.
- 대상: ansible01/server01_ansible → CP1/server02, cicd-runner01/server01_cicd-runner. API `10.1.93.109:6443`, 기존 CA/SSH trust/SA UID 유지. 공급 broker+module9개가 승인 HEAD와 바이트 동일. bundle SHA256 `f213fcc9addbf802b45308d5a1dc4b73666aac9606d03256e19d02057d6bf12e`.
- 창: **09:35~10:05 KST, 실제 시작 상한09:45**. 관련 Harbor·Ansible·D03 세션에서 선행 실행/예약 없음과 종료 인계까지 관련 변경 보류 확인. 추가 PMO 세션도 서버 실행/예약 없음 확인. PR84/85는 Runner0의 QUEUED 상태로 유지하며 공급하지 않음. 실제 시작 직전 앱/Runner/RBAC·GitHub 활동을 재확인.
- 회차: **AC08 진단1회, TokenRequest 명령 최대2번(각900초이하)**. 동일 named Deployment GET의 유효200 → JWT 만료+75초 뒤 실제401 → 새 Token200. 첫401 확인 전 복구용 발급 없음. Deployment 변경·exec·Harbor Push·RBAC 변경 없음.
- 사전점검: 발급0 preflight PASS, 세 서버 시각 동기화와 API v1.36.4 확인. 이는 실제 만료/복구 성공 증거가 아니며 아직 AC08 완료 처리하지 않음.
- 중단/회수: 예상 HTTP/CA/UID/시계/정리 불일치·시간 초과면 중단. 발급 불명 시 시도 소진, 자동 재시도 없음. 자기 subprocess·논리 참조 정리와 자연 만료만 사용하며 SA/Role 삭제·보안 우회·서비스/호스트 종료 없음.

완료 후 공개 원본·명령/시각/rc/hash, 전후 Deployment2/Pod6/RBAC 불변, 새 작업 경로/로그·프로세스 잔존 검증을 회수하고 종료 인계합니다. 증적 저장소 독립 편입 및 AC08 최종 인수는 별도입니다.
