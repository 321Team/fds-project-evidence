# P1-K8S-01 시험 전·후 읽기 전용 조회 묶음 (`ro-evidence-20261005`), 2026-10-02 ~ 2026-10-05

[fds-project-baseline#10](https://github.com/321Team/fds-project-baseline/issues/10) 작업 중 ansible01에서 저장한 **조회·질의 출력 파일 12개**를 편입합니다. 10/4 CP 복구 준비·T09(DNS) 확인·B2 이미지 확인·T15 구성 증적, 10/5 `ac-net-run01` 시작 전 기준선과 SELinux·Calico/CoreDNS 상태가 포함됩니다.

**이 문서는 어떤 AC의 PASS·충족도 주장하지 않는다.** 각 파일은 해당 시각의 단일 조회이며 판정과 인수는 검토자와 Lead가 한다. 이 묶음은 [#30 Close 입력](https://github.com/321Team/fds-project-baseline/issues/30#issuecomment-6013862840)의 KNOWN ISSUE "시험 전 읽기 전용 묶음 편입 예정" 항목을 해소하기 위한 것이다. [Lead 결정 5991399143](https://github.com/321Team/fds-project-baseline/issues/10#issuecomment-5991399143)이 `t15-config.txt`(sha256 접두 `0dea8111…`)를 근거로 이미 인용했고(그 코멘트의 약식 끝 표기 `…cba2`는 이 폴더 파일의 실제 끝 `…6ba2`와 다르다. 전체 해시는 `SHA256SUMS` 기준), [PMO/QA 5992138284](https://github.com/321Team/fds-project-baseline/issues/10#issuecomment-5992138284)가 "11:05 조회 묶음은 보완 자료로 후속 편입하면 된다"고 정리했다.

## 자료 구분
- 모두 **ansible01에서 저장한 출력 파일**이다. 서버 원본 파일을 직접 가져온 것이 아니며, 서버 쪽 원본과의 대조는 하지 않았다. 파일 머리글에 시각과 `ansible01`이 적혀 있다.
- 머리글에 `read-only`가 적힌 파일은 `ac-net-run01-fresh-gate`, `b2-image-check`, `cp-checkpoint-inspect`, `cp-checkpoint2-public`, `cp-recovery-prep`, `ro-new-…T110506`, `t15-config`이다. `t09-prep`, `t09-result`(`dig` 질의 결과), `t09-followup`, `w03-health`는 머리글에 표기가 없고 내용은 조회·질의 출력이다.
- 개인키·`client-key-data`·`dockerconfigjson`·Bearer·password 값 패턴을 이 폴더 전체(압축 내부 포함)에서 검색했고 일치 0건이다. 검색한 패턴 범위의 결과이며 모든 비밀의 부재 보증이 아니다.

## 파일 (머리글 시각, KST)
| 파일 | 머리글 | 시각 |
|---|---|---|
| `t09-prep.txt` | T09 PREP | 2026-10-04 16:02:43 |
| `t09-result.txt` | T09 RESULT | 2026-10-04 16:04:40 |
| `t09-followup.txt` | T09 FOLLOWUP | 2026-10-04 16:18:33 |
| `w03-health.txt` | worker03 health after power-on | 2026-10-04 16:21:27 |
| `t15-config.txt` | T15 CONFIG EVIDENCE | 2026-10-04 17:42:54 |
| `cp-recovery-prep.txt` | CP RECOVERY PREP | 2026-10-04 19:25:27 |
| `cp-checkpoint-inspect.txt` | CP CHECKPOINT INSPECT | 2026-10-04 19:31:20 |
| `cp-checkpoint2-public.txt` | CP checkpoint2 public zone | 2026-10-04 19:32:28 |
| `b2-image-check.txt` | B2 IMAGE CHECK + T09 remaining nodes | 2026-10-04 21:11:05 |
| `ac-net-run01-fresh-gate-20261005T100223.txt` | AC-NET-RUN01 FRESH GATE BASELINE | 2026-10-05 10:02:23 |
| `ro-control01.tgz` | `p1-mon-acnet-pre-20261005T100654/`(`time.txt` 10:06:54, `nodes.txt`, `pods-fds-app.txt`, `pf.log`, `up.txt`, `up-targets.json`·`.txt`, `times.txt`, 내부 `SHA256SUMS`)와 `mon-discover.txt`(머리글 시각 2026-10-02 20:41:58) | 2026-10-05 10:06 전후 |
| `ro-new-20261005T110506.txt` | READ-ONLY: SELinux + Calico/CoreDNS health | 2026-10-05 11:05:06 |

## 무결성
- 편입 전 12개 파일은 수집 때 만든 `SHA256SUMS` 12/12와 일치했고, 이 폴더의 `SHA256SUMS`는 같은 12개 해시에 `README.md` 한 줄을 더한 것이다.
- `ro-control01.tgz` 내부 `p1-mon-acnet-pre-20261005T100654/SHA256SUMS` 7개 항목은 압축을 푼 폴더에서 모두 일치했다(`pf.log`와 `SHA256SUMS` 자신은 목록에 없다).
- 압축 파일은 1MB 이하이며 내부 목록은 `registry/ARCHIVE_CONTENTS.json`에 등록했다.
- `ro-control01.tgz.sha256`은 수집 때 개별 sidecar가 없어 **PC에서 계산한 값**이다(수집 때의 `SHA256SUMS`에 있던 `ro-control01.tgz` 해시와 같다).

## 한계
1. 각 파일은 해당 시각의 단일 조회이며 서로 다른 시점의 값을 하나의 동시 측정으로 쓰지 않는다. 특히 10/4 파일과 10/5 파일은 날짜가 다르다.
2. ansible01 출력 저장본이므로 서버 원본과의 바이트 대조는 하지 않았다. `ro-control01.tgz`는 ansible01에서 묶은 사본이다.
3. `ro-control01.tgz` 안의 `mon-discover.txt`는 머리글 시각이 2026-10-02이고 나머지 `p1-mon-acnet-pre-…` 폴더는 2026-10-05 10:06이다. 두 시점을 같은 조회로 쓰지 않는다.
4. `t09-result.txt`는 `dig` 질의 결과이며 `ac-net-run01`(10/5)의 DNS 인수 근거는 [evidence#114](https://github.com/321Team/fds-project-evidence/pull/114)의 원본이다. 이 묶음의 T09는 10/4의 사전 확인이다.
5. 이 PR을 준비한 PC에서는 파일 내용의 사실 대조를 머리글·시각·해시·비밀값 패턴 검색 수준으로만 했다. 개별 수치의 재검증은 하지 않았다.

AI usage: CLAUDE_CODE_ASSISTED.
