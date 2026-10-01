# P1-K8S-01 StorageClass/PV/PVC 상태 증적 — 2026-10-01

[fds-project-baseline#10](https://github.com/321Team/fds-project-baseline/issues/10) 핵심 요구 "`WaitForFirstConsumer`, `Retain`, nodeAffinity local PV 제공"과 AC "StorageClass/PV 준비 완료"의 **현장(Runtime) 상태**를 읽기 전용으로 조회한 원본이다. **승인 Source와 일치하지 않는 drift가 있어 이 증적을 해당 AC·요구의 PASS 근거로 쓰지 않는다.** 아래 '승인 Source와 Runtime 대조'를 먼저 본다.

## 출처와 수신

| 항목 | 값 |
|---|---|
| 원본 위치 | `k8s-control01`(`10.1.93.102`), 사용자 `server02` 홈 디렉터리 `~/sc-pv-pvc.yaml` |
| 수집 명령 | `kubectl get sc,pv,pvc -A -o yaml > ~/sc-pv-pvc.yaml` (읽기 전용) |
| 실행자 | 이하영(K8S/SEC Lead) |
| 수집 | 2026-10-01 KST (정확한 시각은 파일에 없음) |
| 전달 경로 | control01 콘솔 `cat` 출력을 Claude Code 세션에 붙여넣기 → 파일 재구성 |
| 자료 구분 | **CONSOLE_SUBMITTED / RECONSTRUCTED_COPY** (서버 `.yaml`/`.sha256` 파일을 직접 수신하지 않음) |
| 편입 작성 | Claude Code 세션 (AI 보조) — 독립 검토 필요 |

`/root`에 저장하려 했으나 권한 거부(`server02`는 root 아님)되어 홈 디렉터리에 저장했다. 이 시도는 증적에 영향이 없다.

## 무결성

**자료 구분: `CONSOLE_SUBMITTED / RECONSTRUCTED_COPY`.** 서버의 `sc-pv-pvc.yaml`과 `.sha256` 파일을 직접 수신하지 않았다. 따라서 **서버 원본 파일의 해시 검증을 주장하지 않는다.**

확인한 범위는 다음으로 한정한다.

- 실행자가 control01 콘솔에서 `sha256sum ~/sc-pv-pvc.yaml`을 실행해 화면에 보고한 SHA256과, 콘솔 `cat` 출력에서 재구성한 이 폴더의 `sc-pv-pvc.yaml`의 SHA256이 일치한다.
- 편입본은 8,403 bytes, LF 줄바꿈, CR 없음이다. `.gitattributes` `* -text`로 변환 없이 보관한다.
- 서버에서 `grep -ci password` 0건이 보고됐고, 파일에는 Secret 객체가 없고 StorageClass·PV·PVC 메타데이터만 있다.

```
4d463500dc5fa04b53e8942e0e67ffc08fac2aefe969686619d6103e5d781353  sc-pv-pvc.yaml   (서버 화면 보고값 = 재구성본)
```

```bash
sha256sum --check SHA256SUMS
```

`SHA256SUMS`는 이 폴더에 편입된 파일의 무결성 목록이며 서버 원본의 증명이 아니다. 서버 원본 파일과 `.sha256`을 직접 수신하면 새 수집회차로 보완할 수 있다.

## 확인한 사실

| 요구 | 파일에서 확인한 값 |
|---|---|
| `WaitForFirstConsumer` | StorageClass `fds-local-storage`: `volumeBindingMode: WaitForFirstConsumer`, provisioner `kubernetes.io/no-provisioner` |
| `Retain` | PV 3개(`alertmanager-data-pv` 2Gi, `grafana-data-pv` 5Gi, `prometheus-data-pv` 20Gi) 모두 `persistentVolumeReclaimPolicy: Retain` |
| nodeAffinity local PV | PV 3개 모두 `local.path: /home/fds-local-pv/<name>`, `kubernetes.io/hostname In [k8s-worker03]` |
| 바인딩 | PVC 3개(`monitoring-api` 네임스페이스 `alertmanager-data` 2Gi, `grafana-data` 5Gi, `prometheus-data` 20Gi) 모두 `phase: Bound`, 각 PV의 `claimRef`와 일치 |

## 승인 Source와 Runtime 대조 (`CONFIG_DRIFT=OBSERVED`)

StorageClass·PV 소유 source는 P1-K8S-01이지만, 현장에 적용된 객체는 다른 repo의 source와 일치한다.

| 기준 | StorageClass | SC `reclaimPolicy` | PV 이름 | PVC 이름 |
|---|---|---|---|---|
| **Runtime (이 증적)** | `fds-local-storage` | `Delete`(미지정 기본값) | `alertmanager-data-pv`·`grafana-data-pv`·`prometheus-data-pv` | `alertmanager-data`·`grafana-data`·`prometheus-data` |
| infra-monitoring [`kubernetes/monitoring/pv-monitoring-storage.yaml`](https://github.com/321Team/infra-monitoring/blob/9034a6e61f98f58921f4f4fe59c43f58fe23281e/kubernetes/monitoring/pv-monitoring-storage.yaml) (commit `9034a6e61f98f58921f4f4fe59c43f58fe23281e`, blob `ce4b1863fa6e6193174619c1d1a6ba530c34e21a`) | `fds-local-storage` | 미지정 | `*-data-pv` | `prometheus-data`·`alertmanager-data` 등 → **Runtime과 일치(실제 적용 source)** |
| infra-kubernetes [`manifests/04-storage.yaml`](https://github.com/321Team/infra-kubernetes/blob/c55bad39090d4b14cb34bd674e0b91a96f04a5af/manifests/04-storage.yaml) (commit `c55bad39090d4b14cb34bd674e0b91a96f04a5af`, blob `c7891de9922cecf8997a344d0bb87a01dc603b24`), P1-K8S-01 소유 | `fds-local-retain` | `Retain` | `*-pv` | `*-pvc` → **적용되지 않음** |

- Runtime 형상은 infra-monitoring source와 일치하며, infra-kubernetes `04-storage.yaml`은 현장에 적용되지 않았다. 두 source 사이의 차이는 SC 이름, SC `reclaimPolicy`, PV·PVC 이름이다.
- 정본은 StorageClass/PV 소유를 P1-K8S-01로 둔다. 따라서 이 상태는 'K8S 소유 source 미적용 + MON source로 생성된 객체가 운영 중'인 소유·형상 drift다.
- PV 3개의 `persistentVolumeReclaimPolicy`는 Runtime과 두 source 모두 `Retain`이고 nodeAffinity는 모두 `k8s-worker03`이다. 정적 PV이므로 바인딩된 PV의 실제 reclaim 동작은 PV의 `Retain` 값이 결정한다.
- 확인 범위: 위 source 두 파일의 해당 필드를 GitHub에서 읽어 대조했다. infra-monitoring 쪽 PVC 3종 전체(특히 grafana PVC의 정의 위치)는 이 대조에서 확인하지 않았다.
- **drift 처리 방향**(`04-storage.yaml`을 현장에 맞출지, 소유 이관 CR로 할지, Known Issue로 둘지)은 K8S Lead 결정 사항이다. 운영 중인 PVC가 바인딩돼 있으므로 StorageClass 재생성 같은 Runtime 변경은 이 PR의 범위가 아니다.

## 판정 경계

- `RAW_STATE = USEFUL` (Runtime SC/PV/PVC 조회 원본)
- `CONFIG_DRIFT = OBSERVED` (승인 Source `infra-kubernetes/manifests/04-storage.yaml` ↔ Runtime)
- `SOURCE_RUNTIME_TRACEABILITY = DRIFT_DOCUMENTED` (Runtime은 infra-monitoring source와 일치)
- **`AC_CREDIT = NOT_GRANTED`**: 이 증적을 #10 'StorageClass/PV 준비 완료' 또는 'WaitForFirstConsumer·Retain·nodeAffinity 승인값 일치' AC의 PASS 근거로 쓰지 않는다.

## 참고 사항과 한계

1. **StorageClass의 `reclaimPolicy`는 `Delete`다.** `Retain`이 아니다. 이 클러스터는 정적 PV(no-provisioner)라 PV가 자체 `Retain`을 가지며, 바인딩된 PV의 실제 정책은 PV 값이 결정한다. SC의 `Delete`는 이후 동적 프로비저닝으로 만들어지는 PV에만 적용되는데 이 SC는 provisioner가 없다. SC의 `last-applied-configuration`에 `reclaimPolicy` 필드가 없어 API 기본값이 들어간 것이며, 이는 실제 적용된 infra-monitoring source 기준에서만 '기본값'이다. P1-K8S-01 소유 `04-storage.yaml`은 SC `Retain`을 명시하므로 위 '승인 Source와 Runtime 대조'의 drift로 다룬다.
2. **PV 3개가 모두 `k8s-worker03` 한 노드에 있다.** worker03 장애 시 monitoring 데이터에 접근할 수 없다. 요구사항 위반은 아니나 단일 노드 의존이므로 기록한다.
3. 이 파일은 수집 시점 상태다. Prometheus 재시작 후 데이터 유지는 이 파일로 확인되지 않는다(별도 보고).
4. 수집 시각이 파일에 없어 날짜는 실행자 보고 기준이다. PV·PVC `creationTimestamp`는 2026-09-22T05:45:34Z다.

## 검토 상태

이 편입은 AI 세션의 자체 대조(화면 보고 해시와 재구성본 해시 일치, 민감정보 검사)이며 `governance/EVIDENCE_POLICY.md`가 요구하는 독립 검토는 아직 없다. AC 인수와 티켓 종결은 K8S Lead가 별도로 판단한다.
