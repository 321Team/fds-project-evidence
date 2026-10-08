# P2-APP-01 — portable base live 대조 원본 (2026-10-08 KST, control01)

[#43](https://github.com/321Team/fds-project-baseline/issues/43) portable base([321Team/fds-msa#25](https://github.com/321Team/fds-msa/pull/25), 병합 `7e625274`)의 비교용 overlay `deploy/overlays/p1-onprem`를 Phase 1 운영 `fds-app`과 대조한 원본입니다.

이 폴더는 권욱님 [#25 승인 기록 6053717178](https://github.com/321Team/fds-project-baseline/issues/43#issuecomment-6053717178)의 "live 증적 인수는 별도" 요청에 대응합니다. 요청 항목은 source / cluster-context / namespace / 시각 / revision / digest → render → diff(명령·도구 버전·rc·stdout/stderr)와 원 archive·sidecar입니다.

- 모든 서버 작업은 **읽기 전용**입니다. apply는 하지 않았습니다(`kubectl diff`는 서버 dry-run).
- 실행자: APP Lead 이재환.
- 이 편입은 #43 AC·Status·종결 판정이 아니며, Lab/ROSA Runtime GO가 아닙니다.

## 흐름과 대조 결과

| 단계 | 시각(KST) | 원본 | 결과 |
|---|---|---|---|
| ① live 수집 | 14:45:45 | `control01/p2-app-43-live.tgz` | context `kubernetes-admin@kubernetes`, namespace `fds-app`. Deployment·Service·ServiceAccount·NetworkPolicy·PDB·HPA·Namespace 정리본, Secret·ConfigMap **이름만**, Pod 배치 |
| ② source 묶음 | — | `source/p43-deploy-f618377.tgz` | fds-msa `git archive --format=tar.gz f618377 deploy`. 내장 commit id `f6183777ac9515d68febca57af5cdf559229e0eb`. 같은 명령으로 다시 만들면 같은 SHA-256 |
| ③ 전달·해제 | 14:58 | `terminal/control01-20261008T1458-diff-excerpt.txt` | 서버 `sha256sum -c` 성공, `deploy/` 해제 |
| ④ render·diff 1회차 | 14:58 | `control01/p43-diff-20261008T145807/rendered.yaml`, `diff.txt`, `diff.err` | `kustomize rc=0`, 객체 12개, rendered SHA-256 `58fafcf7…0519`. `diff rc=0`, stdout 0바이트, stderr 0바이트. rc 값은 터미널 출력(③ 발췌)에만 있음 |
| ⑤ 메타·재실행 | 15:44:45 | `30-meta.txt`, `31-rerun-rc.txt`, `rendered-rerun.*`, `diff-rerun.*`, `32-SHA256SUMS` | 도구 버전, context, Deployment revision·digest를 파일로 남기고 같은 diff를 다시 실행. `kustomize_rc=0`, `diff_rc=0`, rendered-rerun은 1회차와 **같은 SHA-256**, stdout·stderr 0바이트 |

### ⑤ 시점 대상 상태 (`30-meta.txt`)

| 항목 | 값 |
|---|---|
| kubectl / Kustomize / Server | v1.36.4 / v5.8.1 / v1.36.4 |
| context | `kubernetes-admin@kubernetes` |
| transaction-api | revision 6, generation 7, `10.1.93.54/fds/transaction-api@sha256:a7093136d12640da00570c18ed278eacbb8e9ba3637c7d509571346eac45cc33` |
| fds-engine | revision 2, generation 5, `10.1.93.54/fds/fds-engine@sha256:5e2a081cd51a957c3fad038b3eab07884c446ea3c2a814a905e3f41c24f67369` |

①의 `20-summary.txt`에 적힌 두 앱의 이미지 digest도 위와 같습니다. 두 앱 모두 분산 설정이 있고(maxSkew 1, hostname, DoNotSchedule, Honor, pod-template-hash), Pod는 3개씩 worker01·02·03에 하나씩 Running입니다.

## 명령

### ① live 수집 (14:45)

```bash
TS=$(date +%Y%m%dT%H%M%S); D=~/p2-app-43-live-$TS; mkdir -p "$D" && chmod 700 "$D" && cd "$D" && echo "dir=$D"
K="sudo kubectl --kubeconfig=/etc/kubernetes/admin.conf"
{ date '+%F %T %Z'; $K config current-context; $K version 2>&1 | tail -2; } > 00-meta.txt; cat 00-meta.txt
for kind in deployment service serviceaccount networkpolicy poddisruptionbudget horizontalpodautoscaler; do $K -n fds-app get $kind -o json > raw-$kind.json; echo "$kind rc=$?"; done
$K get namespace fds-app -o json > raw-namespace.json; echo "namespace rc=$?"
chmod 600 raw-*.json
$K -n fds-app get secret,configmap -o custom-columns=KIND:.kind,NAME:.metadata.name,TYPE:.type > 05-secret-cm-names.txt
$K -n fds-app get pod -o wide > 06-pods-wide.txt
```

이어서 `python3` 정리 스크립트를 실행했습니다. 스크립트가 한 일:
- `raw-*.json`에서 `status`·`managedFields`·`uid`·`resourceVersion`·`generation`·`creationTimestamp`를 뺐습니다.
- env의 `value`가 있으면 `<masked len=N>`으로 바꿉니다(이번 대상에는 `value` 0건, `DATABASE_URL`은 `secretKeyRef`만 있음).
- `last-applied-configuration` 주석은 SHA-256·바이트 수와 정리본으로 바꿨습니다.
- 위 결과를 `10-*.json`과 `20-summary.txt`로 썼습니다.

민감 문자열 검사(`postgres(ql)?(+asyncpg)?://`, `password`)가 0건일 때만 묶었습니다. 원 `raw-*.json`은 서버에만 두고 전송하지 않았습니다.

### ④ render·diff 1회차 (14:58)

```bash
K="sudo kubectl --kubeconfig=/etc/kubernetes/admin.conf"
$K kustomize deploy/overlays/p1-onprem > rendered.yaml; echo "kustomize rc=$?"; grep -c '^kind:' rendered.yaml; sha256sum rendered.yaml
$K diff -k deploy/overlays/p1-onprem > diff.txt 2> diff.err; echo "diff rc=$?"; wc -l diff.txt diff.err; cat diff.err
```

### ⑤ 메타·재실행 (15:44)

```bash
{ echo "collected_at=$(date -Is)"; echo "host=$(hostname)"; echo "pwd=$(pwd)"; echo "--- kubectl version"; $K version 2>&1; echo "--- context"; $K config current-context 2>&1; echo "--- fds-app deployments"; $K -n fds-app get deploy -o custom-columns='NAME:.metadata.name,REVISION:.metadata.annotations.deployment\.kubernetes\.io/revision,GENERATION:.metadata.generation,IMAGE:.spec.template.spec.containers[0].image' 2>&1; } > 30-meta.txt
$K kustomize deploy/overlays/p1-onprem > rendered-rerun.yaml 2> rendered-rerun.err; echo "kustomize_rc=$?" > 31-rerun-rc.txt
$K diff -k deploy/overlays/p1-onprem > diff-rerun.txt 2> diff-rerun.err; echo "diff_rc=$?" >> 31-rerun-rc.txt
sha256sum p43-deploy-f618377.tgz rendered.yaml diff.txt diff.err rendered-rerun.yaml rendered-rerun.err diff-rerun.txt diff-rerun.err 30-meta.txt 31-rerun-rc.txt > 32-SHA256SUMS
tar czf ../p43-diff-results-20261008T145807.tgz rendered.yaml diff.txt diff.err rendered-rerun.yaml rendered-rerun.err diff-rerun.txt diff-rerun.err 30-meta.txt 31-rerun-rc.txt 32-SHA256SUMS
```

## 전달과 무결성

| 묶음 | 크기 | SHA-256 | 전달 |
|---|---|---|---|
| `control01/p2-app-43-live.tgz` | 5148 | `a2309982963ba509e3d57eb56bd39e70ec4810d74812bb6ba015f9cee71516a8` | 서버 `base64 -w76` 출력을 복원. 복원본 SHA-256과 내부 11개 파일 SHA-256이 서버 `sha256sum` 출력과 11/11 같음 |
| `control01/p43-diff-results-20261008T145807.tgz` | 2323 | `7d57f60c7eb4e7c752691ca0cb8af895e34f2d1f7a8e2049482559029702d0ec` | 줄마다 `cksum`을 붙인 base64 41줄을 복원. 41/41 일치, 복원본 SHA-256이 서버 출력과 같음. 내부 파일은 서버 `32-SHA256SUMS`와 9/9 일치(나머지 1개인 `p43-deploy-f618377.tgz`는 묶음 밖이며 ② 원본과 같은 SHA) |
| `source/p43-deploy-f618377.tgz` | 4886 | `0e778f37ea92d83b2e979595c4a3faf70bc7f8d636979cde65de795907f79141` | PC → 서버 방향. 서버 `sha256sum -c` 성공(③) |

- 각 묶음 옆의 `.sha256` sidecar, `ARCHIVE_CONTENTS`(묶음 내부 크기·경로), `registry/ARCHIVE_CONTENTS.json`(내부 해시)을 함께 둡니다.
- `control01/p2-app-43-live-20261008T144545/`와 `control01/p43-diff-20261008T145807/`는 각 묶음을 그대로 푼 파일입니다.
- `SHA256SUMS`는 이 폴더 전체 파일 목록입니다(자기 자신 제외).

## 판독 한계

- diff 0건은 **렌더된 12개 객체**(Deployment 2, Service 5, ServiceAccount 2, NetworkPolicy 3)가 운영과 같다는 뜻입니다. `fds-app`에만 있는 객체(Secret 2, ConfigMap `kube-root-ca.crt`, Pod/ReplicaSet/EndpointSlice)는 대조하지 않았습니다.
- client-side `kubectl diff`의 비교 대상은 서버 dry-run 결과와 현재 객체입니다. Secret **값**은 비교·수집하지 않았습니다(이름과 참조만).
- 14:58 1회차의 rc는 터미널 출력으로만 남아 있습니다(③ 발췌). 15:44 재실행에서 rc를 파일로 남겼고, 출력 바이트는 1회차와 같습니다.
- 14:45 수집과 15:44 재실행 사이에 운영 변경이 있었는지는 따로 조사하지 않았습니다. 15:44 시점 revision·digest는 `30-meta.txt`에 있습니다.
- 이 대조는 P1 운영 소유권 이관이나 p1-onprem overlay apply 승인이 아닙니다.
