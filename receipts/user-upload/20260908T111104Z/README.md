# 사용자 제출 기존 종결 티켓 증적 수신

- 수신 ID: `USER-UPLOAD-20260908T111104Z`
- 수신 시각: `2026-09-08T11:11:04Z`
- 제출 설명: 기존 종결 티켓의 증적자료
- 원본 파일: `evidence.zip`
- 원본 SHA-256: `915be6e1df8c3718a344b0e07dd69a3e57362684749495f246e964391206e1da`
- 원본 크기: `1,651,904 bytes`
- 보관 참조: `libfile_91bb8fc817a48191909d1164bacce412`

원본 ZIP은 수정·재압축하지 않았다. ZIP CRC 검사는 PASS이며 264개 항목의 경로 안전성을 확인했다. 이 저장소에는 원본 압축파일을 중복 업로드하지 않고 보관 참조와 SHA-256, FUP-01/02 관련 판독 결과만 기록한다.

## FUP-02 판독

- ZIP의 `P1-ANS-01` 파일 46개 중 기존 Git 수신본 38개가 38/38 동일하다.
- 추가 8개는 이미지 7개와 `04_ansible_ping.txt`이며 이번 FUP-02 정합성 보완 범위에는 편입하지 않았다.
- 05h 실제 SHA-256: `9f5b8c1b24dc9e44109d57205ca3c13bf54e3b0e05ee53615371f2604065ad95`
- 05j 실제 SHA-256: `944d3e74cfc72e9ed0ce56a5914a16fcba7ae35f2145cd243f2e2a5ef172006d`
- 구 `99_SHA256SUMS.txt` SHA-256: `45a8d2ae43b62e96636fae1a4c43b8490de26a02e33ceff188b43784f37c8bce`
- 구 매니페스트가 가리키는 이전 05h/05j 해시와 일치하는 ZIP 항목은 없다.
- 05h/05j 승인본은 각각 승인본 반영 후 매니페스트 재생성을 후속 조치로 명시한다. 실제 제출 패키지에는 그 갱신이 적용되지 않았다.

[FUP-02 보완 판정](P1-ANS-01_FUP-02_REMEDIATION.md)과 [원본 매핑](SOURCE_FILE_MAP.json)을 따른다.

## FUP-01 판독

이 ZIP에는 `CR-P1-ANS-01-01` 디렉터리, 기대 Refinalization 해시 또는 변경 노드의 `original-resolver.json`이 없다. FUP-01은 [읽기 전용 보완 절차](../../../runbooks/FUP-01-02_REMEDIATION.md)로 별도 수령한다.

## 검사 경계

`P1-ANS-01` 텍스트 파일에서 Private Key, GitHub Token, AWS Access Key, Bearer Credential 강한 패턴은 발견되지 않았다. 이미지·내부 압축파일의 내용 검사는 이번 범위에 포함하지 않았으며, SHA-256 일치는 시험 결과나 승인 진위의 단독 증거가 아니다.
