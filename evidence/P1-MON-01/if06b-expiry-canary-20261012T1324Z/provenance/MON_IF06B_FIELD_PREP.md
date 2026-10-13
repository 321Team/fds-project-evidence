# MON IF06B 현장 실행 준비 패키지

CLAUDE_ASSISTED · 이권욱 검토용 · 2026-10-12 KST · **r6**. `FOLLOWUP_AND_OVERLAP.md` 권고의 1~3단계 준비물이다. `P1-MON-01` [baseline#17](https://github.com/321Team/fds-project-baseline/issues/17), ICR [#14](https://github.com/321Team/fds-project-baseline/issues/14) AC12·15~17 연계.

**r2 정정(18:12 검토의 R1~R4·C1~C5 반영).** 공급 파일·manifest·해시 후보는 그대로다. 고친 것은 실행 카드와 설명이다: ① `ARMED`는 생성 완료가 아니므로 소유 확정 뒤에만 요청을 보낸다(5.2) ② 시간 예산의 기준점과 "180초 보장" 서술(4.4) ③ T19 보호 복원 조건을 Harbor 비중첩으로 대체한 오류(6절) ④ tmpfs 단정과 관리 키 우선 권고(4.1) ⑤ 수집 범위, preflight 실패 해석, glob, 역할 표, H04 결정의 지위. r1은 SHA256 `b0c284d2…f27c`.

**상태: 로컬 준비만.** 서버 접속·명령 실행·파일 배치·정책 생성/삭제·티켓 게시·담당자 메시지는 0건이다. 아래 명령은 모두 `NOT RUN`인 제안이며 실행 승인이 아니다. 실행기는 이미 병합돼 있으므로 새 코드나 PR은 만들지 않았다.

**r3(18:34 인계 반영).** Codex가 18:33:48 KST에 C1~C7 읽기 수집을 끝냈다(2.1a). 같은 명령을 다시 실행하지 않는다. 실측값을 입력표와 입력 틀에 넣었고, 회차 순서를 `ARMED → watch 시작 → 소유 확정 대기·확인 → lease 확인 → 요청 허용`으로 통일했다(5.2). validate·survival-check·preflight·실제 canary는 여전히 `NOT RUN`이다. r2는 SHA256 `f57f1c03…8b5a`.

**r4(18:54 재검토 반영).** r3에서 새로 쓴 두 설명을 고쳤다: ① `request_timeout`은 HTTP 요청 1건의 예산이며 소유 증적이 기록될 때까지의 상한이 아니다(5.2). 기다림의 끝은 "요청 시작 최종 시점"으로 정한다 ② `preflight` 6건은 그 6건의 검증일 뿐 `.109` 뒤의 모든 backend를 보장하지 않는다(2.1a). 신규 자격증명의 기본 후보를 회차용 ServiceAccount + RBAC + 단기 token으로 바꾸고(4.1), 현재 후보값으로 쓴 실행안 초안 `RUNBOOK_DRAFT.md`를 추가했다. r3는 SHA256 `38b270b6…a0d2`.

**r5(일괄 반영 인계 R1~R5).** 실행 명령은 이제 `RUNBOOK_DRAFT.md`(r2) **한 곳에만** 있다. 이 문서는 근거·의미·순서를 설명하고 명령 위치를 가리킨다. 바뀐 것: 시작 판정이 중단·회수·다른 회차·시간 부족에서 허용을 내지 않게 됨(5.2), 감독 식별 뒤에만 신호(5.2·5.4), RBAC를 한 개씩 만들고 응답으로 소유를 확인(4.1), token은 자동 회수용이고 수동 인수는 기존 관리 인증이라는 점의 통일(4.1), 네 캡처의 분리와 HEP·GNP 전후 명령 연결(5.2·5.3), 시간 후보를 입력표 한 표로(4.4). r4는 SHA256 `476fa80c…78a5`.

**r6(20:41 변경분 검토의 D1·D2).** ① 같은 control01이 재부팅된 뒤에는 감독 식별 도구가 계속 거부하므로, 그 경우의 수동 회수 입구를 따로 두었다(5.4, 실행안 8.2a). ② 캡처 창은 각 캡처의 `timeout`이 시작된 순간부터 세며, 후보 X가 만료 회수와 post-deny까지 덮는다는 r5의 설명은 성립하지 않아 고쳤다(4.4). r5는 SHA256 `75977f0b…0871`.

패키지 구성:

| 파일 | 내용 |
|---|---|
| `MON_IF06B_FIELD_PREP.md` | 이 문서: 입력표, 최소 수집 목록, 결정 사항, 실행 카드, 판정 기준 |
| `supply/` | 병합 커밋에서 꺼낸 실행 파일 6개 + `canary-manifest.json` + `SHA256SUMS` |
| `supply-index.json` | 공급 파일별 크기·SHA-256·Git blob |
| `hash-candidates.json` | manifest·spec 해시 후보와 그 근거 대조 결과 |
| `input.template.json` | 입력 파일 틀. r3에서 API·CA 관측값을 채웠다. 나머지 `<…>`는 선택 뒤 채운다. 이대로는 실행할 수 없는 초안이다 |
| `SESSION_INPUT_SHEET.md` | 회차 입력표 한 장. 수집 결과와 선택을 여기에 모아 한 번에 확정한다 |
| `RUNBOOK_DRAFT.md` | **실행 명령의 유일한 위치**(r3). 공급 배치, 자격증명, validate, survival-check, preflight, 외부 관측, 회차, 인수(재부팅 분기 포함), 정리, 판정 연결. `<…>`가 남아 있어 실행 가능본이 아니다 |
| `rbac/` | 회차용 ServiceAccount·ClusterRole·ClusterRoleBinding 초안과 `SHA256SUMS` |
| `supply-92c182f.tar` | `supply/`의 8개 파일을 LF·0644·root로 묶은 전달용 tar. SHA-256 `8d1630c8…fc20` |
| `tools/` | 읽기 전용 보조 도구 4개(`gate.py`·`ident.py`·`objinfo.py`·`tokeninfo.py`)와 결과 기록기 `record.sh`. API 요청도 신호도 보내지 않는다. `gate.py`는 검토된 교체 명령과 바이트 단위로 같다 |
| `if06b-aux-r1.tar` | `rbac/`와 `tools/`를 묶은 전달용 tar. 코드 tar와 따로 전달한다. SHA-256 `fd5bb7c4…d7ad` |
| `verify_local.py`, `verification-local.json` | 위 도구의 로컬 MOCK, `record.sh`의 실제 동작, 실행안 셸 블록의 구문 확인과 그 결과. 서버 증적이 아니다 |

---

## 1. 공급 기준

기준은 `infra-kubernetes` main **`92c182fc58de999536e56d90012bb2686d9f07cf`**(PR85 병합)이다. `supply/`의 6개 파일은 그 커밋의 Git blob을 그대로 꺼낸 것이라 줄바꿈이 LF다. Windows 작업 사본(CRLF)을 서버에 올리지 않는다.

| 파일 | SHA-256 |
|---|---|
| `coordinator.py` | `70b87a3a6d2341acbbd724a0e99d930d318fa337b94132c8d6f85cd9d9551a03` |
| `decision.py` | `21b8811c814a28415ad5da2276744f12783ff69d667ab6d77d943ab5b5b3f7d3` |
| `journal.py` | `32abeeff990690ecefa7db983c2b9b94c108dc7494f0c18cc3717aff18abaf58` |
| `transport.py` | `b07c433b72ecf12d7ba4f5e3d481cdf74769b0d2b0d8e078778930a92f04670f` |
| `supervisor.py` | `702e88a66fdea8a464df884c0776999b7f48c2dba576c35796f83ccb723333d5` |
| `guardian.py` | `0015a779b04c85718358e361c75da563a17630965655bafab38d4491bdead6ca` |
| `canary-manifest.json` | `48f44146386a324e81a43633a8ad2c83976148a8ceb5c216e58c68ed2e7df90a` (저장소에 없는 파생물, 2.2 참조) |

6개는 한 디렉터리에 함께 있어야 한다(서로 import). 시험 파일·문서는 공급하지 않는다. 서버에서는 `sha256sum -c SHA256SUMS`로 대조하고, 불일치면 그 뒤 단계를 하지 않는다.

---

## 2. 입력표

### 2.1 이미 확보한 사실 — 다시 묻지 않는다

| 항목 | 값 | 출처 · 관측 시점 |
|---|---|---|
| control01 | `10.1.93.102`, EL10, systemd 257, SELinux Enforcing, `/usr/bin/python3.12`·`kubectl` 있음 | Codex 읽기 10/12 11:19~11:33 |
| cluster 식별 | kube-system UID `e1669cff-1435-423f-a6c4-28bc44f488de` | 같은 읽기. `run`·`preflight`가 매번 다시 확인한다 |
| canary 부재 | 정확 이름 GET이 CLI NotFound | 같은 읽기. CLI 관측이며 `run`이 HTTP Status로 다시 확인한다 |
| 보호 경로 부모 후보 | `/var/lib/fds-change` root:root 0700, local XFS, 여유 약 65 GB. `/run`은 tmpfs | 같은 읽기 |
| 세션 | `svc_ansible` Linger=no, logind active | 같은 읽기. 세션 종료 후 생존은 미검증 |
| 요구 수준 | **gateway 구간 귀속**. 특정 rule 귀속(counter/log/nftrace)은 요구하지 않음 | [H04 회신](https://github.com/321Team/fds-project-baseline/pull/160#issuecomment-6083293377) |
| 재사용할 성공 | `.108` Source 보존·wrong-auth 401(증적 122), gateway 정책 원본(증적 151) | [#17 정정](https://github.com/321Team/fds-project-baseline/issues/17#issuecomment-6072071555) |
| 10/6 canary 회차 | 같은 manifest로 생성 16:39:19 → 조건부 삭제 16:42:20 KST(약 3분), 전후 GNP·HEP 불변, `up` 23/23, remote write 실패 증가 0 | 증적 122 `control01/canary-20261006/` |
| 시험 기준 | worker03 `.108` → monitor01 `10.250.10.30`, 443 양성 대조 1회 + 8443 새 연결 1회 | [MON 최소 관측안](https://github.com/321Team/infra-monitoring/blob/0dd0235b07d44ba7965490e3808e0a67a3bd903b/docs/IF06B_REMAINING_TEST_INPUTS_20261009.md), V04 |

### 2.1a control01 읽기 실측 — 2026-10-12 18:33:48 KST (Codex 수행)

경로 `SERVER01 → fds-ansible01 → svc_ansible@10.1.93.102 → sudo -n`, BatchMode·strict host-key, 명령 18개 모두 rc0. host `k8s-control01`, product UUID `80724d56-7c17-f8a0-b2ea-ece7a154e24b`, boot `2a889fe4-51fe-43fe-bcd7-5a0f9b8ff360`(오전 관측과 같은 세대). 게스트에 파일을 두지 않았고 정책 API 요청·credential 출력은 없었다. 원본은 Codex의 `mon-field-read-20261012/control01-C1-C7.json`(SHA256 `e1bbfe0e…3b4b`)이며, 아래는 그 원본을 직접 읽어 대조한 값이다.

| 수집 | 관측 | 쓰임과 한계 |
|---|---|---|
| C1 기존 endpoint | 관리 kubeconfig의 서버 `https://10.1.93.109:6443`. control01에 `*:6443` listener | **`connect_ip=10.1.93.109`, `port=6443`, `tls_server_name=10.1.93.109`** 후보. 기존 경로를 유지하고 `.102` 직접 접속으로 바꾸지 않는다 |
| C1 인증서 | control01 apiserver 인증서 SAN: IP `10.96.0.1`·`10.1.93.102`·`10.1.93.109`, DNS `k8s-control01`·`kubernetes…`. 만료 2027-09-09 21:34:59 KST | control01의 파일을 읽은 것이다. `.109`가 실제로 내놓는 인증서의 온라인 검증은 `preflight`에서 한다 |
| C2 CA | `/etc/kubernetes/pki/ca.crt` root:root 0644 1107 B, SHA256 `5e4462b48b67aa3c452119f02578feb5b2ace358782c9b050ba0ad2ea951a49c` | `ca_file`·`ca_sha256` 후보. MON 목적지용 Root CA(`20ddfa5e…`)와 다른 것이다 |
| C3 자격증명 목록 | `/etc/kubernetes/` 아래 `admin.conf`·`super-admin.conf`·`kubelet.conf`·`controller-manager.conf`·`scheduler.conf`, 모두 root 0600 | 내용은 읽지 않았다. 이 디렉터리에 guardian 전용 파일은 보이지 않지만, 이것으로 한정 자격증명의 부재·권한·수명을 확정하지 않는다. 시스템 구성요소 자격증명을 쓰자는 뜻이 아니다 |
| C4 세션 종료 정책 | D-Bus 유효값 `KillUserProcesses=false`, `KillOnlyUsers`·`KillExcludeUsers` 비어 있음. 설정 파일에 활성 `Kill*` 행 없음. `svc_ansible` Linger=no, 세션 2개 | A안 후보 유지. 로그아웃 뒤 생존은 `survival-check`를 해야 안다 |
| C5 보호 경로 부모 | `/var/lib/fds-change` root:root 0700, label `var_lib_t`, local XFS. 자식은 `CR-P1-NTP-01-01`·`ssh-pr4` | 4.3의 제안 이름과 충돌 없음. 새 경로 생성·label 적합성은 아직 확인하지 않았다 |
| C6 실행 환경 | Python 3.12.14, OpenSSL 3.5.8, `CLOCK_BOOTTIME` 있음 | 실행기 요구(3.10+) 충족 |
| C7 swap | `/proc/swaps`에 항목 없음. `/run`은 tmpfs | 그 시점의 사실이다. 키 사본을 허용한다는 뜻도, 메모리 흔적이 없다는 증거도 아니다 |

**`.109`와 `preflight`의 검증 범위:** 기존 관리 endpoint `.109:6443`과 고정 CA·검증 이름을 유지한다. 실행기는 요청마다 새 연결을 맺고, 그때마다 **실제로 연결된 TLS 상대**에 대해 CA와 이름을 검증한다. TLS가 backend까지 전달되는 구성이면 그 backend의 인증서가, 중간에서 끝나는 구성이면 그 지점의 인증서가 검증 대상이다. `.109`가 어느 쪽인지, backend가 무엇인지는 이번 조회 범위 밖이다. `preflight`의 6건 성공은 그 6건의 근거이며 backend 전체나 이후 모든 연결의 성공을 보장하지 않는다. 회차 중에도 요청마다 검증이 유지되고, 실패하면 기존 인수 절차를 따른다. `transport_last`는 마지막 요청의 기록이므로 `method`와 `stage`를 함께 본다. 이 불확실성을 이유로 `.102` 직접 접속으로 바꾸거나 TLS 검증을 풀지 않으며, 부하분산기 조사를 이 회차의 필수 작업으로 더하지 않는다. (r3의 "모든 backend 인증서에 `.109`가 있어야 한다"와 "6건으로 확인한다"는 서술은 TLS가 끝나는 위치를 가정한 것이라 철회한다.)

### 2.2 이번에 계산한 후보 — 검토가 필요하다

| 항목 | 후보 값 | 근거와 한계 |
|---|---|---|
| manifest JSON | `supply/canary-manifest.json` | 검토 후보 YAML(8ecbc34 이후 변경 없음)을 JSON으로 옮긴 것. 18:12 검토(Codex)가 PyYAML 6.0.3 SafeLoader로 원본 YAML을 읽은 객체와 완전히 일치함을 확인했다 |
| `reviewed_manifest_sha256` | `0602b0001405a9929f3b8d91dc6a2b9175c5811531a6eab930e50520b2f6d37f` | 공급 대상 `coordinator.manifest_hash`로 계산. 서버에서 `validate`가 같은 값을 다시 계산해 보여 준다 |
| `reviewed_spec_sha256` | `4b5599c45f99528dc1e0f02216bd220afd3789af39db38159e718488d53b8146` | 10/6 실제 생성 응답(증적 122 `04-create.json`)의 spec 해시. **제출 spec 해시와 같다**(당시 서버가 기본값을 더하지 않음). `preflight`의 dry-run으로 다시 확인해야 확정된다 |

대조 결과(`hash-candidates.json`):

- 저장소 YAML이 10/6에 실제 적용한 `canary.yaml`과 바이트 단위로 같다.
- 10/6 서버 응답의 spec과 annotations가 JSON 옮김과 같다. 서버가 YAML을 해석한 결과와 일치하므로 옮김 오류 가능성은 낮다.
- 서버가 metadata에 더한 키는 `creationTimestamp`·`generation`·`resourceVersion`·`uid`뿐이었고, 병합된 `decision.owned_receipt`가 그 응답을 소유 근거로 받아들인다(finalizer 없음).
- 18:12 검토의 독립 canonical JSON 계산이 두 후보와 일치했고, 10/6 응답을 `decision` 함수에 넣은 정적 재생도 OWNED였다. 과거 응답의 재생이며 새 Runtime 증거는 아니다.
- 한계: 10/6 이후 Calico·CRD·admission이 바뀌었다면 응답이 달라질 수 있다. 두 해시는 **계속 후보**이며 자동 승인값이 아니다.

### 2.3 미확정 — 수집(C) 또는 회차 입력(D)

아래는 따로따로 승인받을 7건이 아니다. 수집 결과를 넣어 `SESSION_INPUT_SHEET.md` **한 장**에서 함께 확정한다. 핵심 미확정은 두 가지다: **사용할 자격증명(D1)** 과 **실제 콘솔 인수가 가능한지(D5)**.

| # | 항목 | 종류 | 채우는 방법 |
|---|---|---|---|
| 1 | API 접속 IP·포트, 인증서 이름 | 수집 완료(후보) | 2.1a. `preflight`로 확정 |
| 2 | CA 파일 경로·SHA-256 | 수집 완료(후보) | 2.1a |
| 3 | 사용할 자격증명 | **결정 D1** | 4.1 |
| 4 | 세션 종료 후 생존, 실행 구조 | C4 수집 완료 + `survival-check` 미실행 + **결정 D2** | 2.1a, 4.2 |
| 5 | journal·증적 디렉터리 2개, 공급 경로 | **결정 D3** | 4.3 |
| 6 | 시간 예산 5개 + watch 2개 | **결정 D4** | 4.4 |
| 7 | 회수 인수자, abort 전달자, 관측 담당·계정 | **결정 D5** | 4.5 |
| 8 | 회차 시각(Harbor·다른 작업과 비중첩) | **결정 D6** | 5.0 |

---

## 3. 최소 수집 목록 (control01, 읽기 전용) — 18:33:48 수집 완료

**이 절의 명령은 이미 실행됐다(2.1a). 다시 실행하지 않는다.** 뒤에 변경이나 drift가 의심되는 항목만 그 항목에 한해 다시 읽는다. 실제 실행에서는 `loginctl show-session` 대신 `loginctl show-user svc_ansible`을 읽었고(sudo 환경의 세션 ID를 추정하지 않기 위해), endpoint 조회에는 `--minify`를 썼으며, C7에 `/run` mount 조회가 더해졌다. 아래는 계획했던 명령의 기록이다.

기존 `svc_ansible`+`sudo -n` 경로의 **MON 전용 새 세션**에서 실행한다. Harbor 작업이 쓰는 세션을 건드리지 않는다. 파일을 만들거나 바꾸지 않으며, 인증서·키·kubeconfig의 **내용을 출력하지 않는다**.

```text
# C1 — apiserver 접속 주소와 인증서 이름. 셋째 줄은 기존 관리 경로가 쓰는 endpoint만 읽는다(비밀값 없음)
sudo -n ss -ltn 'sport = :6443'
sudo -n openssl x509 -in /etc/kubernetes/pki/apiserver.crt -noout -ext subjectAltName -enddate
sudo -n kubectl config view --kubeconfig=/etc/kubernetes/admin.conf -o jsonpath='{.clusters[0].cluster.server}'

# C2 — CA
sudo -n stat -c '%n %U:%G %a %s' /etc/kubernetes/pki/ca.crt
sudo -n sha256sum /etc/kubernetes/pki/ca.crt

# C3 — 있는 자격증명의 목록만(메타데이터). 내용은 읽지 않는다
sudo -n find /etc/kubernetes -maxdepth 1 -type f -name '*.conf' -printf '%p %u:%g %m %s %TY-%Tm-%TdT%TH:%TM:%TS\n'

# C4 — 세션이 끝날 때 프로세스를 죽이는지
busctl get-property org.freedesktop.login1 /org/freedesktop/login1 org.freedesktop.login1.Manager KillUserProcesses
systemd-analyze cat-config systemd/logind.conf | grep -i -E '^(KillUserProcesses|KillOnlyUsers|KillExcludeUsers)'
loginctl show-session "$XDG_SESSION_ID" -p Id -p Type -p Remote -p Scope

# C5 — 보호 경로 부모
sudo -n stat -c '%n %U:%G %a %F' /var/lib/fds-change
sudo -n ls -Zd /var/lib/fds-change
sudo -n ls -la /var/lib/fds-change
findmnt -T /var/lib/fds-change -o TARGET,FSTYPE,OPTIONS

# C6 — 실행 환경
/usr/bin/python3.12 -c 'import ssl,sys,time; print(sys.version.split()[0], ssl.OPENSSL_VERSION, hasattr(time,"CLOCK_BOOTTIME"))'

# C7 — swap 사용 여부(자격증명 임시 파일의 위치 판단용)
cat /proc/swaps
```

| 수집 | 채워지는 입력 | 기대와 판단 |
|---|---|---|
| C1 | `connect_ip`, `port`, `tls_server_name` | **결과: 기존 관리 endpoint가 `10.1.93.109:6443`이고 SAN에 있다. 그 값을 유지한다.** SAN과 listener만으로 승인된 접속 경로가 정해지지는 않으므로 `.102` 직접 접속으로 바꾸지 않는다(r1의 `.102` 권고는 철회). 인증서 만료는 2027-09-09 |
| C2 | `ca_file`, `ca_sha256` | 파일은 root 소유이고 group/other 쓰기 불가여야 한다 |
| C3 | D1의 선택지 | 파일 목록은 자격증명의 종류·주체·권한 범위를 증명하지 않는다. 출력이 비었거나 rc≠0이어도 부재로 단정하지 않는다. 선택한 자격증명의 실제 권한은 `preflight`의 접근 검토 결과로 연결한다 |
| C4 | D2 | `KillUserProcesses=false`(EL 기본)는 A안의 필요조건일 뿐 생존의 증명이 아니다. 증명은 전용 세션 `survival-check`다. `true`이거나 판단이 안 서면 B안 |
| C5 | D3 | 하위 경로 이름 충돌이 없는지, SELinux label |
| C6 | 실행 가능 여부 | 3.10 이상, `CLOCK_BOOTTIME` True |
| C7 | D1 | swap이 켜져 있으면 tmpfs의 내용도 디스크에 기록될 수 있다. 꺼져 있다는 관측은 그 시점의 사실일 뿐이다 |

kube-system UID와 canary 부재는 여기서 다시 읽지 않는다. `preflight`와 `run`이 인증된 요청으로 직접 확인한다.

### 3.1 control01 밖의 회차 입력

C1~C7은 control01 쪽 입력의 일부다. **"control01 수집 완료"와 "회차 입력 전체 확정"은 다르다.** 아래는 기존 [MON 최소 관측안](https://github.com/321Team/infra-monitoring/blob/0dd0235b07d44ba7965490e3808e0a67a3bd903b/docs/IF06B_REMAINING_TEST_INPUTS_20261009.md) 3절과 canary 카드가 요구하는 값이며, 새로 만든 조건이 아니다. 현장 값만 채운다.

| 위치 | 필요한 입력 | 이미 있는 근거 |
|---|---|---|
| worker03 `.108` | 정상 접근 경로, `route get`의 src·출발 인터페이스, 회차별 고정 출발 TCP 포트 2개의 가용성, 도구 버전 | 기존 접근은 `server07`. 10/6에 `src 10.1.93.108` 관측(증적 122) |
| worker03 → monitor01 TLS | 승인 CA 파일과 해시, 검증할 이름, live `GET /`의 기대 응답 | 카드: 승인 Root SHA-256 `20ddfa5e…053f`, IP SAN `.30`으로 검증. 승인 nginx 소스는 `/`에 404. live 설정은 회차에서 확인 |
| mgmt-gw01 `.58` | physical·management 인터페이스의 실제 대응, 현재 정책·route·NAT, 관측 계정과 sudo/콘솔 | 증적 151: 10/8 정책 원본(`.108→.30 tcp443` 단일 allow, 그 밖은 DROP). 10/8의 인증을 오늘 것으로 재사용하지 않는다 |
| monitor01 `.30` | 수신 인터페이스, listener, firewalld runtime/permanent, 관측 계정 | 카드: `ens160`, 헤더 전용 캡처 절차와 종료 코드 보존 방식 |
| 세 관측 지점 공통 | 캡처 필터, 권한, 시작·종료 시각, captured/received/dropped 통계, 시계 정합 | 카드 3절의 필터와 유효성 Gate를 재사용 |

---

## 4. 회차 입력으로 함께 확정할 것

이미 인수한 Phase 1 실행 범위 안의 값이며, 항목마다 새 승인을 받는 절차가 아니다. 한 장의 입력표로 확정한다. 새 credential 사본이나 새 RBAC처럼 **실제로 새 권한 행위가 필요한 것만** 구체적 범위로 따로 확인한다.

### 4.1 D1 — 자격증명 (핵심 미확정 1)

실행기는 **bearer token 파일** 또는 **client 인증서·키 파일**만 받는다. kubeconfig를 직접 읽지 않는다. 지금까지 확인된 기존 자격증명은 관리 kubeconfig뿐이고, 이 canary만 다루는 한정 자격증명이 있다는 기록은 찾지 못했다.

| 안 | 내용 | 새로 생기는 것 | 고려할 점 |
|---|---|---|---|
| 가 | 관리 kubeconfig의 client 인증서·키를 회차 동안만 파일로 꺼내 쓰고, 회차 뒤 삭제·부재 확인 | cluster 객체 0. 관리 키의 임시 사본 1쌍 | 10/6 회차와 카드가 쓴 권한과 같다. **실행기의 고정 요청 목록은 그 키 자체의 권한을 줄이지 않는다.** tmpfs에 두어도 swap으로 디스크에 기록될 수 있고(C7), 파일을 지우는 것은 인증서 폐기가 아니다. 키 사본 생성은 INTEGRATION이 별도 변경 범위로 둔 행위다 |
| 나 | 회차용 ServiceAccount + ClusterRole/Binding을 만들고 TokenRequest로 단기 token 발급, 회차 뒤 삭제 | cluster 객체 3개 + token | 권한이 가장 좁다. 10/6 PF 회차에 같은 방식의 선례가 있다(증적 122 `run-20261006T1625`). 다만 create는 RBAC로 이름 제한이 안 되고, **kube-system namespace `get` 권한도 줘야 한다**(실행기가 cluster UID를 확인하므로). 새 RBAC manifest·리뷰가 필요한 별도 변경이다 |
| 다 | 이미 있는 한정 자격증명 사용 | 없음 | C3와 담당자 확인에서 실제로 있을 때만 |

**C3 실측과의 관계:** `/etc/kubernetes/` 바로 아래에는 관리·시스템 구성요소용 kubeconfig 5개만 있었다(2.1a). 다 안에 해당하는 파일이 그 위치에서 보이지 않았다는 사실일 뿐, 다른 위치나 cluster 안의 기존 ServiceAccount까지 없다는 뜻은 아니다. C7에서 활성 swap은 없었지만 그것이 가 안을 허용하는 근거는 아니다.

**선택 순서(r1의 "가 우선" 의견은 철회한다):**

1. 먼저 지금 쓸 수 있는 자격증명의 경로·발급 주체·용도·유효기간·허용 범위를 비밀값 없이 확인한다. 실행기에 맞는 승인된 파일이 이미 있으면 그것을 쓴다(다). 파일 목록만으로 한정 자격증명이 없다고 단정하지 않는다.
2. 새로 준비해야 한다면 **기본 후보는 나**(회차용 ServiceAccount + 필요한 범위의 RBAC + 단기 TokenRequest)다. 자동으로 도는 주체의 권한과 수명을 관리 키 사본보다 좁힐 수 있기 때문이다. 채택 제안이지 객체 생성 허용이 아니다. 구체 초안은 `RUNBOOK_DRAFT.md` 2절과 `rbac/`에 있다.
   - 최상위 create는 RBAC로 이름 제한이 안 되므로 "이 canary만 만들 수 있는 credential"이라고 쓰지 않는다. 그 token은 유효한 동안 어떤 GlobalNetworkPolicy든 만들 수 있다. 통제는 고정 manifest, 짧은 수명, 보호 저장, 회차 뒤 삭제다.
   - token의 요청 TTL을 실제 TTL로 가정하지 않고 발급 결과의 `exp`를 읽는다. token이 만료·소실돼도 콘솔 인수자가 **기존 별도 관리 인증**으로 회수할 수 있어야 한다.
3. 가를 고른다면 대상 키·호스트·보호 경로·사용 기간·삭제와 부재 확인·실패 시 인수 방법을 적고, 그 사본 생성 범위의 허용을 확인한다. 보안 설정(swap 등)을 임의로 바꾸지 않는다.
4. 나를 고른다면 token은 **감독의 자동 회수 예산**을 덮어야 한다. token이 만료·소실돼도 콘솔 인수자는 기존 별도 관리 인증으로 회수한다. 인수가 끝날 때까지 임시 token 하나에 의존하지 않는다.(r4의 "만료된 token으로는 감독도 인수자도 삭제할 수 없다"는 틀린 서술이라 고쳤다.)
5. RBAC 객체 3개는 한 번에 만들어지지 않는다. 한 개씩 만들고 **생성 응답**으로 소유를 확인한 뒤 다음으로 가며, 중간에 실패하거나 응답이 불확실하면 뒤 객체·token·run을 하지 않는다. 정리는 응답으로 소유가 확인된 객체만, 현재 UID가 같을 때만 한다(`RUNBOOK_DRAFT.md` 2.3·2.6).

같은 범위가 이미 허용돼 있다면 다시 승인받지 않는다. 어느 안이든 credential 값은 문서·채팅·증적에 남기지 않는다.

### 4.2 D2 — 실행 구조

| 안 | 조건 |
|---|---|
| **A (권장)** `run` 기본 — 세션을 떠난 프로세스 | C4는 `KillUserProcesses=false`로 관측됨(2.1a). 남은 조건은 `survival-check` 통과 |
| B 콘솔에서 `run --foreground` | VMware 콘솔 세션을 회차 끝까지 유지할 담당자 |
| C `systemd-run` transient unit | 새 systemd 단위라 별도 허용 |

A를 택해도 B의 콘솔은 **인수 경로**로 필요하다(감독이 죽었을 때 수동 회수).

### 4.3 D3 — 경로

제안(부모는 관측된 `/var/lib/fds-change`, 이름은 제안일 뿐):

```text
/var/lib/fds-change/if06b-<S>/              회차 경로 SES (0700). 새로 만들어질 때만 쓴다
    supply/                                  코드 6개 + canary-manifest.json + SHA256SUMS (0644, root)
    aux/rbac/  aux/tools/                    RBAC 초안 3개, 읽기 도구와 기록기 (0644, root)
    journal/                                 0700, 비어 있어야 함. 다른 파일을 두지 않는다
    evidence/                                0700, journal과 다른 디렉터리
    results/                                 0700, 단계별 .time .out .err .rc
    input.json                               0644, root
/var/lib/fds-change/if06b-survival-<S>/     생존 시험 전용 SURV (0700). SES와 다른 경로
/run/fds-if06b-<S>/                         token 경로 TOK (0700, tmpfs). 신규 SA 방식일 때만
```

C5 실측에서 부모의 기존 자식은 `CR-P1-NTP-01-01`·`ssh-pr4`뿐이라 위 이름과 겹치지 않는다. 새 디렉터리의 SELinux label이 부모와 같게 잡히는지는 만들 때 확인한다.

디렉터리 생성과 파일 배치는 control01에 대한 쓰기다. 세 경로 모두 **새로 만들어지는 것을 확인**하며(이미 있으면 `mkdir`가 실패), 기존 것을 지우거나 다시 쓰는 동작은 없다. journal 디렉터리는 회차마다 새것이어야 하고 한 번 쓴 것은 다시 쓸 수 없다(실행기가 거부). 부모가 root 0700이므로 그 아래의 glob·`cd`·리다이렉션은 root 셸 안에서만 한다. 전달물은 코드 tar와 보조 tar(`rbac/`+`tools/`) 두 개이고 따로 대조한다(`RUNBOOK_DRAFT.md` 0.1·1절).

### 4.4 D4 — 시간 예산

기본값은 없다. 실행기가 강제하는 제약은 `lease > request_timeout`과 `cleanup_window > 3 × request_timeout + readback_delay`뿐이다. 각 값의 뜻:

| 예산 | 뜻 |
|---|---|
| `lease_seconds` | `ARMING` 기록 직전에 잡은 기준 시각부터 `expires_mono`까지. journal 기록과 생성 요청에 쓰인 시간이 여기서 빠지므로 **실제 시험 가능 시간은 더 짧다.** `complete`/`abort`는 회수를 앞당길 뿐이다 |
| `cleanup_window_seconds` | `expires_mono`부터 `cleanup_deadline_mono`까지의 추가 API 처리 예산. **조기 회수를 시작한 시점부터 다시 세는 값이 아니다** |
| `request_timeout_seconds` | HTTP 요청 1건의 연결~응답 절대 기한. `ARMED`부터 소유 증적이 기록될 때까지의 상한은 아니다 |
| `observation_max_age_seconds` | 삭제 직전 GET 결과를 믿는 최대 나이. GET이 이보다 오래 걸리면 삭제하지 않고 HANDOFF |
| `readback_delay_seconds` | DELETE 뒤 확인 GET까지 대기. 이 시간이 서버의 삭제 완료를 보장하지 않는다. 판단은 실제 readback 결과를 따른다 |

**숫자는 `SESSION_INPUT_SHEET.md`의 "시간 후보" 한 표에서 한 번에 채택한다.** 그 표는 MON 최소 관측안의 원래 제안(캡처 최대 120초 · 무시험 배경 20초 · 두 요청 20초 이내 · 후관측 20초 · canary 180초), 그 숫자를 유지하는 후보 X(lease 90), r4까지 쓰던 후보 Y(lease 120 · 회수 60 · 시험 30 · 캡처 200초 초과)를 나란히 둔다. 120초는 제안값이어서 후보를 고르는 것이 새 AC 변경은 아니다.

**캡처 창의 기준점.** 각 캡처의 창은 **그 캡처의 `timeout`이 시작된 순간부터** 센다. t0는 네 지점의 준비를 서로 확인한 시각일 뿐, 타이머를 다시 시작하는 시각이 아니다. 먼저 켠 캡처는 t0 전에 이미 시간이 줄어든다. 네 캡처에 공통으로 유효한 관측 구간은 **가장 늦게 준비된 시각부터 가장 먼저 끝난 시각까지**다.

후보 X(lease 90)는 원안의 캡처·요청·후관측 숫자를 유지한다. 그러나 `run`의 사전 읽기 2건, 사람 사이의 전달, 만료에 의한 회수, post-deny가 모두 그 구간에 들어온다는 보장은 없다. **X는 관측 범위가 제한될 수 있음을 받아들일 때 고르는 후보다.** 시험이 일찍 끝나 완료 신호로 회수하는 회차는 들어갈 수 있지만, 만료까지 가는 회차는 벗어날 수 있다. 만료 회수와 post-deny까지 관측하려면, 캡처 창 후보에 **각 캡처의 시작 시각 차이 + `run` 사전 GET 2건 + lease + cleanup_window + post-deny + 전달 여유**를 넣어 입력표에서 한 번에 고른다. 숫자는 제안값이며 새 AC를 만들지 않는다. 실제 지연과 파일 동기화에는 끝나는 시각의 보장이 없다. 합성 예는 실행안 6.0에 있다. (r5는 X를 "만료 회수와 post-deny까지 120초 안에 드는 조합"이라고 썼는데, 캡처 창의 기준점을 t0로 잘못 잡고 `run`의 사전 읽기를 빼고 계산한 것이어서 철회한다.)

lease와 회수 window는 **API 처리 예산**이다. 그 합(예: 150초, 180초) 안에 삭제나 인수가 끝난다는 보장이 아니다: 파일 동기화 지연, 감독의 강제 종료, 재부팅은 이 예산 밖이다. `watch`의 감시 창도 `watch`를 띄운 시점부터 세는 별도의 창이다. 캡처 창은 또 다른 기준점, 곧 각 캡처의 `timeout`이 시작된 시각에서 센다.

그래서 인수자는 `watch`와 별개로 그 회차의 만료·회수 기한 시각을 알고 있어야 한다. 감독 소실, HANDOFF, 또는 기한이 지나도 종결이 확인되지 않으면 새 시험 요청을 멈추고 콘솔 인수 절차(5.4)로 넘어간다. 이때 늦게 도착하는 기존 요청이 있을 수 있음을 염두에 두고, 자동 재전송이나 감독과 동시에 하는 삭제는 하지 않는다.

어느 후보든 배경 구간, 소유 대기, 시험과 후관측, 회수, post-deny가 **네 캡처의 공통 유효 관측 구간** 안에 들어왔는지를 회차 뒤에 시각으로 판단한다. 벗어난 부분은 `NOT_VERIFIED`이고 추가 시험 없이 회수한다. lease와 캡처 창을 현장에서 늘리지 않는다. 참고로 10/6 수동 회차의 실제 존속은 약 181초였다.

### 4.5 D5 — 역할과 전달 (핵심 미확정 2: 콘솔 인수 가능 여부)

아래는 책임의 구분이지 다섯 명을 새로 지정·승인하는 절차가 아니다. 이미 인수한 실행 범위 안에서 **겸임할 수 있다.** 다만 네 지점의 동시 관측과, 장애 때 콘솔 인수가 실제로 가능해야 한다. 회차 표 한 장에 역할별 실행자·대체 연락·인수 경로를 적는다.

| 역할 | 필요한 것 | 지금 상태 |
|---|---|---|
| control01 실행자 | `run`, 소유 확정 확인, 신호 전송 | 회차 표에 기록 |
| 회수 인수자 | 콘솔에서 수동 조건부 회수가 **실제로 가능한** 사람과 경로. `watch`를 `ARMED` 직후 띄우고 종료 코드 3을 인수 신호로. 만료·회수 기한 시각을 알고 있을 것 | **후보: 이권욱**(이미 맡은 Phase 1 실행 책임에 따른 가장 단순한 안). control01 콘솔 로그인·sudo·기존 관리 API 인증을 지금 실제로 쓸 수 있는지는 **미확인**이다. SSH 읽기 성공은 콘솔 가용성의 근거가 아니다. 불가능할 때만 다른 실제 콘솔 운영자를 연결한다 |
| MON 관측자 | 기준선·abort 판단 | 이재환 제안 있음(아래), 채택은 미정 |
| worker03 요청자 | `server07` 경로에서 443·8443 요청. **소유 확정 통보를 받은 뒤에만** | 회차 표에 기록 |
| gateway·monitor01 관측자 | 헤더 캡처, 계정·sudo/콘솔 | 회차 표에 기록. 10/8의 gateway 인증을 오늘 것으로 재사용하지 않는다 |

MON Lead의 abort 제안(결정 아님): 회차 중 `count(up==1)`이 기준선 23에서 감소, heartbeat 60초 이상 단절, `prometheus_remote_storage_samples_failed_total` 증가. 셋 중 하나면 관측자가 실행자에게 알리고 실행자가 `kill -USR1 <pid>`.

원격 알림(Alertmanager/Discord)은 만들지 않는다. 전달은 `watch` 출력·종료 코드와 사람 사이의 직접 연락이다.

---

## 5. 실행 카드

### 5.0 시작 조건 — Harbor·다른 작업과의 구간 분리

| 단계 | Harbor 변경과 같은 시간대 | 조건 |
|---|---|---|
| 공급·`validate` | 가능 | MON 전용 세션. control01 쓰기는 D3 허용 뒤 |
| `survival-check` | 가능 | **이 시험을 위해 연 세션만** 닫는다. `loginctl terminate-user`나 다른 세션 종료 금지(Harbor가 같은 `svc_ansible` 계정을 쓴다) |
| `preflight` | 조건부 | 실제 API 요청 6건(읽기 2, 접근 검토 3, dry-run 1). 영속 쓰기 0 |
| **`run`(실제 canary)** | **불가** | Harbor 주소 적용·앱 재생성·복구/장애시험·worker 검증과 사후 관측이 끝났고, 다음 H6·worker·정책 변경과 겹치지 않는 구간. 실패 상태가 미정이거나 복구 중이면 보류. Harbor 전체 AC 종결을 기다릴 필요는 없다 |

회차 직전에 다시 확인할 것: T19 보호 복원 이후의 변경과 현재 기준선 안정(6절), 다른 K8S·네트워크·APP 작업 없음, worker03 HEP·host GNP의 UID/RV(10/6 값과 같을 필요는 없고 기록만), 같은 selector·order 90의 다른 GNP 없음.

### 5.1 준비 검증

명령은 `RUNBOOK_DRAFT.md`에 있다. 여기에는 순서와 통과 기준만 둔다.

| 순서 | 실행안 위치 | 통과 기준 | 중단 |
|---|---|---|---|
| P1 공급 배치 | 1절 | 두 tar의 해시 일치, 새 경로 생성 성공, `SHA256SUMS` 대조 통과 | 경로가 이미 있음(지우거나 재사용하지 않는다), 해시 불일치 |
| P2 `validate` | 3절 | rc 0, `passed=true`, `network_requests=0`, `computed_manifest_sha256`이 2.2의 후보와 같음 | rc 5(어느 검사가 `false`인지), rc 2(입력·파일 오류) |
| P3 `survival-check` (A안) | 4절 | 그 시험을 위해 연 세션을 닫은 뒤에도 `BEAT`가 이어지고 `FINAL`이 있음 | `BEAT`가 세션 종료 시각에 끊김 → B안 |
| P4 `preflight` | 5절 | rc 0, `passed=true`, `persisted_writes=0`, 5개 check 모두 `PASS`, `defaulted_spec_sha256`이 pin과 같음 | 아래 |

P4가 실패하면:

- `cluster_and_absence`가 `CLUSTER_CHANGED` → 대상이 다르다. 전부 중단.
- `CANARY_ALREADY_PRESENT` → 누가 만든 객체인지 조사. 삭제하지 않는다.
- `access_*`가 `FAIL` → D1의 권한이 부족하다. 회차를 열지 않는다(생성은 되고 삭제가 안 되는 상황을 피하려는 검사다).
- `dry_run_spec_pin`이 통과하지 않음 → 원인을 먼저 구분한다. `FAIL`이고 `defaulted_spec_sha256`이 출력됐으면 **spec 해시 불일치**다. `DRY_RUN_REJECTED`면 dry-run 응답 조건 위반(201이 아님, 이름·kind 불일치, finalizer 있음)이고, 그 밖의 코드는 응답 형식이나 연결 문제다. 해시 불일치의 원인은 기본값 추가일 수도, admission 변형이나 CRD 변경일 수도 있으니 단정하지 않는다. 새 해시를 자동으로 채택하지 않으며, 원인이 확인되고 검토된 변경일 때만 입력을 고친다.
- TLS·연결 오류(`OS_ERROR`·`TIMEOUT`) → C1·C2 값 재확인.

P3·P4를 회차 당일 무조건 다시 할 필요는 없다. 다만 그 뒤 **관련 입력이 바뀌었으면 영향받는 검증만 다시 한다**: reboot, 인증서·CA·endpoint 교체, credential 교체나 만료, RBAC·admission 변경, Calico·CRD 변경, manifest 변경. `run`은 cluster 식별과 canary 부재만 다시 확인하고, 권한 3종과 dry-run은 다시 하지 않는다.

### 5.2 회차

아래는 순서와 역할이다. 명령·출력·판정표는 `RUNBOOK_DRAFT.md` 7절(회차)과 6절(관측)에 있고 여기에 복제하지 않는다. 숫자는 입력표의 시간 후보를 따른다.

| 시점 | 누가 | 무엇 |
|---|---|---|
| T−α | MON 관측자 · control01 실행자 | 기준선 기록: `up` 수, remote write 실패 증가, heartbeat, monitor01 listener·firewalld runtime/permanent, gateway 정책 수집, **worker03 HEP·host GNP의 UID/RV/spec와 GNP 목록**(실행안 6.1) |
| T−α | 관측자들 | **네 지점**(`worker-out`·`gateway-in`·`gateway-out`·`monitor-in`)에서 헤더 캡처 시작. 지점마다 터미널과 결과 디렉터리가 다르다(실행안 6.2). 준비 표시를 실행자에게 알린다. 하나라도 준비 실패면 **`run`을 치지 않는다** |
| T | 실행자 | token 수명과 boot 재확인(7-0) → `run`(7-1) → `ARMED`. **`ARMED`와 launcher rc 0은 생성도 회수도 아니다** |
| `ARMED` 직후 | 인수자 | `watch`를 바로 띄운다(7-2). 소유 확정을 기다리지 않는다. 락 보유는 감독이 건강하다는 보장이 아니다 |
| 그다음 | 실행자 | **시작 판정**(7-3 `gate.py`). `SNAPSHOT_ELIGIBLE`이 나올 때까지 로컬 증적만 다시 읽는다. `WAIT_…`는 대기, `STOP_…`은 새 요청 금지 |
| 그다음 | 실행자 | 시작 전달 조건 네 가지(7-3)를 모두 볼 때만 요청자에게 **시작을 전달**. 전달 뒤에도 `watch` 결과와 abort를 요청자에게 바로 넘긴다 |
| 시작 전달 뒤 | worker03 요청자 | `route get`의 src 확인 → 443 양성 대조 1회 → **8443 직전에 실행자가 다시 판정** → 8443 새 연결 1회(6.3). 재시도 없음 |
| 요청 뒤 20초 | 관측자들 | 후관측 |
| 그 뒤 | 실행자 | **감독 식별**(`ident.py`) 뒤 완료 신호(7-4). `GUARDIAN_ALIVE`가 아니면 신호를 보내지 않는다 |
| 자동 | 감독 | GET → 조건부 DELETE 1회 → readback |
| 끝 | 인수자 | `watch` 종료 코드 확인 |

**소유 확정 없이 요청을 보내지 않는다.** `ARMED`는 CREATE_INTENT 기록 뒤, 실제 POST **전**에 나온다. 생성이 실패하거나 시간을 넘기거나 spec이 다르면 그 뒤에 HANDOFF가 된다. 그 상태에서 443/8443을 보내면 canary가 없거나 소유가 미확정인 채로 결과를 모으게 되어, 정상 차단과 생성 실패를 구분할 수 없다.

- **기다림의 끝은 "요청 시작 최종 시점"이다.** `request_timeout`은 HTTP 요청 1건의 전송 처리 예산이며, `ARMED`부터 `CREATE` 증적이 기록될 때까지의 상한이 아니다(응답 뒤의 journal 동기화와 증적 기록은 그 예산 밖이다). `CREATE` 행이 아직 없으면 `watch`를 유지하면서 이 회차의 로컬 증적만 읽는다. POST를 다시 보내지 않는다.
- **요청 시작 최종 시점 = `expires_mono` − (확정한 시험 소요 + 후관측 소요).** 회차 카드에서 계산해 두며, 늦어도 lease를 늘리지 않는다. 그 시점에 이르렀거나 남은 시간이 모자라면 새 트래픽을 보내지 않는다. 계산 명령은 `RUNBOOK_DRAFT.md` 7-3에 있다.
- **새 요청을 보내지 않는 경우:** 증적에 `TRIGGER`·`CLEANUP`·`READBACK`·`FINAL` 중 하나가 있음, 마지막 행이 덜 쓰였음, 다른 session·cluster·boot의 기록임, 감독이 `ARMING`에 적힌 그 프로세스가 아님, `CREATE`가 `OWNED`+UID+RV가 아님, 시험+후관측 시간이 모자람, `watch`가 인수 결과를 냈음, **이 회차에 abort를 이미 보냈음(그 행이 아직 없어도)**.
- 판정의 "허용"은 읽은 순간의 진단이다. 그 뒤의 생존을 보장하지 않으므로 감시 유지·중단 전달·다음 요청 직전 재판정으로 틈을 좁힌다.
- 중단되기 전에 이미 나간 요청이 있으면 "요청 0건"이라고 적지 않고 실제 횟수를 적는다.
- 기다림이 끝났다는 것이 POST 실패·미전송이나 소유 해제를 뜻하지는 않는다. **진행 중인 감독과 동시에 수동 DELETE를 보내지 않는다.**
- HANDOFF의 `unowned_create_response`에 있는 진단 UID는 소유 증거가 아니다.
- POST가 늦어 lease가 모자라면 창을 늘리거나 POST를 다시 보내지 않는다. 그 회차는 요청 없이 회수로 끝낸다.
- 감독이 살아 있는 journal에 새 `run`을 시작하지 않는다(실행기도 거부한다).
- 표의 시각 표기는 순서를 보이는 것이며 시작 조건을 대신하지 않는다.

시작 판정과 감독 식별의 명령은 `RUNBOOK_DRAFT.md` 7-3·7-4에만 있다. 예전 판에 있던 `CREATE`·`FINAL`만 보는 한 줄 읽기는 중단·회수 중에도 허용을 낼 수 있어 없앴다.

```text
(명령은 RUNBOOK_DRAFT.md 7-3 · 7-4)
```

요청 두 건(MON 최소 관측안 그대로, 실제 명령은 회차 카드에서 확정):

- **443 양성 대조:** 승인 CA 검증을 유지한 `GET /`. 승인 nginx 소스는 이 경로에 404를 정의하므로 TLS 성공 + HTTP 404 + 같은 5-tuple의 gateway 양방향 통과 + monitor01 도착을 기대한다. live 설정이 달라 404가 아니면 기대를 고치지 말고 중단한다. 401 재시험이 아니다.
- **8443 음성 연결:** 별도 고정 출발 포트로 새 TCP 연결 1회, 연결 상한 5초, 앱 재시도 0. **rc가 0이 아니라는 것만으로는 차단 성공이 아니다.** TLS·CA·출발 포트 bind 단계의 실패는 차단의 근거가 아니고, 귀속은 7절의 행렬과 네 캡처로만 판단한다.
- 세 curl 명령(443·8443·post-deny)은 사용자 설정 파일을 읽지 않도록 `--disable`을 첫 인자로 둔다(실행안 6.3·6.4).

`complete`를 보내지 못해도 `lease`가 지나면 감독이 스스로 회수한다. 실행자의 세션이 끊겨도 같다(A안).

### 5.3 회수 뒤 — 도구가 확인하지 않는 것

`ABSENT_BASELINE_UNVERIFIED`는 canary 객체의 부재만 뜻한다. 사람이 이어서 확인한다.

- 기존 HEP·host GNP의 UID/RV와 spec이 회차 전과 같다.
- monitor01 firewalld runtime/permanent, gateway 정책·NAT가 전과 같다.
- worker03 호스트에서 `.30:443`으로 **새 연결**이 다시 막힌다(기존 Deny 복귀). 이미 맺어진 연결로 판단하지 않는다.
- `up` 23/23, remote write 실패 증가 0, heartbeat 정상.
- 캡처 프로세스가 끝났고 종료 코드·drop 통계가 남았다.

명령과 결과 파일은 실행안 6.4(post-deny, HEP·GNP 전후 비교, 나머지 위치의 `-post` 읽기)에 있다. 네 가지 판정(canary 부재 · 기준 복귀 · 증적 완전성 · AC)을 서로 구분한다(실행안 10절).

### 5.4 인수 (`watch` 종료 코드 3 또는 감독 소실)

자동 재시도는 없다. 인수자는 콘솔에서 **기존 관리 인증**으로 한다(임시 token이 아니다). 먼저 감독의 상태를 구분한다: 진행 중 · `NOT_STARTED` · 자동 회수 종결 · HANDOFF · 감독 소실 · 종료 확인 불가(실행안 8.2). **수동 삭제는 감독이 `ARMING`에 적힌 프로세스로 더는 존재하지 않고 writer 락이 풀렸음을 둘 다 확인한 뒤에만** 한다. 종료를 확정하지 못하면 수동 DELETE를 하지 않고 콘솔 인수 상태를 유지한다. 그다음 현재 GET의 원본(rc·stdout·stderr)을 남기고, 객체일 때만 이름·spec·UID·RV를 읽어, 카드 5절 4의 UID+최신 RV 조건부 raw DELETE를 판단한다. NotFound·403·timeout·해석 실패를 서로 구분하며, DELETE의 성공 응답은 부재가 아니고 삭제 뒤 읽기 실패도 부재가 아니다. 409·403을 force나 이름만 쓴 삭제로 우회하지 않는다. 사유별 "먼저 볼 것"은 [INTEGRATION §5 인수 표](https://github.com/321Team/infra-kubernetes/blob/92c182fc58de999536e56d90012bb2686d9f07cf/ops/p1-mon-if06b-cleanup/INTEGRATION.md)를 따른다. journal·증적 파일은 지우거나 고치지 않는다.

**재부팅 예외.** control01이 재부팅되면 감독 식별은 boot가 달라 계속 거부한다(새 요청과 신호를 막는 올바른 동작이다). 그 거부만으로는 삭제를 허용하지 않는다. 같은 호스트·같은 회차·같은 cluster이고 boot만 바뀌었으며 journal을 읽을 수 있고 락이 풀렸음을 **모두** 확인한 기록이 있을 때에만, 그 기록이 "감독이 더는 존재하지 않음"의 확인을 대신한다. 이전 boot의 PID에 신호를 보내지 않고, 기록의 boot 값을 고치지 않고, 감독을 다시 실행하지 않는다. 읽기 카드와 다섯 확인은 실행안 8.2a에 있다.

---

## 6. 과거 canary 카드 조건과 이번 회차의 대응

[canary 카드](https://github.com/321Team/infra-kubernetes/blob/92c182fc58de999536e56d90012bb2686d9f07cf/docs/change/P1-MON-01/P1_MON_01_IF06B_WORKER03_CANARY_20261002.md)를 그대로 반복하지 않는다. 바뀌는 조건과 근거:

| 카드 조건 | 이번 회차 | 근거 |
|---|---|---|
| T0 `route get`이 `src .108` | **유지** | — |
| T1 잘못된 인증으로 401 | **재사용, 반복 안 함** | 증적 122에서 관측됨. 이번의 443 요청은 캡처 유효성을 위한 양성 대조(`GET /` → 404)이며 목적이 다르다 |
| T2 8443: **monitor01에 SYN 도착** + SYN-ACK 없음 | **대체.** gateway ingress에 SYN 있음 + egress에 없음 + 같은 창의 443이 양방향 유효 + 캡처 누락 0 + 정책·route 불변이면 "gateway 구간에서 소실되는 것과 정합" | H04: "기존 monitor01 SYN 도착 기준은 gateway가 앞에서 차단하는 이 흐름에 적용하지 않는다". 증적 151: gateway가 non-DNAT 8443을 앞에서 DROP |
| T3 monitor01 캡처에서 출발지 `.108` | **재사용** + 443 양성 대조에서 다시 보임 | 증적 122 |
| `kubectl create`, 응답 UID/RV 보존 | **대체.** `guardian run`이 POST 1회, UID/RV를 journal에 기록 | PR84 |
| UID 확인 뒤 사람이 raw DELETE | **대체.** 감독이 UID+방금 읽은 RV로 조건부 DELETE 1회 + readback. 사람의 수동 삭제는 인수 때만 | PR84 |
| 서버 측 dry-run, 후보 이름 부재 | **대체.** `preflight` + `run` 시작 검사 | PR84 |
| T19 종료 → 보호 복원 검토 → baseline 안정 뒤 시작 | **유지.** 기존 근거를 연결하고 새 T19 재시험·재승인은 요구하지 않는다. 그 뒤의 변경과 현재 기준선 안정 여부는 **시작 직전에** 확인한다 | [10/2 보호 복원 중간 승인](https://github.com/321Team/fds-project-baseline/issues/10#issuecomment-5952074346)만으로는 범위가 부족하고, [10/5 후속 검토](https://github.com/321Team/fds-project-baseline/issues/17#issuecomment-5990093805)가 evidence#103의 후속 원복·최종 기준선 검수·독립 승인·병합까지 확인했다. 과거 기록이며 현재 cluster 상태의 증거는 아니다 |
| (카드에 없던 현행 조건) | **추가 적용.** Harbor 변경·복구·worker 검증과 사후 관측, 다른 K8S·네트워크·APP 변경과 비중첩 | 5.0. 위 T19 조건을 대신하지 않고 함께 적용한다 |
| baseline `up` 23/23·remote write·heartbeat·firewalld | **유지** (사람이 확인) | 5.2, 5.3 |
| 헤더만 캡처, payload·`-k` 금지, CA 고정 | **유지** | — |

**H04의 지위:** [H04](https://github.com/321Team/fds-project-baseline/pull/160#issuecomment-6083293377)는 gateway 구간 귀속, 특정 rule 귀속 미요구, 이 흐름에 대한 monitor01 SYN 도착 조건 비적용을 **이미 결정했다.** 이 범위의 시험 방법 정렬을 다시 미결정 안건으로 올리지 않는다(r1이 최종 판단을 열어 둔 것처럼 쓴 부분은 정정한다). 할 일은 위 표처럼 행별 관측 조건과 요구 수준의 대응을 회차 기록에 남기는 것이다. 실제 AC 문구를 바꾸거나 허용 범위를 넓히는 일이 생길 때에만 별도 변경 기록의 필요성을 판단한다.

---

## 7. 판정 기준

### 관측 결과별로 허용되는 결론 (MON 최소 관측안 4절 그대로)

이 행렬을 요청의 5-tuple·rc·시각과 네 캡처 파일에 잇는 표는 실행안 10절에 있다.

| 관측 | 허용되는 결론 |
|---|---|
| gateway ingress에 SYN 있음, egress에 없음, 443 양방향 유효, 누락·drop 0, 정책·route 불변 | gateway 구간에서 소실되는 것과 정합. 특정 nft rule의 DROP 확정은 아니다(요구되지도 않음) |
| worker 송신이 없거나 gateway ingress에 없음 | gateway 귀속 불가. 상류·캡처·경로 조사 대상 |
| gateway egress에 SYN 있음, monitor01 ingress에 없음 | 두 지점 사이 또는 관측 공백. PASS 아님 |
| monitor01에 SYN 도착, SYN-ACK 없음 | 수신 노드 단계 조사. 특정 firewalld 규칙 귀속 불가 |
| 연결 성공, SYN-ACK, 예상 밖 응답, 관측 불능 | 차단 PASS 아님. 원본 보존, 추가 요청 중단, 회수 |

### 중단 (다음 요청을 보내지 않고 회수)

- 캡처 준비 실패, 443 양성 대조가 기대와 다름, `route get`의 src가 `.108`이 아님.
- MON 건강 악화(4.5의 세 관측), Source·정책 drift, 예상 밖 접근.
- 시간 초과. 창을 늘려 다시 돌리지 않는다.

### 하지 않는 것

같은 요청 반복, gateway에 8443 허용, counter·log·nftrace 추가, nft reset/flush, firewalld reload, conntrack 초기화, Prometheus 재시작, 선호하는 결과가 나올 때까지 재시험.

---

## 8. 회차 증적 (새 수집 회차, 과거 증적에 소급하지 않음)

- 공급: 커밋, `SHA256SUMS` 대조 출력, 입력 JSON(credential 경로만 있고 값은 없음), `validate`·`preflight` 출력.
- 감독: `journal.jsonl`, `writer.lock`, `supervisor.jsonl`, `watch` 출력과 종료 코드.
- 요청: worker03의 시험별 stdout·stderr·rc·시각, `route get`.
- 관측: **네 지점** 캡처(`worker-out`·`gateway-in`·`gateway-out`·`monitor-in`) 각각의 시작·종료 시각, 종료 코드, captured/received/dropped 통계, 인터페이스·필터.
- 전후: HEP·host GNP의 raw 원본과 UID/RV/spec 해시, GNP 목록, monitor01 listener·firewalld, gateway 정책 수집 2회, MON 기준선.
- 단계 결과: control01 `$SES/results/`의 `.time`·`.out`·`.err`·`.rc`(validate, preflight, run launcher, watch, 시작 판정, 감독 식별, RBAC 영수증, 수동 GET·DELETE).
- 모으는 순서와 내보내지 않는 것(token, 관리 credential)은 실행안 9.2.
- 한계 기록: 분리 실행에서는 `supervisor.jsonl`의 FINAL 줄만으로 그 줄의 fsync를 확인할 수 없다. 회수 상태는 journal과 실제 상태 확인으로 판정한다.

증적 PR과 담당 범위 리뷰 뒤에 AC를 판단한다. 회차가 통과해도 AC를 자동으로 체크하지 않는다.

---

## 9. 한계와 하지 않은 것

- 이 패키지는 로컬 문서와 파일이다. 이 세션이 control01에서 실행한 것은 하나도 없다.
- `tools/`의 도구는 로컬 MOCK으로만 확인했다(`verification-local.json`). root 0700 아래의 실제 동작, kubectl의 실제 오류 문구, token의 실제 수명은 현장 단계에서 본다.
- 2.2의 해시는 후보다. manifest JSON은 저장소에 없는 파생물이다. YAML과의 일치는 18:12 검토가 파서로 확인했지만, 해시가 현장 값으로 확정되는 것은 `validate`·`preflight` 뒤다.
- `hash-candidates.json`의 `yaml_parser_equal: NOT_RUN`은 최초 계산 때의 기록이라 그대로 둔다. 파서 검증은 Codex의 `mon-field-prep-review-20261012/verification.json`에 있다.
- 2.1a의 실측은 18:33:48 한 시점의 값이다. 이 세션이 서버에 접속한 것이 아니라 Codex의 수집 원본을 읽어 대조했다.
- C1~C7을 다 수집해도 회차 입력이 다 채워지는 것은 아니다(3.1).
- 3절의 명령은 읽기 전용으로 골랐지만 실행해 본 적이 없다. 출력 형식은 현장에서 다를 수 있다.
- 4.4의 숫자는 제안에서 유도한 후보일 뿐 승인값이 아니다.
- Harbor 쪽의 현재 상태는 권고 문서의 보고를 따랐고 직접 확인하지 않았다. 회차 직전에 다시 확인해야 한다.
- 정책 생성·삭제, 새 RBAC, 키 추출, 파일 배치, AC 판정, 티켓 게시는 하지 않았다.
