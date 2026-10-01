# P1-K8S-01 StorageClass/PV/PVC 상태 증적 — 2026-10-01

[fds-project-baseline#10](https://github.com/321Team/fds-project-baseline/issues/10) 핵심 요구 "`WaitForFirstConsumer`, `Retain`, nodeAffinity local PV 제공"과 AC "StorageClass/PV 준비 완료"에 대응하는 읽기 전용 조회 원본이다.

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

## 참고 사항과 한계

1. **StorageClass의 `reclaimPolicy`는 `Delete`다.** `Retain`이 아니다. 이 클러스터는 정적 PV(no-provisioner)라 PV가 자체 `Retain`을 가지며, 바인딩된 PV의 실제 정책은 PV 값이 결정한다. SC의 `Delete`는 이후 동적 프로비저닝으로 만들어지는 PV에만 적용되는데 이 SC는 provisioner가 없다. 다만 요구사항 문구와 SC 값이 다르므로 설계 원문이 SC 기준 Retain을 요구했는지는 별도 확인이 필요하다.
2. **PV 3개가 모두 `k8s-worker03` 한 노드에 있다.** worker03 장애 시 monitoring 데이터에 접근할 수 없다. 요구사항 위반은 아니나 단일 노드 의존이므로 기록한다.
3. 이 파일은 수집 시점 상태다. Prometheus 재시작 후 데이터 유지는 이 파일로 확인되지 않는다(별도 보고).
4. 수집 시각이 파일에 없어 날짜는 실행자 보고 기준이다. PV·PVC `creationTimestamp`는 2026-09-22T05:45:34Z다.

## 검토 상태

이 편입은 AI 세션의 자체 대조(화면 보고 해시와 재구성본 해시 일치, 민감정보 검사)이며 `governance/EVIDENCE_POLICY.md`가 요구하는 독립 검토는 아직 없다. AC 인수와 티켓 종결은 K8S Lead가 별도로 판단한다.
