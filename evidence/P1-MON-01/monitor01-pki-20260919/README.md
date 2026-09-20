# monitor01 PKI 발급·반환·종료 증적 인계

판정: **PKI 발급·공개 반환·monitor01 현장 대조·CA 볼륨 잠금 완료(사용자 콘솔 근거)**. TLS 서비스 배포·IF-06B·ICR-AC12/16 인수·P1-MON-01 종결은 미완료다.

이 폴더는 2026-09-19 이권욱이 대화에 제출한 화면 9개, 공개 PEM 2개 및 분석 환경의 검증 결과를 보존한다. 원본 스크린샷은 바이트 그대로 복사했다. 화면 촬영·각 실행의 정확한 시각과 전체 서버 원문 로그/종료코드는 수신하지 않아 추정하지 않았다. 작성 시각은 RECEIPT.json의 recorded_at_kst이며 실행 시각이 아니다.

## 요청·승인 소스 연결

- [P1-MON-01 #17](https://github.com/321Team/fds-project-baseline/issues/17): Lead 이재환 / Support 이권욱 유지.
- [infra-pki PR #4](https://github.com/321Team/infra-pki/pull/4), 승인 HEAD `c731ed6c4f23e5a4bf5f796d1f805cb11f68a2b4`, merge `aeda506aebf89d86fd788f64227e898af8f0e324`.
- 사용 ISO `FDS_MONITOR01_CA_37fda6d9_v1.1.iso`, SHA256 `25c358cd90c7bb0f43bfadbd57e5e6c9e47e9f6d520bbd5c1d42a3159bf163a2`는 기존 발급 소스 기록의 참조다. 이 폴더에 ISO를 재편입하지 않았다.
- 요청 CSR SHA256 `37fda6d9fb99f101bf213a8e6a070c3e6dce3ba5238b54f178d9c62c8ddd3fa1`.

## 실제로 확인한 결과

| 단계 | 근거·판정 |
|---|---|
| ca01 서명 | 서명/대장 반영 화면, serial 1001(hex), CA_SIGN_AND_VERIFY=PASS |
| 공개 PEM 복원 | 사용자 캡처의 본문 복원 후 원본 화면의 파일 SHA256 2/2 일치 |
| 분석 환경 검사 | 고정 Root 지문·서명 체인·IP/serverAuth·기존 ISO CSR 공개키 일치 |
| monitor01 수신 | sha256sum 두 파일 성공 화면 |
| monitor01 현지 키 비교 | PUBLIC_KEY_MATCH=PASS·CHAIN_IP_SERVER_PURPOSE=PASS 화면 |
| ca01 종료 | XFS unmount 및 /dev/mapper/fds-ca is inactive 화면 |
| CA VM 전원 OFF | 미확인 |
| TLS/Auth/Remote Write·Blackbox | 미실행/미인수 |

수신 공개 PEM의 값은 다음과 같다. 파일 SHA256과 인증서 DER 지문을 구분한다.

```text
Leaf file SHA256: 85620544c77fb1b8e7a4ab5acfaf491ed45244a51fdfaebde951c05572d0a3ec
Root file SHA256: 20ddfa5e92c346aaf46fc30179fbc0b069e256effd2615a9f4308a8fe719053f
Leaf fingerprint SHA256: 98424fca698e250c72c3c1c0fb7bc3de84f34926fc1fc3ebf82e2d059efdf7a4
Root fingerprint SHA256: 6a75baf4dbe03ef24cce944e616384d318f7ca919cd7bd914624b4cebac06b10
CSR/Leaf SPKI DER SHA256: 175f4b5dcc4563d2a42096de853ea8eb45d9d808ef06e8dcdb806cd101085028
```

Leaf: C=KR/O=FDS/OU=Monitoring/CN=monitor01, RSA3072, IP SAN 10.250.10.30, CA:FALSE, serverAuth. 유효기간 2026-09-19 19:57:32 ~ 2027-09-19 19:57:32 KST. 서버 공개키의 기존 receipt는 PEM 인코딩을 해시하므로 DER 해시와 다르며, 두 형식 모두 앞선 로컬 검증에서 대조했다.

## 파일과 재확인

`SHA256SUMS`는 화면에서 읽은 두 PEM 해시와 이름으로 재작성한 공개 반환용 파일이다. ca01의 원본 체크섬 파일 자체를 수신했다고 주장하지 않는다. `LOCAL_VERIFICATION_20260919T204135KST.json`은 현장 반환 전의 로컬 검증 원문이므로 당시 NOT_EXECUTED/NOT_CONFIRMED 값은 보존하며, 이후 사용자 화면 결과는 RECEIPT.json과 위 표를 따른다.

```bash
sha256sum -c SHA256SUMS
sha256sum -c RECEIPT_SHA256SUMS
openssl verify -x509_strict -CAfile fds-root-ca.crt -purpose sslserver -verify_ip 10.250.10.30 monitor01.crt
```

첫 두 검사는 수신 바이트 무결성, 마지막은 실행 시점의 인증서 유효성을 확인한다. 향후 만료 후 결과를 과거 Runtime 실패로 해석하지 않는다. 사진별 관측·SHA256은 RECEIPT.json에 연결한다. 공개키·공개 인증서 외 CA 디렉터리/대장/개인키/암호를 반출하지 않았다.

## 후속 인계

monitor01의 Leaf `/home/server01_monitor/monitor01.crt`, Root `/home/server01_monitor/fds-root-ca.crt`, 현지 개인키 `/etc/fds/pki/monitor01/request/monitor01.key`를 MON Lead의 TLS proxy/localhost receiver 통합에 사용한다. 공개 파일 홈 경로는 수신 위치이며 최종 서비스 경로·소유권·SELinux 검증은 아직이다. 재발급하지 않는다.

이번 PR은 기존 증적의 편입 심사 대상이다. 모든 evidence PR의 독립 리뷰 규칙을 유지하며, 이 문서나 작성자 검증으로 독립 승인·병합·전체 Runtime AC 완료를 선언하지 않는다.
