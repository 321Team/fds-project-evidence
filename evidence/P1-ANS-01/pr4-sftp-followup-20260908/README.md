# PR4 SFTP 후속 수신 및 전송 옵션 수정

직접 SFTP 읽기 6/6 PASS, 내부 Hash 25/25, 원본 텍스트 26개. 기존 키 상태와 PR4 최종 키 상태도 일치한다.

- [수신·원인·수정 검토](FDS_SFTP_Receipt_and_Transport_Fix_Review_v1.0.md)
- [원본 SFTP 보고서](results/SFTP_REPORT.json)
- [기술 대조 결과](RECEIPT_REVIEW.json)
- [원본 매핑](SOURCE_FILE_MAP.json) · [압축 원본 보관](SOURCE_PACKAGE.json)
- [등록 파일 체크섬](SHA256SUMS)
- [키트 수정 diff](fix-reference/APPLY_KIT_V1_3_FIX.patch)

v1.2 적용 키트의 SSH -T 옵션을 공통 인자에 넣은 결함을 수정했다. fix-reference는 로컬 검증한 배포·시험 소스이며 새 실 서버 실행 결과가 아니다. 승인 main 28개 코드는 그대로다. 수정 후 Ansible SFTP-only ping 실제 서버 검증은 대기다. 원래 실제 apply를 반복할 필요는 없다.

[운영 이슈 #10](https://github.com/321Team/infra-ansible/issues/10). 독립 사람 검토·증적 전체 병합·엔진 전환·Bootstrap은 별도 상태다.
