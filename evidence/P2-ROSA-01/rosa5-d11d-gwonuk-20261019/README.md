# ROSA #5 — 권욱 D-11d 원본 편입 작업본

상태: **PRIVATE_STAGING_NOT_PUBLISHED**. 2026-10-20 중앙 준비. 실행자·작성자 이권욱 / CODEX_ASSISTED. 이 폴더는 하영의 예정된 기존 증적 PR에서 재사용할 새 수집회차 후보이며, 새 PR·병합·증적 독립 승인 또는 #5 종결을 뜻하지 않는다.

## 출처와 단계

- 책임 Record ID: `P2-ROSA-01`, 실행 티켓 [infra-rosa #5](https://github.com/321Team/infra-rosa/issues/5).
- 실제 실행 source: `f3042f6228c4d5bdcde59c13330ceb90b287987a` / oc 4.22.17, Kustomize v5.7.1. 대상은 API `https://api.fds-rosa-hcp.khht.p3.openshiftapps.com:443`, 본인 ROSA 사용자 `gwonuk`.
- [최초 결과 인계](https://github.com/321Team/infra-rosa/issues/5#issuecomment-6268659431) · [원본 실제 전달](https://github.com/321Team/infra-rosa/issues/5#issuecomment-6270087938). 10/19 23:34 KST 공유 사본 바이트·SHA256 일치. 10/20 00:00 KST에도 사본 존재/해시 일치. **하영 수신 ACK·증적 PR 편입은 미확인**이다.
- 원본 TGZ는 고정 비공개 검토 공유 최상위에 보존한다. 기존 아카이브를 재압축·이동·삭제하지 않고 안의 텍스트 세 파일을 각 회차에 바이트 그대로 복사했다. TGZ의 Git/Release 업로드는 수행하지 않았다.
- 기존 수집회차 폴더를 변경하지 않는다. 새 경로 `evidence/P2-ROSA-01/rosa5-d11d-gwonuk-20261019/`만 후보로 준비했다. 실제 PR 편입 시 최신 정책·대장·변경 경로와 겹침을 확인한다.

## 회차별 실제 결과

| 회차 | 실제 KST | 결과 | 정리 |
|---|---|---|---|
| attempt1-auth-failure | 10/19 22:05:14~22:19:47 | 로그인 401, 6 SSAR NOT_RUN, D-11d rc1/log_rc0. 원인은 미확인 | 임시 kubeconfig 삭제 YES. OWN_LOGOUT_RC=1은 성공적인 토큰 회수 증거가 아님 |
| attempt2-pass | 10/19 22:25:12~22:25:35 | 본인 로그인 성공, 권욱 기대값 6/6, D-11d rc0/log_rc0 | OWN_LOGOUT_RC=0·임시 kubeconfig 삭제 YES |

| 2회차 can-i 질의 | 실제 응답 | RC | 권욱 기대값 |
|---|---|---|---|
| get pods -n fds-app | yes | 0 | yes |
| create deployments -n fds-app | no | 1 | no |
| list nodes | no | 1 | no |
| get secrets -n fds-app | no | 1 | no |
| create servicemonitors.monitoring.coreos.com -n fds-app | no | 1 | no |
| create prometheusrules.monitoring.coreos.com -n fds-app | no | 1 | no |

`nodes` namespace-scope Warning은 별도 경고이며 뒤의 실제 `no`/RC1을 보존한다. 재환의 모니터링 생성 허용 기대값과 권욱의 거부 기대값은 서로 다르므로 하나의 표로 덮지 않는다. 재환 원본은 이 작업본에 없다.

## 원본·무결성 범위

| 원본 TGZ | SHA256 |
|---|---|
| gwonuk-d11d-20261019T130514Z.tgz | `54abb5a9c4a92fe5fa8f8e03cf756bd12eb947bfe3a4f4663d1e83cc5137db20` |
| gwonuk-d11d-20261019T132512Z.tgz | `3741810af9e648870eea96a60f7e7f6fc8d3a0044fccbfe80332883226e799dd` |

각 하위 회차의 `D11d.log`, `run-status.txt`, `SHA256SUMS`는 원본 그대로다. 기존 `SHA256SUMS`는 두 데이터 파일만 덮으며 README·새 source manifest를 원본 목록에 추가하지 않았다. 이 복사 검증과 이전 원본 검토를 재사용했고 서버 시험을 다시 실행하지 않았다. 새 문서 및 기존 Manifest의 대장 등록 후보는 작업본 바깥 `REGISTRY_ENTRIES.pending.txt`에서 제공한다. 실제 대장을 수정/발행하지 않았다.

## 한계와 후속

- 암호는 소유자가 AWS 화면에서 직접 입력했다. 원본의 `Password:` 줄은 빈 프롬프트이고 암호·JWT·kubeconfig를 수록하지 않는다. staged 여섯 파일의 실제 내용 점검 범위이며 다른 원본의 무비밀성을 대신 보증하지 않는다.
- 부모 기본 kubeconfig 전후 해시와 전체 바깥 런처 명령 원본은 미수집이다. 독립 subshell 실행·임시 파일 삭제 관측, 로그 안 source/version/각 질의·RC까지만 주장한다. 누락을 보완하려는 동일 시험 재실행은 요구하지 않는다.
- 권욱 개인 D-11d PASS는 deploy SA의 fresh 인증·배포 권한, #46 Runtime 또는 #5 전체 AC 완료가 아니다. DNS/TLS·Route 검증도 포함하지 않는다.
- REVIEW는 실행자 자체 점검/AI 보조 검토까지다. 증적 정책의 독립 사람 리뷰는 미완료이고 실제 PR 편입 후 해당 commit에서 진행한다.
- 후속 담당: 하영은 기존 계획 PR에 이 폴더를 필요 범위로 재사용하고 수신·편입 링크를 연결한다. 재환의 PASS 보고와 원본 두 개 수신은 별도 연결한다. 이미 확인한 같은 시험이나 중복 자료 제출은 요청하지 않는다.
