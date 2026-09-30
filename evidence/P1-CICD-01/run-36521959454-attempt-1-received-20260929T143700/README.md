# P1-CICD-01 — Run 36521959454/1 Runtime 수신 증적

수신 기준: **2026-09-29 14:49 KST**. 책임 티켓은 `321Team/infra-cicd#11`, 상위 정본 티켓은 `321Team/fds-project-baseline#16`이다.

**Run #5 Test→Build→Scan = PASS / Harbor Push = NOT_EXECUTED / DELIVERY_GATE = NOT_VERIFIED.**

이 폴더는 Runner에서 수집한 Run #5 원본의 수신·검증 기록이다. 증적 편입의 독립 검토와 병합은 Runtime 실행 자체의 재승인이 아니며, Harbor/Kubernetes Delivery 인수를 의미하지 않는다.

## 실행 식별자

| 항목 | 값 |
|---|---|
| GitHub Actions Run / Attempt | `36521959454 / 1` |
| Workflow SHA | `52cf494bec02ab4b814bed07e4cf66f37a3547b6` |
| Active config SHA256 | `05dadd477f483e8c288acfabb2e785193185b402d8dba3baf24fc4562b9796d8` |
| Source | `321Team/fds-msa@368786c1e36b2bfb5424c4da472c1cc319c5c8c3` |
| Runner | `cicd-runner01 / server01_cicd-runner / UID 1000` |
| APP_WORKFLOW | `PASS` |
| BUILD_SCAN / IMAGE_SCAN | `PASS / PASS` |
| Push / Deploy | `NOT_EXECUTED / NOT_EXECUTED` |
| Delivery Gate | `NOT_VERIFIED` |

## Test / Build / Scan

- `fds-engine-unit-0`: **16 passed**.
- `transaction-api-contract-0`: **14 passed, warning 1**.
- `fds-engine-contract-0`: **10 passed, warning 1**.
- `transaction-api` Trivy: **HIGH 0 / CRITICAL 0**.
- `fds-engine` Trivy: **HIGH 0 / CRITICAL 0**.
- Trivy DB receipt SHA256: `28ce86e310b4edb75070e93447ce5d215f77c333ec3bdafe5be4223f6ab70f90`.

두 warning은 Starlette `TestClient`의 `httpx` 사용 deprecation warning이며 해당 시험의 종료 코드는 0이었다.

## 이미지 식별자

| 서비스 | OCI archive SHA256 | local OCI manifest digest | config digest |
|---|---|---|---|
| transaction-api | `c13cb05f072c212e0282473c8b60d0037c42d06d1b43d051e3f15c9215e7b256` | `sha256:b4d8675dc350bb6f602196f840a7afc3c034163f28ad83f718496cfc345be966` | `sha256:20c72b6b6d35fc92860f7573d9ad67feb3878ede4c807dd3ee84e1f42695c21b` |
| fds-engine | `53322489ffe5049e3b21b1cb6c825b313d9737c131aaeefba244b01a114554f1` | `sha256:eea750c2ff3a86d5bbe50a699fc98266b2d9a032c4e1ebeb268526781d8a4f79` | `sha256:b07e79980c6b1390dd9de25849281e97ebd58c2bc90daa518ab8acb2914fcc77` |

위 manifest digest는 **Runner의 local OCI archive 식별값**이다. 아직 Harbor registry manifest digest나 Deployment/Pod digest로 표시하지 않는다.

## 수신 원본

`SOURCE_ARCHIVES.sha256`에 두 수집 archive의 원본 SHA256을 고정한다.

- main evidence archive: 17,990 bytes / SHA256 `32624aef49ca490551df18e0ed777ae7f93fb67fae960b8555aeb9ab9df1b549`
- supplement archive: 48,300 bytes / SHA256 `9dacfae8fd42044965ccf17ea2c570b9acfccf089cf5cd5fb8542f87a309ae9a`

main archive는 일반 파일 39개를 포함하며 collector 추적 목록 33개에 대해 수신측 SHA256 재검사를 통과했다. supplement의 두 `report.json`은 원 Scan 영수증의 report SHA와 수신측 재계산값이 각각 일치했다.

독립 검토를 위해 수신 원 tar.gz 2개와 동명 `.sha256` sidecar를 `originals/`에 **byte-for-byte** 편입한다. 저장소 루트 `registry/ARCHIVE_CONTENTS.json`은 각 archive의 외부 SHA256/크기와 내부 member 이름·크기·SHA256을 기록한다. main archive의 collector 추적 목록은 **33/33 MATCH**, supplement의 report manifest는 **2/2 MATCH**다. 독립 리뷰어의 실제 원본 대조는 아직 `PENDING`이며 이 편입 자체를 독립 승인으로 간주하지 않는다.

## Harbor preflight — 차단사항

2026-09-29 14:37 KST Runner 읽기 전용 점검:

- route: `10.1.93.54 via 10.250.10.1 dev ens160 src 10.250.10.20`, rc 0.
- `harbor.fds.internal`: DNS rc 2.
- `https://10.1.93.54/api/v2.0/health`: curl rc 60 / HTTP `000`.
- OpenSSL verify code 20: `unable to get local issuer certificate`.
- Podman 6.1.0 / rootless `true`.
- rootless authfile 없음.
- 14:47 KST CA discovery에서 server issuer는 `FDS Project Root CA 2026`; Runner 로컬 matching CA candidate는 **0개**.

따라서 현재 **Harbor Push Gate는 TLS Trust BLOCK**이다. `--tls-verify=false`, insecure registry 또는 인증서 검증 비활성화를 사용하지 않는다.

## 검증 범위와 한계

1. Run #5의 Test→Build→Scan 실행과 수신된 선택 원문/해시의 연결은 확인했다.
2. OCI archive 자체 바이트는 Runner에 남아 있고 이 PR에 포함하지 않는다. Harbor Push 직전 동일 경로에서 SHA256을 다시 계산해야 한다.
3. 원본 Trivy report 바이트는 supplement archive에 있으며 이 PR에는 full body를 복제하지 않는다. SHA256은 수신측 재계산 PASS다.
4. Harbor Push, Harbor registry manifest digest, Kubernetes dry-run/diff, Deploy, Pod `imageID`, rollback은 **미실행**이다.
5. `DELIVERY_GATE=NOT_VERIFIED`를 유지한다.
6. 증적 PR의 독립 검토는 **PENDING**이며 작성자/AI 검증을 독립 승인으로 표시하지 않는다.

## 독립 검토 포인트

- 두 archive SHA와 `SOURCE_ARCHIVES.sha256` 연결.
- Run/Attempt/Workflow/config/source identity 일치.
- Unit/Contract log와 Run summary의 종료 코드 및 건수 일치.
- Trivy HIGH/CRITICAL 0 및 report SHA 연결.
- local OCI archive hash / manifest / config identity 연결.
- Harbor TLS Trust BLOCK을 Push PASS로 확대하지 않았는지.
- 민감정보·credential 원문 미포함 여부.
- 원 archive 접근이 필요하면 리뷰 완료 전에 별도 인계 확인.
