# PR #4 실제 운영 적용 수신 기록

2026-09-08 사용자 서버 실행 결과: **6/6 적용 및 수신 기술 검토 PASS**, 비차단 SFTP 경고 후속 확인.

- [검토 결과와 주의점](FDS_PR4_Runtime_Receipt_Review_v1.0.md)
- [서버 실행 원본 보고서](results/APPLY_REPORT.json)
- [기존 운영 경로 Git 동기화 원본](results/GIT_SYNC_REPORT.json)
- [수신 검토 JSON](RECEIPT_REVIEW.json)
- [원본 패키지 보관·Hash](SOURCE_PACKAGE.json)
- [원본 파일 → Git 매핑](SOURCE_FILE_MAP.json)
- [등록 파일 SHA-256](SHA256SUMS)
- [운영 이슈 #10](https://github.com/321Team/infra-ansible/issues/10)

운영 경로 `~/p1-ans-01`, main `3a02dc8934adb1f80df48ec6763689c401a1e8d6`, 엔진 2.16.19.
51단계 PASS, 내부 Hash 55/55, 승인 소스 28개, 기존 증적 등 59개 보존.
실제 apply 12회 모두 changed=0이며 제한 키가 이미 기대값이어서 키 파일은 보존됐다. 전용 백업은 6대 각각 생성됐다.

원본 상태 APPLIED_VERIFIED_REVIEW_REQUIRED는 바꾸지 않는다. Codex 수신 검토를 사람의 독립 승인으로 표시하지 않는다. 운영 독립 검토와 증적 편입·병합 대기, Bootstrap HOLD.

이 디렉터리에서 `sha256sum --check SHA256SUMS`로 등록 파일을 검사하고, `results` 디렉터리에서 `sha256sum --check SHA256SUMS`로 원본의 내부 55개 목록을 검사할 수 있다. 압축 원본 검사는 별도 보관된 패키지와 sidecar를 함께 받아 수행한다.
