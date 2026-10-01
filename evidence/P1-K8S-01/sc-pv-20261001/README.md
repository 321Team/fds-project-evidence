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
| 편입 작성 | Claude Code 세션 (AI 보조) — 독립 검토 필요 |

`/root`에 저장하려 했으나 권한 거부(`server02`는 root 아님)되어 홈 디렉터리에 저장했다. 이 시도는 증적에 영향이 없다.

## 무결성

control01에서 실행한 `sha256sum ~/sc-pv-pvc.yaml` 결과와 편입본의 해시가 일치한다. 붙여넣기로 옮겼으나 바이트 단위로 원본과 같다.

```
4d463500dc5fa04b53e8942e0e67ffc08fac2aefe969686619d6103e5d781353  sc-pv-pvc.yaml
```

- 크기 8,403 bytes, LF 줄바꿈, CR 없음. `.gitattributes` `* -text`로 변환 없이 보관한다.
- 비밀번호·토큰·키 문자열 검사: 서버에서 `grep -ci password` 0건. 파일에는 Secret 객체가 없고 StorageClass·PV·PVC 메타데이터만 있다.

```bash
sha256sum --check SHA256SUMS
```

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

이 편입은 AI 세션의 자체 대조(서버 해시와 편입본 해시 일치, 민감정보 검사)이며 `governance/EVIDENCE_POLICY.md`가 요구하는 독립 검토는 아직 없다. AC 인수와 티켓 종결은 K8S Lead가 별도로 판단한다.
