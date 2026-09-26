# P1-SEC-01 Gate 2 원본·보안 후속 수집 v1.0

기준일: 2026-09-26. 상태: **수집 도구 준비 / control01 실행·원본 수신 대기**. 대상 Issue: [#34](https://github.com/321Team/fds-project-evidence/issues/34).

[수신 검토](../evidence/P1-SEC-01/received-20260924T081821Z/RECEIPT_REVIEW.md)에서 미수신으로 남긴 원본 4종과, 보안 후속 중 클러스터에서 확인 가능한 항목을 한 번에 수집한다. 결과는 새 수집회차 `evidence/P1-SEC-01/received-<수신시각>/`로 별도 PR에서 편입한다.

## 1. 수집 범위

| 결과 파일 | Issue #34 항목 | 내용 |
|---|---|---|
| `gate2-logs/`, `01-gate2-logs-verify.txt` | 1-① 원본 로그 6개 | `~/gate2-final-evidence/logs/`를 `cp -p`로 복사하고 9/22 문서의 SHA-256과 `sha256sum --check` |
| `10-apiserver-encryption-flag.txt` | 1-② 보조 | CP 3대 kube-apiserver의 `--encryption-provider-config`, control01 설정 파일 stat·구조(`secret:` 값은 `<REDACTED>`) |
| `11-etcd-secret-prefix.txt` | 1-② etcd raw | etcd의 모든 Secret 키에 대해 저장값 앞 26바이트만 기록. `k8s:enc:secretbox:v1:<키이름>:` 건수 집계 |
| `20`~`22` | 1-③ GNP·HEP | `nodeport-30080-allow` `-o yaml`, GNP 목록, HEP 라벨 |
| `30`~`32` | 1-④ 배포 상태 | fds-app Deployment·RS·Pod·Service, 이미지·Ready, Secret 메타데이터(값 제외) |
| `40-control01-history-check.txt` | 2-① 키 노출 | control01 bash history에서 **현재 설정 키 값**을 포함한 줄 수와 `^ENC_KEY=` 줄 수. 내용은 출력하지 않음 |

9/22 당시 etcd raw 조회 출력은 원본 로그 6개에 포함돼 있지 않다. `11`은 **수집 시점의 재조회**이며 9/22 당시 출력을 대체하지 않는다. 당시 출력이 다른 곳에 남아 있으면 별도로 제출한다.

`11`의 키 이름이 `key1`이 아니면 키가 교체된 것이다. `40`의 `current_key_lines`가 0이어도 이전(노출) 키가 교체됐다면 그 키의 잔존 여부는 이 방법으로 확인되지 않는다.

## 2. 배치와 실행

CP는 인터넷·저장소 접근이 없다. [collect-p1-sec-01-originals.sh](../tools/collect-p1-sec-01-originals.sh)를 control01 root 콘솔에 `cat > /root/collect-p1-sec-01-originals.sh <<'P1SEC01_END'`로 붙여넣고 마지막에 `P1SEC01_END` 한 줄을 입력해 옮긴 뒤 해시를 대조한다. 기대값은 [P1_SEC_01_ORIGINALS_SHA256SUMS](../tools/P1_SEC_01_ORIGINALS_SHA256SUMS)에 있다.

```bash
cd /root && sha256sum collect-p1-sec-01-originals.sh
```

값이 다르면 실행하지 않는다. 일치하면 실행한다.

```bash
bash /root/collect-p1-sec-01-originals.sh
```

읽기 명령만 쓴다(`kubectl get`, `etcdctl get`, `grep`, `stat`, `cp -p`). 클러스터·원본 파일을 바꾸지 않고 `/root/p1-sec-01-originals-<UTC>/`와 같은 이름의 `.tar.gz`, `.tar.gz.sha256`만 만든다. 경로가 다르면 `LOG_DIR=`, `ENC_CONFIG=`, `ETCD_POD=` 환경변수로 지정한다.

## 3. 결과 제출

콘솔의 `ARCHIVE=`, `SIDECAR=` 두 파일을 ansible01 경로 등으로 옮겨 제출한다. 옮긴 뒤 `sha256sum --check <SIDECAR>`로 확인한다. 제출 전 결과에 키·비밀번호 값이 없는지 한 번 더 확인한다.

## 4. 보안 후속 기록 (Lead 결정)

수집 결과와 별개로 아래를 Issue #34에 코멘트로 남긴다. 키·비밀번호 값은 적지 않는다.

| 항목 | 기록할 것 | 근거 |
|---|---|---|
| etcd secretbox 키 | control01 history 정리 여부, 키 교체 여부. 교체했다면 시각(KST)·방법, 새 키 반영 근거 | `11`의 키 이름·접두어 건수, `40`의 건수 |
| Harbor `robot$fds-ci` 60일 | 30일로 맞출지, 예외로 둘지와 이유 | P1-HBR-01 Lead 확인 |
| `nodeport-30080-allow` GNP | infra-kubernetes 반영 여부와 배포 주체 | `20`~`22` |
| DB 비밀번호 | P1-DB-01 Lead [기록](https://github.com/321Team/fds-project-evidence/issues/34#issuecomment-5832659134)의 NOT VERIFIED 잔여 위험 수용 여부 | 재환님 코멘트 |

## 5. Gate

이 도구 편입과 원본 수신으로 P1-SEC-01·P1-K8S-01·ICR의 AC나 Gate가 인수되지 않는다. 로컬 검증은 Rocky Linux 9 컨테이너에서 stub `kubectl`로 수행했다(해시 불일치·누락 보고, 접두어 집계, 키 값 가림, 결과 Manifest·압축 Sidecar 확인). 운영 실행 결과는 아직 없다.
