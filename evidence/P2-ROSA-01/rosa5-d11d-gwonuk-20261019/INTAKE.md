# 수신·편입 기록 — infra-rosa#5 D-11d 이권욱 원본 (이하영, 2026-10-20)

이 폴더의 `README.md`·`SOURCE_MANIFEST.json`은 생산자(이권욱)가 만든 편입 준비 문서입니다. 두 문서에는 `PRIVATE_STAGING_NOT_PUBLISHED`, `recipient_ack: PENDING`으로 적혀 있습니다. 이 파일은 그 뒤 **수신자(이하영)가 한 확인**을 기록합니다. 생산자 문서는 고치지 않았습니다.

- 결과 인계: [#5 6268659431](https://github.com/321Team/infra-rosa/issues/5#issuecomment-6268659431)
- 원본 전달: [#5 6270087938](https://github.com/321Team/infra-rosa/issues/5#issuecomment-6270087938)
- 관계:
  - [PR #248](https://github.com/321Team/fds-project-evidence/pull/248) 병합 폴더 `infra-rosa-5-bootstrap-20261019/` README의 "미수신" 표 중 **이권욱 D-11d 행**을 받는 후속 수집회차입니다.
  - 그 폴더는 봉인돼 있어 수정하지 않았습니다.
  - 이재환 D-11d는 같은 PR의 `infra-rosa-5-d11d-jaehwan-20261019/`에 있습니다.
- 편입 경위:
  - 이 폴더는 #248 브랜치의 미병합 커밋 `ae4f3e35`에 올라 있던 것입니다.
  - 그 커밋에서 **이 폴더 파일만** 가져왔습니다.
  - 같은 커밋의 봉인 폴더 수정(README·SHA256SUMS)은 가져오지 않았습니다.

## 수신 확인 (2026-10-20, 이하영)

**1. 공유 폴더 원본 재해시:** 위치는 `\\10.1.93.150\HybridCloud과정공유디렉토리\07_프로젝트\제01조\02차 프로젝트\`입니다. 원본 TGZ 2개의 값이 생산자 sidecar `.sha256`와 전달 기록 `gwonuk-D11d-transfer-20261019-2333.txt`의 값과 같습니다.

| 원본 TGZ | 크기 | SHA-256 | 회차 |
|---|---:|---|---|
| `gwonuk-d11d-20261019T130514Z.tgz` | 643 | `54abb5a9c4a92fe5fa8f8e03cf756bd12eb947bfe3a4f4663d1e83cc5137db20` | attempt1-auth-failure |
| `gwonuk-d11d-20261019T132512Z.tgz` | 851 | `3741810af9e648870eea96a60f7e7f6fc8d3a0044fccbfe80332883226e799dd` | attempt2-pass |

전달 기록 파일 `gwonuk-D11d-transfer-20261019-2333.txt`의 SHA-256은 `2cbf2a7058897a4bef162aeae21fbc2c7330cf76c8b4bf82632c40b1341fe7f3`입니다.

**2. 압축 내용과 이 폴더 대조:** 두 TGZ를 풀어 나온 파일 6개(각 `D11d.log`, `run-status.txt`, `SHA256SUMS`)가 이 폴더의 `attempt1-auth-failure/`, `attempt2-pass/` 파일과 **바이트 단위로 6/6 일치**합니다. `SOURCE_MANIFEST.json`에 적힌 해시와도 같습니다.

**3. TGZ 보관 위치:** 생산자 설계를 따라 TGZ는 Git에 넣지 않고 공유 폴더에 둡니다. 이 저장소에는 풀어 낸 텍스트 원본과 각 회차의 원래 `SHA256SUMS`만 있습니다.

**4. 민감정보:** 편입자가 6개 파일 전문을 읽고 패턴 검사(OAuth `sha256~` token, JWT, 개인키, `client-key-data`, AWS access key, `password:`)를 했고 0건이었습니다. `Password:` 줄은 빈 프롬프트입니다.

## 결과 (attempt2-pass, 원문 그대로)

| 질의 | 기대(gwonuk) | 관측 |
|---|---|---|
| `get pods -n fds-app` | yes | yes (rc=0) |
| `create deployments -n fds-app` | no | no (rc=1) |
| `list nodes` | no | no (rc=1) |
| `get secrets -n fds-app` | no | no (rc=1) |
| `create servicemonitors.monitoring.coreos.com -n fds-app` | no | no (rc=1) |
| `create prometheusrules.monitoring.coreos.com -n fds-app` | no | no (rc=1) |

`USER=gwonuk`, `SERVER=https://api.fds-rosa-hcp.khht.p3.openshiftapps.com:443`, `SOURCE=f3042f6`, oc 4.22.17, `D-11d rc=0 log_rc=0`, `TEMP_KUBECONFIG_CLEANED=YES`, `OWN_LOGOUT_RC=0`.

attempt1-auth-failure는 로그인 401로 6개 질의가 NOT_RUN이었습니다(원인 미확인). PASS로 덮지 않고 보존합니다.

## 판정 범위

`D-11d(gwonuk)=PASS(attempt2) / attempt1=FAIL(401, 보존) / ORIGINALS=RECEIVED(TGZ 2/2, 내부 6/6 일치) / RECIPIENT_ACK=이하영 2026-10-20`

해시 일치는 무결성 확인이며 시험 PASS의 단독 근거가 아닙니다. 독립 사람 리뷰는 이 PR에서 이권욱이 합니다. 생산자 본인 자료이므로, 독립성 판단은 리뷰어가 합니다.
