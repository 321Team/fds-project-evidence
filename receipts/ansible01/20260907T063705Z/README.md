# ansible01 2026-09-07 원본 수신

- [수신 검토 보고서](FDS_Ansible_Evidence_Receipt_Review_v1.0.md)
- [파일별 무결성 대조](RECEIPT_VERIFICATION.json)
- [원본 파일 경로·Hash 매핑](SOURCE_FILE_MAP.json)
- [원본 압축파일 보관 참조](SOURCE_PACKAGES.json)

CR 17개, P1-ANS 38개, DNS ZIP·Sidecar 2개 수신. DNS ZIP 내부 텍스트 24개는 별도 바이트 보존 추출본이다. 수집 Metadata 2개는 원본 그대로 보존한다. 원본 tar/ZIP은 제출된 파일에서 그대로 보존하며 Git에는 텍스트·참조만 기록한다. DNS ZIP 재생성·Release 게시 없음.

COLLECTION_SHA256SUMS는 원래 review-input 배치를 위한 원본 Manifest다. 이 디렉터리에서 직접 실행하는 용도가 아니다. Git 배치 경로는 SOURCE_FILE_MAP.json, 전체 저장소 현재 바이트는 루트 REGISTRY_SHA256SUMS를 사용한다. 현재 Manifest PASS는 P1-ANS 과거 Manifest의 2개 불일치를 소급 해소하지 않는다.
