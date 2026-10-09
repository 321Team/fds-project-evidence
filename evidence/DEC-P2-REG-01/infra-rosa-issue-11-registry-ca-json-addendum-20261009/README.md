# DEC-P2-REG-01 — registry 추가 CA JSON 증적 addendum: FQDN 전환 문구 정정 (2026-10-09 KST)

- 정정 대상: [`../infra-rosa-issue-11-registry-ca-json-20261008/README.md` 60행](../infra-rosa-issue-11-registry-ca-json-20261008/README.md) "판정 범위" 표의 "HCP가 IP key를 실제 pull trust에 적용하는지" 행 비고. 병합본: [evidence merge `70bdb92` L60](https://github.com/321Team/fds-project-evidence/blob/70bdb9290b6360fb5ecd5e3b3d7980ce02a0c8bc/evidence/DEC-P2-REG-01/infra-rosa-issue-11-registry-ca-json-20261008/README.md#L60)
- 근거: [infra-rosa#11 후속 심층 리뷰 §2 보완 A (이권욱, 2026-10-08 18:58 KST)](https://github.com/321Team/infra-rosa/issues/11#issuecomment-6057397677)
- 원 폴더는 봉인 규칙에 따라 고치지 않는다. 이 addendum이 해당 비고를 **대체**한다. JSON·스크립트·로그·해시(`4d86507ecd81789e376669940f68b2dbb27f5989e6fd4315238c9f61a2401da4`)는 바뀌지 않는다.
- 이 문서는 문구 정정이다. 새 Runtime 결과가 아니며 FQDN 구현이나 시험을 수행하지 않았다.

## 정정

| 구분 | 문구 |
|---|---|
| 원문 (L60 비고) | infra-rosa#4 cold-pull에서 확인. 실패하면 manifest를 FQDN으로 바꾼다(재생성 불필요) |
| **대체 문안** | HCP IP-key/cold-pull 실패 시 원인과 로그를 보존하고 중단한다. FQDN 전환은 fds-project-baseline#40의 worker DNS 해석·경로 계약, 해당 host에 매칭되는 P2 pull-only credential reference, image repository/digest·TLS 이름 일관성을 확인한 뒤 별도 승인 범위에서 수행한다. 동일한 추가 CA map을 유지하면 FQDN key 추가에 따른 registry-config rollout은 필요하지 않지만, 다른 설정 변경의 영향은 별도로 판단한다. 전환 후 cold-pull로 확인하며 실패 시 승인된 이전 참조/설정으로 원복하거나 중단 상태를 유지한다. |

## 원문이 틀린 이유
1. **CA key가 있어도 나머지 조건은 따로 필요하다.** trust map에 FQDN key가 있다는 것은 "그 이름의 인증서를 신뢰한다"는 것뿐이다. worker가 `harbor.fds.internal`을 해석할 DNS 경로(#40)와 그 host에 매칭되는 pull credential은 별도로 필요하다.
   - IP용 auth 항목만 있는 상태에서 image host만 FQDN으로 바꾸면 인증 없이 pull을 시도해 실패할 수 있다. 쿠버네티스는 이미지 registry와 매칭되는 credential을 사용한다([Kubernetes: Pull an Image from a Private Registry — multiple registries](https://kubernetes.io/docs/tasks/configure-pod-container/pull-image-private-registry/#using-images-from-multiple-registries)).
2. **"재생성 불필요"의 범위는 좁다.** 같은 추가 CA map을 유지하므로 FQDN key 추가로 인한 registry-config rollout을 피할 수 있다는 뜻까지만이다. DNS나 다른 클러스터 설정 변경의 영향, 또는 모든 IP pull 실패의 복구를 보장하지 않는다. registry 설정을 변경하면 전체 machine pool rollout이 일어난다([ROSA HCP image configuration](https://docs.redhat.com/en/documentation/red_hat_openshift_service_on_aws/4/html/images/image-configuration-hcp)).

## 판정 범위 (변경 없음)
`OUTPUT4=FIXED_CANDIDATE_ACCEPTED / FQDN_RECOVERY=DOC_CORRECTED(this addendum) / HCP_IP_KEY=UNVERIFIED / COLD_PULL=NOT_RUN / D22_FINAL=NOT_ISSUED`

## 민감정보
문구, 링크, 해시만 있다. 자격증명·키는 없다.
