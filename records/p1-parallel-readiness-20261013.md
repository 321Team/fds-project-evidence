# Phase 1 병행 준비와 실제 읽기 결과 — 2026-10-13

CODEX_ASSISTED · 이권욱.04:26 기존 CP1 server02 인증/CA/SA GET 확인,04:28~29 OID03 관련6노드 설치/cache/unit metadata 읽기. 새 Token/Deploy/reboot/정책 변경 없음.

[결과·범위·실패 이력·후속](../evidence/P1-CICD-01/parallel-readiness-20261013T0426/README.md), [봉인](../evidence/P1-CICD-01/parallel-readiness-20261013T0426/SHA256SUMS).

03:13 p1_ansible_ed25519의 실패는 보존하며 CP1에는 기존 id_ed25519 경로가 유효함을 확인했다. 새 Push 영수증/Deploy 창·복구 승인은 여전히 미확정이다. 현재 설치와 RPM cache 관측은 공급 출처/오프라인 재설치/부팅 연속 보호의 증거가 아니다. 기존 OID02 import와 이번 조회를 분리한다.

검증: 공개 소스7개 Git blob·구문·bundle, 읽기9묶음 receipt/해시·host/user/SA/CA,6노드 관측표. 검증 명령은 collection의 verify_collection.py에 해당 collection 경로를 준다. Runtime 읽기·작성자 검증을 독립 REVIEW/AC 인수로 확대하지 않는다.
