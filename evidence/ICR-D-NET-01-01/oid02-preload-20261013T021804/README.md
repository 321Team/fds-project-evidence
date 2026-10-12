# OID02 실제 공급·반입 수집회차

Phase1 / 이권욱 / CODEX_ASSISTED. [보고서](../../../records/p1-oid02-preload-20261013.md). 준비21개와 runtime44개 영수증을 원래 bytes로 보존. preparation 문서의 미실행/승인 대기는 당시 상태이고 현재 결과는 runtime/VERIFICATION.json에 있다.

원 준비 checksum은 그대로 보존했고 live status는 runtime/에 분리했다. 실행 helper 독립 REVIEW 미수행; 편입 리뷰/병합은 PR208 대기. API/설정은 선택 필드 및 원 응답 해시 기록. 비밀 값·OCI tar는 Git에 포함하지 않는다. 기록 소스를 서버에 재실행하지 않는다. 읽기 검증: `python3 runtime/verify_results.py <이 폴더>/runtime`.
