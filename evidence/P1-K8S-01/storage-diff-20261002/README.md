# P1-K8S-01 Storage 소스↔현장 `kubectl diff` 증적 — 2026-10-02

[fds-project-baseline#10](https://github.com/321Team/fds-project-baseline/issues/10) 핵심 요구 "`WaitForFirstConsumer`, `Retain`, nodeAffinity local PV 제공"과 AC "StorageClass/PV 준비 완료"에서 남아 있던 **소스와 현장의 일치 확인**이다. [evidence#82](https://github.com/321Team/fds-project-evidence/pull/82)가 `CONFIG_DRIFT=OBSERVED`로 기록한 drift를 [infra-kubernetes#51](https://github.com/321Team/infra-kubernetes/pull/51)로 소스 쪽에서 해소한 뒤, 병합된 소스를 현장에 대고 비교한 결과다.

## 자료 구분

**`CONSOLE_SUBMITTED / RECONSTRUCTED_COPY`.** 서버의 `storage-diff-check.txt`와 `.sha256` 파일을 직접 수신하지 않고 콘솔 출력을 붙여넣어 재구성했다. **서버 원본 파일의 해시 검증을 주장하지 않는다.**

## 출처와 수신

| 항목 | 값 |
|---|---|
| 원본 위치 | `k8s-control01` `server02` 홈 `~/storage-diff-check.txt` |
| 수집 | 2026-10-02T14:39:23+09:00 (파일 2행 `date -Is`) |
| 수집 명령 | `kubectl --kubeconfig /etc/kubernetes/admin.conf diff -f /tmp/04-storage.yaml` (읽기 전용, 클러스터에 아무것도 적용하지 않음) |
| 실행자 | 이하영(K8S/SEC Lead) |
| 전달 경로 | control01 콘솔 출력 붙여넣기 → Claude Code 세션에서 파일 재구성 |
| 대상 소스 | infra-kubernetes main `7329bf2eb988b552483af48ff660d6a3f1f1d4f5`(#52 병합)의 `manifests/04-storage.yaml`, blob `bfcd5eaf81a84593e069ad9f44b2955ce10b221a`, SHA-256 `800105063894a44278e0890260c1b9deeb50a5a4494c5b438a1d140f34e1d67b` |
| 소스 전달 경로 | ansible01에서 `gh repo clone`(depth 1)으로 받아 해시 확인 후 ansible `copy`로 control01 `/tmp/04-storage.yaml`에 전달. ansible01·control01에서 각각 SHA-256이 위 값과 일치함을 확인(콘솔 보고) |
| 편입 작성 | Claude Code 세션 (AI 보조) — 독립 검토 필요 |

## 무결성

실행자가 control01 콘솔에서 `sha256sum ~/storage-diff-check.txt`를 실행해 화면에 보고한 SHA-256과, 콘솔 출력에서 재구성한 이 폴더의 `storage-diff-check.txt`의 SHA-256이 일치한다.

```
13325cb57189eb0a2b061e28316812c2e00f4889614ff0d8bc2105673b43d8a8  storage-diff-check.txt   (서버 화면 보고값 = 재구성본)
```

```bash
sha256sum --check SHA256SUMS
```

`SHA256SUMS`는 이 폴더에 편입된 파일의 무결성 목록이며 서버 원본의 증명이 아니다. 암호·토큰 값은 파일에 없다(`sudo` 암호 프롬프트는 `sudo -v`로 미리 처리해 출력에 섞이지 않았다).

## 확인한 사실

- 대상 파일 `/tmp/04-storage.yaml`의 SHA-256이 대상 소스 해시와 같다(파일 5행).
- `kubectl diff -f /tmp/04-storage.yaml` 종료 코드 **0**, 출력 **없음**(파일 7행 `rc=0`). `kubectl diff`는 차이가 없으면 종료 코드 0, 차이가 있으면 1, 오류면 2 이상이다.
- 따라서 이 시각(2026-10-02T14:39:23+09:00)에 소스 `04-storage.yaml`의 객체(StorageClass 1, PersistentVolume 3, PersistentVolumeClaim 3)와 현장 객체 사이에 diff가 없다.

K8S Lead 결정([#10 코멘트](https://github.com/321Team/fds-project-baseline/issues/10#issuecomment-5927261733))에 따라 정본 `Retain`은 static PV의 `persistentVolumeReclaimPolicy: Retain` 기준이고, no-provisioner StorageClass의 기본값 `Delete`는 허용하며, `infra-kubernetes/manifests/04-storage.yaml`이 authoritative source다.

## 한계

1. 서버 원본 파일을 직접 수신하지 않았다(위 자료 구분).
2. `kubectl diff`는 소스가 선언한 필드를 현장과 비교한다. `status`, `claimRef`, 서버 기본값 등 소스에 없는 필드는 비교 대상이 아니다. 같은 이유로 PV 3개의 데이터 보존 동작이나 PVC 바인딩 상태 자체의 증명은 아니며, 그 사실은 [evidence#82](https://github.com/321Team/fds-project-evidence/pull/82)(`sc-pv-20261001/`)의 조회 원본에 있다.
3. 이 증적은 **수집 시각 한 시점**의 비교다. 이후 변경 여부는 확인되지 않는다.
4. infra-monitoring `kubernetes/monitoring/pv-monitoring-storage.yaml`의 legacy/참조 정리는 이 증적의 범위가 아니다(#10 결정 코멘트의 후속 4).
5. 소스 파일은 증적 저장소에 복사하지 않았고, 위 commit·blob·SHA-256으로 참조한다.
6. 수집 중 첫 `kubectl diff` 시도(시각 미기록)에서도 `rc=0`이 보고됐으나 시각·호스트가 파일에 없어 이 증적에 포함하지 않았다.

## 판정 경계

- `STORAGE_SOURCE_RUNTIME_DIFF = EMPTY` (`rc=0`, 출력 없음, 콘솔 제출 자료 기준)
- `CONFIG_DRIFT` ([evidence#82](https://github.com/321Team/fds-project-evidence/pull/82)가 기록한 항목)은 #51 병합과 이 비교로 **해소된 것으로 관측**된다. 해소 판정과 AC 충족 판정은 검토자·Lead가 한다.
- 이 문서는 AC 충족을 주장하지 않는다.

## 검토 상태

AI 세션의 자체 대조(화면 보고 해시와 재구성본 해시 일치, 소스 해시 일치, 민감정보 확인)이며 `governance/EVIDENCE_POLICY.md`의 독립 검토는 아직 없다. 이 편입은 AC 인수나 티켓 종결을 뜻하지 않는다.
