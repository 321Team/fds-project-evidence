# IF06B 실행안 초안 — 현재 후보값 기준

CLAUDE_ASSISTED · 이권욱 검토용 · 2026-10-12 KST · **r3**. `ONE_PASS_HANDOFF.md`의 R1~R5를 반영한 r2에 20:41 변경분 검토의 D1·D2를 더했다: **D1** 같은 control01이 재부팅된 뒤의 수동 회수 분기(8.2a), **D2** 캡처 창의 기준점과 후보 X의 한계(6.0). 도구·RBAC·두 tar는 그대로다. r2는 SHA256 `706132e6…ddd4`.

**이 문서는 실행 가능본이 아니다.** `<…>`가 남아 있고 아래 명령은 전부 `NOT RUN`이다. 현장에서 옵션·출력이 다를 수 있으며, 다르면 관측한 원본에 맞춰 해당 부분을 고친다. 단계마다 실제 입력과 기존 허용 범위를 확인한 뒤에만 실행한다. 새 ServiceAccount·RBAC·token(2절), control01 파일 배치(1절), 실제 canary(7절)는 각각 별도의 변경이다. 서버 실행·Phase 2 작업은 이 문서로 추가되지 않는다.

근거 문서: `MON_IF06B_FIELD_PREP.md`(r6), `SESSION_INPUT_SHEET.md`(r5). 공급 기준 `92c182fc58de999536e56d90012bb2686d9f07cf`(코드 6개 변경 없음).

| R | 반영 위치 |
|---|---|
| R1 시작·중단·감독 식별 | 7-3 판정과 표, 7-4 신호 전 식별, 8.1~8.3 |
| R2 RBAC 부분 생성·불확실 응답·정리 | 2.2~2.4, 2.6, 9.1 |
| R3 공급·경로·세션·결과 보존 | 0절 전체, 1절, 각 카드 머리의 실행 위치, `tools/record.sh` |
| R4 credential 수명·독립 인수 | 2.5, 7-0, 8절 머리, 9.1 |
| R5 관측 경로·전후 비교·판정 | 6절 전체, 7-3의 요청 직전 재확인, 8.3, 9.2, 10절 |

---

## 0. 공통 — 실행 위치, 변수, 결과 보존

### 0.1 전달물과 받는 위치

| 전달물 | 크기 · SHA-256 | 내용 | control01에서 풀리는 곳 |
|---|---|---|---|
| `supply-92c182f.tar` | 81,920 B · `8d1630c872eb9a88cecc3f5dec3cc6e2316f87ec6dacea420777967b5795fc20` | 실행 코드 6개, `canary-manifest.json`, `SHA256SUMS` | `$SES/supply/` |
| `if06b-aux-r1.tar` | 20,480 B · `fd5bb7c43fa8cf166f074eb78afb98bf4e552cfdc6f4762adac9eda1bab9d7ad` | `rbac/`(YAML 3개 + `SHA256SUMS`), `tools/`(읽기 도구 4개 + `record.sh` + `SHA256SUMS`) | `$SES/aux/rbac/`, `$SES/aux/tools/` |
| `input.json` | 회차마다 다름 | 입력표로 채운 실행기 입력 | `$SES/input.json` |

RBAC 파일은 코드 tar에 들어 있지 않다. 둘은 따로 전달하고 따로 대조한다. 기존 승인 전송 경로로 control01의 `<IN>`(입력표 C에 적는 절대경로)에 둔다. credential은 전달물이 아니다.

`tools/`는 읽기 전용 보조 도구다. API 요청을 보내지 않고 신호도 보내지 않는다.

| 도구 | 하는 일 | 출력과 종료 코드 |
|---|---|---|
| `gate.py` | 시작 판정. 18:54 이후 검토의 교체 명령과 바이트 단위로 같다 | `SNAPSHOT_ELIGIBLE`(0) / `WAIT_…`·`STOP_…`(3) |
| `ident.py` | 이 회차 감독이 `ARMING`에 기록된 그 프로세스로 살아 있는지 | `GUARDIAN_ALIVE pid=N`(0) / `GUARDIAN_GONE …`(4) / `STOP_…`(3) |
| `objinfo.py` | 저장해 둔 API 응답 한 개의 kind·name·UID·RV·spec 해시 | `OBJECT_OK …`(0) / `STATUS reason= code=`(4) / `STOP_…`(3) |
| `tokeninfo.py` | token 파일의 claim(값은 출력 안 함)과 수명 판정 | `TOKEN_CLAIMS_OK …`(0) / `STOP_TOKEN_…`(3) |
| `record.sh` | 명령 1개를 실행하고 시작 시각·stdout·stderr·종료 코드를 `$RES`에 남김. 이미 쓴 이름이면 실행하지 않고 97 | 명령 자신의 종료 코드 |

### 0.2 control01 변수 블록

**control01의 모든 새 터미널에서 가장 먼저 붙여 넣는다.** 변수는 다른 터미널로 넘어가지 않는다(survival-check 뒤의 새 세션, watch 콘솔 포함). 값은 입력표에서 확정한 것을 그대로 쓴다. credential의 내용은 변수에 넣지 않는다.

```sh
S=<session>
IN=<받은 위치의 절대경로>
BASE=/var/lib/fds-change
SES=$BASE/if06b-$S
SUP=$SES/supply
AUX=$SES/aux
RES=$SES/results
SURV=$BASE/if06b-survival-$S
TOK=/run/fds-if06b-$S
PY=/usr/bin/python3.12
KC='/usr/bin/kubectl --kubeconfig=/etc/kubernetes/admin.conf --request-timeout=10s'
G="$PY -B $SUP/guardian.py"
REC="sudo -n env IF06B_RESULTS=$RES /bin/sh $AUX/tools/record.sh"
GNP=/apis/crd.projectcalico.org/v1/globalnetworkpolicies/p1-mon-if06b-worker03-to-monitor01-canary
SA=system:serviceaccount:monitoring-api:p1-mon-if06b-guardian
echo "S=$S IN=$IN SES=$SES SURV=$SURV TOK=$TOK"
```

- 실행 위치: control01, 기존 `svc_ansible` 경로의 **MON 전용 세션**, bash. cwd는 상관없다(모든 경로가 절대경로).
- `/var/lib/fds-change`는 root 0700이다. 그 아래의 glob·`cd`·리다이렉션은 `svc_ansible` 셸에서 풀리지 않으므로 **root 셸 안에서만** 한다(`sudo -n sh -c '…'` 또는 `$REC`).
- `$KC`는 **기존 관리 인증**이다. 감독은 이것을 쓰지 않고 2절의 token을 쓴다. 콘솔 인수자는 token이 아니라 `$KC`로 회수한다.
- 작업 셸에 `set -e`·`set -u`를 걸지 않는다. 필요한 곳은 `sudo -n sh -eu -c '…'`처럼 서브셸 안에만 둔다. 검사가 실패해도 작업 콘솔은 닫히지 않는다.

### 0.3 결과 보존 규칙

`$REC 이름 명령…`은 그 명령을 root로 한 번 실행하고 `$RES/이름.time`·`.out`·`.err`·`.rc`를 남긴다.

- 이름은 단계 번호로 시작한다(예: `2-3a-sa-create`). 같은 이름을 다시 쓰면 실행되지 않고 97이 나온다. 다시 해야 하면 `-2`를 붙인 새 이름을 쓴다.
- 판단은 화면의 마지막 줄이 아니라 `.rc`와 `.out`·`.err` 원본으로 한다. 파이프 뒤 명령의 종료 코드를 API 결과로 쓰지 않는다.
- token이 stdout으로 나오는 명령에는 `$REC`를 쓰지 않는다(2.5).
- `$RES`는 journal·evidence와 다른 디렉터리다. journal 디렉터리에는 아무것도 추가하지 않는다.
- `$REC`는 `$AUX/tools`가 풀린 뒤(1-3)부터 쓸 수 있다. 그 전 단계는 화면의 `…_rc=`를 회차 기록에 적는다.

자주 나오는 종료 코드:

| 명령 | 0 | 그 밖 |
|---|---|---|
| `validate` | 통과 | 5 검사 실패(입력을 고쳐 새 이름으로 다시) · 2 입력/도구 오류 |
| `preflight` | 통과 | 5 검사 실패(5절) · 2 오류 |
| `run`의 launcher | `ARMED`까지 감. **생성·회수 성공이 아니다** | 4 `NOT_STARTED`(POST 0건) · 2 오류 |
| `watch` | `ABSENT_BASELINE_UNVERIFIED` | 3 인수 필요 |
| `kubectl get`(부재 확인) | 객체가 있음 | 1이고 `.err`에 `(NotFound)` → 부재. 1이지만 다른 문구 → **부재가 아니다** |
| `kubectl auth can-i` | `yes` | 1이고 `.out`이 `no` → 거부. 그 밖은 판정 불가 |
| `gate.py`·`ident.py`·`objinfo.py`·`tokeninfo.py` | 위 0.1 표 | 3 중단·대기, 4 `GONE`·`STATUS` |

---

## 1. 공급 배치

실행 위치: control01, 0.2 블록을 붙여 넣은 세션. 선행: `<IN>`에 두 tar가 전달됨, 경로 확정.

```sh
# 1-1 충돌 검사와 전달물 해시 (읽기)
sudo -n ls -la "$BASE"
sudo -n test ! -e "$SES" && echo SES_ABSENT
sudo -n test ! -e "$SURV" && echo SURV_ABSENT
sudo -n test ! -e "$TOK" && echo TOK_ABSENT
sha256sum "$IN/supply-92c182f.tar" "$IN/if06b-aux-r1.tar"

# 1-2 새 경로 만들기 (쓰기). 이미 있으면 mkdir가 실패하고 아무것도 바꾸지 않는다
sudo -n sh -eu -c '
  umask 022
  mkdir -m 0700 "$1"
  mkdir -m 0755 "$1/supply" "$1/aux"
  mkdir -m 0700 "$1/journal" "$1/evidence" "$1/results"
' sh "$SES"; echo "mkdir_rc=$?"

# 1-3 풀기와 대조 (쓰기). 해시·목록이 맞을 때만 푼다
sudo -n sh -eu -c '
  echo "8d1630c872eb9a88cecc3f5dec3cc6e2316f87ec6dacea420777967b5795fc20  $2" | sha256sum -c -
  test "$(tar -tf "$2" | LC_ALL=C sort | tr "\n" " ")" = "SHA256SUMS canary-manifest.json coordinator.py decision.py guardian.py journal.py supervisor.py transport.py "
  tar -xf "$2" -C "$1/supply" --no-same-owner --no-same-permissions
  cd "$1/supply"
  chown root:root ./*
  chmod 0644 ./*
  sha256sum -c SHA256SUMS
  test "$(ls -A | wc -l)" -eq 8
' sh "$SES" "$IN/supply-92c182f.tar"; echo "supply_rc=$?"

sudo -n sh -eu -c '
  echo "fd5bb7c43fa8cf166f074eb78afb98bf4e552cfdc6f4762adac9eda1bab9d7ad  $2" | sha256sum -c -
  test "$(tar -tf "$2" | LC_ALL=C sort | tr "\n" " ")" = "rbac/01-serviceaccount.yaml rbac/02-clusterrole.yaml rbac/03-clusterrolebinding.yaml rbac/SHA256SUMS tools/SHA256SUMS tools/gate.py tools/ident.py tools/objinfo.py tools/record.sh tools/tokeninfo.py "
  tar -xf "$2" -C "$1/aux" --no-same-owner --no-same-permissions
  chown -R root:root "$1/aux"
  chmod 0755 "$1/aux/rbac" "$1/aux/tools"
  cd "$1/aux/rbac"; chmod 0644 ./*; sha256sum -c SHA256SUMS
  cd "$1/aux/tools"; chmod 0644 ./*; sha256sum -c SHA256SUMS
' sh "$SES" "$IN/if06b-aux-r1.tar"; echo "aux_rc=$?"

# 1-4 배치 결과 기록 (읽기, 여기서부터 $REC 사용)
$REC 1-4-layout /bin/sh -c 'ls -lZ "$1/supply" "$1/aux/rbac" "$1/aux/tools"; ls -Zd "$1" "$1/journal" "$1/evidence" "$1/results"; ls -A "$1/journal" "$1/evidence"' sh "$SES"
```

- **통과:** 1-1의 세 경로가 모두 ABSENT이고 두 tar의 해시가 0.1 표와 같음. `mkdir_rc`·`supply_rc`·`aux_rc`가 모두 0. 1-4에서 파일 소유가 root이고 journal·evidence가 비어 있음.
- **중단:** 어느 `…_rc`든 0이 아니면 다음 블록을 실행하지 않는다. 경로가 이미 있으면 **지우거나 다시 쓰지 않고** `S`를 바꾼다. 해시가 다르면 풀지 않는다.
- **부분 실패:** 1-2가 성공하고 1-3이 실패하면 `$SES`가 남는다. 그 `$SES`는 이 회차에 쓰지 않고 그대로 둔 채 새 `S`로 다시 시작한다. 지울지는 나중에 따로 정한다.
- SURV(생존 시험)와 SES(회차)는 다른 경로다. TOK는 2.5에서 만든다.

---

## 2. 회차용 자격증명 — ServiceAccount + RBAC + 단기 token

실행 위치: control01, 0.2 블록. 선행: 1절 통과, **이 방식의 선택과 객체 3개 생성 범위가 확정됨.**

용도·권한·수명이 확인된 기존 guardian용 credential이 제공되면 그것을 쓰고 2.1~2.4와 2.6을 건너뛴다(2.5의 수명 확인과 3절 이후는 같다). 그런 credential을 찾으려고 전체를 뒤지거나 모든 binding을 전수 검사하는 일은 하지 않는다. 없을 때의 기본 후보가 이 절이다. 채택 제안이며 생성 허용이 아니다.

### 2.1 권한과 남는 범위

| 권한 | 이유 | 이름 제한 |
|---|---|---|
| `globalnetworkpolicies` `create` | canary 생성, preflight dry-run | **불가.** RBAC는 최상위 create를 이름으로 제한하지 못한다 |
| `globalnetworkpolicies` `get`·`delete` | 관측·조건부 회수 | canary 이름 하나 |
| `namespaces` `get` | 실행기의 cluster UID 확인 | `kube-system` 하나 |
| `selfsubjectaccessreviews` `create` | preflight 접근 검토 | role에 없음. 기본 `system:basic-user`의 권한이며 2.4에서 확인 |

이 token은 유효한 동안 **어떤 이름·어떤 내용의 GlobalNetworkPolicy든 생성할 수 있다.** "이 canary만 만들 수 있는 credential"이 아니다. 통제는 실행기의 고정 manifest와 고정 요청 집합, 짧은 수명, root 전용 파일, 회차 뒤 객체 삭제다. manifest의 권한은 r1에서 바꾸지 않았다(`rbac/SHA256SUMS` 그대로).

### 2.2 사전 확인 (읽기)

```sh
$REC 2-2-rbac-sums /bin/sh -c 'cd "$1" && sha256sum -c SHA256SUMS' sh "$AUX/rbac"
$REC 2-2-ns        $KC get ns monitoring-api -o json
$REC 2-2-sa-pre    $KC get sa -n monitoring-api p1-mon-if06b-guardian -o json
$REC 2-2-cr-pre    $KC get clusterrole p1-mon-if06b-guardian -o json
$REC 2-2-crb-pre   $KC get clusterrolebinding p1-mon-if06b-guardian -o json
$REC 2-2-dryrun    $KC create --dry-run=server -o name -f "$AUX/rbac/01-serviceaccount.yaml" -f "$AUX/rbac/02-clusterrole.yaml" -f "$AUX/rbac/03-clusterrolebinding.yaml"
```

기대: `rbac-sums`·`ns`·`dryrun`은 rc 0. 세 `-pre`는 rc 1이고 `.err`에 `(NotFound)`.

- `-pre`가 rc 0(이미 있음) → **만들지도 지우지도 않는다.** 누구 것인지 조사한다. `apply`·`replace`로 덮지 않는다.
- `-pre`가 rc 1인데 `(NotFound)`가 아님(Forbidden, timeout 등) → 부재가 아니다. 중단.
- dry-run 실패 → 생성을 시작하지 않는다.

### 2.3 한 개씩 생성하고 응답으로 소유를 확인 (쓰기)

**앞 단계의 두 줄이 모두 rc 0일 때만 다음 객체로 간다.** 생성 응답(`…-create.out`)이 소유의 근거이고, 나중의 GET은 근거가 아니다.

```sh
# a. ServiceAccount
$REC 2-3a-sa-create  $KC create -o json -f "$AUX/rbac/01-serviceaccount.yaml"
$REC 2-3a-sa-receipt $PY -B "$AUX/tools/objinfo.py" "$RES/2-3a-sa-create.out" ServiceAccount p1-mon-if06b-guardian monitoring-api

# b. ClusterRole — a가 둘 다 rc 0일 때만
$REC 2-3b-cr-create  $KC create -o json -f "$AUX/rbac/02-clusterrole.yaml"
$REC 2-3b-cr-receipt $PY -B "$AUX/tools/objinfo.py" "$RES/2-3b-cr-create.out" ClusterRole p1-mon-if06b-guardian

# c. ClusterRoleBinding — b가 둘 다 rc 0일 때만
$REC 2-3c-crb-create  $KC create -o json -f "$AUX/rbac/03-clusterrolebinding.yaml"
$REC 2-3c-crb-receipt $PY -B "$AUX/tools/objinfo.py" "$RES/2-3c-crb-create.out" ClusterRoleBinding p1-mon-if06b-guardian

sudo -n cat "$RES/2-3a-sa-receipt.out" "$RES/2-3b-cr-receipt.out" "$RES/2-3c-crb-receipt.out"
```

각 객체의 판정:

| create `.rc` | receipt | 판정 | 다음 |
|---|---|---|---|
| 0 | `OBJECT_OK … uid=…` | **이번 작업이 만든 객체.** 그 UID를 회차 기록에 적는다 | 다음 객체 |
| 0이 아님, `.err`가 `AlreadyExists`·`Forbidden`·`Invalid` 같은 서버의 명시적 거부 | — | 이 단계가 만든 것이 없다 | **중단.** 뒤 객체·token·run 모두 하지 않는다. 2.6 |
| 0이 아님, timeout·연결 끊김·알 수 없는 문구 | — | **UNKNOWN.** 만들어졌을 수 있다. "생성 0"이나 "부재"로 적지 않는다 | **중단.** 다시 만들지 않는다. 2.6의 UNKNOWN 줄 |
| 0 | `STOP_…` | 응답이 기대한 객체가 아니다. UNKNOWN과 같이 다룬다 | **중단.** 2.6 |
| `$REC`가 97 또는 기록 실패 | — | 증적 없이 진행하지 않는다 | **중단** |

### 2.4 부여된 범위 확인 (읽기, 관리 인증의 impersonation)

```sh
C=p1-mon-if06b-worker03-to-monitor01-canary
# yes(rc 0)여야 하는 것
$REC 2-4-y1 $KC auth can-i create globalnetworkpolicies.crd.projectcalico.org --as="$SA"
$REC 2-4-y2 $KC auth can-i get    "globalnetworkpolicies.crd.projectcalico.org/$C" --as="$SA"
$REC 2-4-y3 $KC auth can-i delete "globalnetworkpolicies.crd.projectcalico.org/$C" --as="$SA"
$REC 2-4-y4 $KC auth can-i get    namespaces/kube-system --as="$SA"
$REC 2-4-y5 $KC auth can-i create selfsubjectaccessreviews.authorization.k8s.io --as="$SA"
# no(rc 1, .out이 no)여야 하는 것
$REC 2-4-n1 $KC auth can-i list   globalnetworkpolicies.crd.projectcalico.org --as="$SA"
$REC 2-4-n2 $KC auth can-i delete globalnetworkpolicies.crd.projectcalico.org/fds-k8s-host-k8s-worker03 --as="$SA"
$REC 2-4-n3 $KC auth can-i patch  "globalnetworkpolicies.crd.projectcalico.org/$C" --as="$SA"
$REC 2-4-n4 $KC auth can-i get    secrets -n kube-system --as="$SA"
$REC 2-4-n5 $KC auth can-i get    namespaces/default --as="$SA"
$REC 2-4-n6 $KC auth can-i create clusterrolebindings.rbac.authorization.k8s.io --as="$SA"
```

하나라도 기대와 다르면 **token을 발급하지 않고** 2.6으로 간다. 이 11건은 정해 둔 검사일 뿐, 통과가 "다른 권한이 전혀 없다"거나 "최소 권한이다"의 증명은 아니다.

### 2.5 token 발급과 실제 수명 (쓰기: token 파일 1개)

이 명령의 stdout은 token이므로 `$REC`를 쓰지 않는다. TOK는 **새 디렉터리로만** 만들고(`mkdir`가 기존 경로에서 실패) token 파일은 덮어쓰지 않는다(`set -C`).

```sh
TTL=<요청 TTL 초>
MAXLIFE=<허용하는 실제 수명 상한 초>
NEED=<lease + cleanup_window + 인수 여유, 초>
SAUID=<2-3a 영수증의 uid>

sudo -n sh -eu -c '
  umask 077
  mkdir -m 0700 "$1"
  set -C
  rc=0
  /usr/bin/kubectl --kubeconfig=/etc/kubernetes/admin.conf --request-timeout=10s create token p1-mon-if06b-guardian -n monitoring-api --duration="$2"s > "$1/token" 2> "$3" || rc=$?
  echo "$rc" > "$4"
  exit "$rc"
' sh "$TOK" "$TTL" "$RES/2-5-token-issue.err" "$RES/2-5-token-issue.rc"; echo "token_issue_rc=$?"

$REC 2-5-token-stat   /usr/bin/stat -c '%n %U:%G %a %s' "$TOK/token"
$REC 2-5-token-claims $PY -B "$AUX/tools/tokeninfo.py" "$TOK/token" "$SA" "$SAUID" "$MAXLIFE" "$NEED"
sudo -n cat "$RES/2-5-token-claims.out"
```

| `tokeninfo` 출력 | 뜻 | 행동 |
|---|---|---|
| `TOKEN_CLAIMS_OK sub= aud= iat= exp= lifetime_s= left_s=` | sub와 SA UID가 영수증과 같고, 실제 수명이 상한 이내이며, 남은 시간이 `NEED` 이상 | 3절로 |
| `STOP_TOKEN_LIFETIME_EXCEEDS` | 서버가 상한보다 긴 token을 줬다 | **run을 시작하지 않는다.** 2.6으로 정리(SA 삭제가 무효화 경로) |
| `STOP_TOKEN_TOO_SHORT` | 남은 시간이 자동 회수 예산을 덮지 못함 | run을 시작하지 않는다. 재발급은 **새 TOK 경로와 새 단계 이름**으로 하는 별도 시도다 |
| `STOP_TOKEN_SUBJECT`·`STOP_TOKEN_SA_UID` | 기대한 SA의 token이 아니거나 SA가 바뀜 | 쓰지 않는다. 2.6 |
| `token_issue_rc`가 0이 아님, 그 밖의 `STOP_…` | 발급 실패·읽기 실패 | run 중단. `.err` 보존 |

- `<TTL>`과 `<MAXLIFE>`의 **현재 MON 후보는 둘 다 900초**다(미승인, 입력표에서 채택). 다른 업무에서 정한 900초를 가져온 것이 아니다. 서버는 요청과 다른 수명을 줄 수 있으므로 `lifetime_s`·`left_s`가 실제 값이다.
- claim을 읽은 것은 인증 성공의 증명이 아니다. 그 증명은 이 token으로 하는 5절 `preflight`다.
- **token 파일을 지워도 token은 무효가 되지 않는다.** 재발급하면 앞의 token도 만료나 SA 삭제 전까지 유효할 수 있다고 기록한다. `run`이 시작된 뒤에는 token을 바꾸지 않는다.
- **역할 분리:** token은 감독의 **자동 회수**에만 쓰인다. 콘솔 **수동 인수**는 기존 관리 인증(`$KC`)으로 한다. token이 만료·소실돼도 인수 경로는 남는다.

입력 파일의 credential은 `{"kind": "bearer_token_file", "token_file": "/run/fds-if06b-<session>/token"}`이 된다.

### 2.6 준비 중 실패했을 때의 정리 (canary 시작 전)

대상은 **2.3에서 `OBJECT_OK` 영수증이 있는 객체뿐**이다. 역순(Binding → Role → SA)으로, 객체마다 아래를 한다. 이름이 같다는 이유만으로 지우지 않는다.

```sh
# 예: ClusterRoleBinding. Role·SA는 경로와 kind, 단계 이름(2-6b, 2-6a)만 바꾼다
OWNED_UID=<2-3c 영수증의 uid>
$REC 2-6c-crb-now  $KC get clusterrolebinding p1-mon-if06b-guardian -o json
$REC 2-6c-crb-info $PY -B "$AUX/tools/objinfo.py" "$RES/2-6c-crb-now.out" ClusterRoleBinding p1-mon-if06b-guardian
sudo -n cat "$RES/2-6c-crb-info.out"
# 위 uid가 OWNED_UID와 같을 때만:
printf '%s' '{"apiVersion":"v1","kind":"DeleteOptions","preconditions":{"uid":"'"$OWNED_UID"'"}}' | $REC 2-6c-crb-delete $KC delete --raw=/apis/rbac.authorization.k8s.io/v1/clusterrolebindings/p1-mon-if06b-guardian -f -
$REC 2-6c-crb-after $KC get clusterrolebinding p1-mon-if06b-guardian -o json
```

raw 경로: Binding `/apis/rbac.authorization.k8s.io/v1/clusterrolebindings/p1-mon-if06b-guardian`, Role `/apis/rbac.authorization.k8s.io/v1/clusterroles/p1-mon-if06b-guardian`, SA `/api/v1/namespaces/monitoring-api/serviceaccounts/p1-mon-if06b-guardian`.

| 상황 | 행동 |
|---|---|
| 현재 UID = 영수증 UID | 위의 UID 조건부 삭제. `-after`가 rc 1 + `(NotFound)`여야 부재 |
| 현재 UID ≠ 영수증 UID | 다른 객체로 바뀌었다. **지우지 않는다.** 조사 |
| 현재 조회가 rc 1 + `(NotFound)` | 이미 없다. 삭제하지 않고 기록 |
| 현재 조회가 그 밖의 실패 | 부재로 보지 않는다. 다시 읽는다 |
| 삭제가 409 | 조건을 빼거나 force로 바꾸지 않고 다시 읽는다 |
| **UNKNOWN 객체**(영수증 없음) | 현재 조회(`-now`, `-info`)만 하고 결과를 기록한다. 같은 이름·같은 spec·가까운 생성 시각이라는 것만으로 이번 작업의 것으로 확정하지 않는다. **자동으로 지우거나 다시 만들지 않고 인수 상태로 남긴다** |

보고는 한 번에 한다: 어느 단계에서 멈췄는지, 영수증이 있는 객체와 UNKNOWN 객체, 현재 남은 객체, token 발급 여부. token을 이미 발급했다면 SA 삭제 전까지 유효할 수 있다는 점을 적고 TOK 파일은 9.1의 순서로 지운다.

---

## 3. 입력 파일과 `validate`

실행 위치: control01, 0.2 블록. 선행: 1절, credential 파일 존재(2.5 또는 기존 credential), `<IN>/input.json` 전달.

```sh
sha256sum "$IN/input.json"
sudo -n sh -eu -c 'umask 022; set -C; cat "$2" > "$1/input.json"; sha256sum "$1/input.json"' sh "$SES" "$IN/input.json"; echo "input_rc=$?"
$REC 3-1-validate $G validate --config "$SES/input.json"
sudo -n cat "$RES/3-1-validate.out"
```

- **통과:** rc 0, `passed=true`, `network_requests=0`, 네 검사(`manifest_sha256_matches`·`directories_independent`·`session_directories_unused`·`budgets_consistent`)가 모두 `true`, `computed_manifest_sha256`이 `0602b000…d37f`. 두 `sha256sum`이 같음.
- 이 단계는 CA와 token **파일을 읽는다**(검사만, 전송 없음).
- **rc 5:** 어느 검사가 `false`인지 보고 입력을 고친다. `input.json`은 덮어쓰지 않으므로 고친 파일은 새 `S`의 새 `$SES`에 두거나, 같은 `$SES`를 쓰려면 사용자가 그 파일 교체를 명시적으로 정한다. 다시 돌릴 때는 `3-1-validate-2`.
- **rc 2:** `.out`의 `reason`(`FILE_INVALID`·`CA_PIN_MISMATCH`·`CREDENTIAL_INVALID`·`INPUT_INVALID`). 서버 상태는 바뀌지 않는다.

---

## 4. `survival-check` — 세션 종료 뒤 생존 (A안일 때)

API·credential·정책을 쓰지 않는다. `run`과 같은 방식(`$REC`를 거친 launcher)으로 띄워 같은 경로를 시험한다. 숫자는 후보다.

**세션 S (이 시험만을 위해 새로 연 SSH 세션). 0.2 블록을 먼저 붙여 넣는다.**

```sh
echo "session=$XDG_SESSION_ID tty=$(tty) shell_pid=$$ $(date -Is)"
loginctl list-sessions --no-legend
sudo -n mkdir -m 0700 "$SURV"; echo "mkdir_rc=$?"
$REC 4-1-survival-launch $G survival-check --evidence-dir "$SURV" --seconds <초> --interval-seconds <초>
sudo -n cat "$RES/4-1-survival-launch.out"
date -Is
```

`ARMED` 한 줄을 확인한 뒤 **세션 S만** 닫는다(그 터미널에서 `exit`). 다른 세션은 건드리지 않는다.

**다른 세션(기존 것 또는 새 것). 0.2 블록을 다시 붙여 넣는다.**

```sh
date -Is
loginctl list-sessions --no-legend
$REC 4-2-survival-tail /usr/bin/tail -n 3 "$SURV/survival.jsonl"
sudo -n cat "$RES/4-2-survival-tail.out"
# 지정한 시간이 지난 뒤
$REC 4-3-survival-beats /usr/bin/grep -a -c '"step":"BEAT"' "$SURV/survival.jsonl"
$REC 4-3-survival-final /usr/bin/grep -a '"step":"FINAL"' "$SURV/survival.jsonl"
sudo -n cat "$RES/4-3-survival-beats.out" "$RES/4-3-survival-final.out"
```

- **통과:** S를 닫은 시각 **뒤에도** `BEAT`의 `utc`가 이어지고, `FINAL`이 `SURVIVED_REQUESTED_DURATION`이며 `evidence_complete_before_write=true`. 세션 목록에서 S만 사라졌다.
- **불통과:** `BEAT`가 S를 닫은 시각에 끊김 → A안 불가, B안(콘솔 foreground).
- **금지:** `loginctl terminate-user`·`terminate-session`·`kill-user`, 다른 세션 종료. Harbor 작업이 같은 계정을 쓴다.
- 시험을 멈추려면 `ARMED` 행의 `guardian_epoch`(`pid-시작틱`)에서 pid를 얻고, `sudo -n cat /proc/<pid>/stat`의 22번째 값이 그 시작틱과 같은지 본 뒤 `sudo -n kill -TERM <pid>`. 남는 것은 `$SURV`의 파일뿐이다.
- 통과는 "이 실행 방식이 그 시점에 세션 종료를 넘겼다"는 뜻이다. reboot·SIGKILL 생존은 아니다.

---

## 5. `preflight`

실행 위치: control01, 0.2 블록. 실제 API에 인증된 요청 6건(읽기 2, 접근 검토 3, dry-run 1). 영속 쓰기 0.

```sh
$REC 5-1-preflight $G preflight --config "$SES/input.json"
sudo -n cat "$RES/5-1-preflight.out"
```

- **통과:** rc 0, `passed=true`, `persisted_writes=0`, `checks` 5개가 모두 `PASS`, `defaulted_spec_sha256`이 `4b5599c4…8146`.
- **검증 범위:** 고정 CA와 검증 이름으로 실제로 연결된 TLS 상대를 검증한다. 6건의 성공은 그 6건의 근거이며 `.109` 뒤의 backend 전체나 이후 연결을 보장하지 않는다. 이 token이 API에서 실제로 인증되고 create/get/delete가 허용된다는 것도 여기서 처음 확인된다.
- **rc 5:** `access_*`가 `FAIL`이면 2.4로 돌아가 권한을 본다. `dry_run_spec_pin`은 `FAIL`(해시 불일치)과 `DRY_RUN_REJECTED`(응답 조건 위반)를 구분하고 새 해시를 자동 채택하지 않는다. `cluster_and_absence`가 `CLUSTER_CHANGED`면 전부 중단, `CANARY_ALREADY_PRESENT`면 조사(삭제하지 않음).
- TLS·연결 오류에 TLS 검증을 풀거나 `.102`로 바꾸지 않는다.
- `preflight`는 journal을 만들지 않는다. `$SES/journal`은 그대로 비어 있다.

---

## 6. 외부 관측 카드

### 6.0 시간 축 — 한 곳에서 정한다

숫자는 입력표의 "시간 후보" 한 표에서 한 번에 채택한다. **원안(MON 최소 관측안)의 제안은 캡처 최대 120초 · 무시험 배경 20초 · 두 요청 20초 이내 · 후관측 20초 · canary 180초**다. r1 실행안의 후보(lease 120 · 회수 60 · 시험 30 · 캡처 200초 초과)는 그것과 같은 숫자가 아니었다.

**기준점.** 각 캡처의 창은 **그 캡처의 `timeout`이 시작된 순간부터** 센다. t0는 네 지점의 준비를 서로 확인한 시각일 뿐, 타이머를 다시 시작하는 시각이 아니다. 먼저 켠 캡처는 t0 전에 이미 시간이 줄어든다. 네 캡처에 공통으로 유효한 관측 구간은 **가장 늦게 준비된 시각부터 가장 먼저 끝난 시각까지**다.

| 구간 | 기준점 |
|---|---|
| 캡처 창 | **지점마다** 그 캡처의 `timeout`이 시작된 시각. 네 지점의 값이 서로 다르다 |
| 공통 유효 관측 구간 | 가장 늦게 준비된 캡처의 시작 ~ 가장 먼저 끝난 캡처의 종료 |
| 무시험 배경 | 네 지점의 준비를 확인한 시각 t0 |
| lease · 회수 window | `ARMING` 직전. `run`의 사전 GET 2건(각각 `request_timeout`까지)은 **그 앞**에 일어난다 |
| 요청 시작 최종 시점 | `expires_mono` − (시험 + 후관측) |

**후보 X의 한계.** 후보 X(lease 90)는 원안의 캡처·요청·후관측 숫자를 유지한다. 그러나 `run`의 사전 읽기 2건, 사람 사이의 전달, 만료에 의한 회수, post-deny가 모두 그 구간에 들어온다는 보장은 없다. **X는 관측 범위가 제한될 수 있음을 받아들일 때 고르는 후보다.** 시험이 일찍 끝나 완료 신호로 회수하는 회차는 들어갈 수 있지만, 만료까지 가는 회차는 벗어날 수 있다.

합성 예(산술만, 서버 증적 아님 — 네 캡처를 동시에 켠 가장 유리한 경우, 요청은 각각 9초로 예산 10초 이내):

| t0 뒤 | 사건 |
|---|---|
| 18초 | `run` 사전 GET 2건 뒤 `ARMING` |
| 27초 | 생성 응답, `OWNED` |
| 108초 | lease 90초 만료 |
| 117초 · 126초 | 회수 GET 완료 · DELETE 완료 |
| 128초 · 137초 | readback 대기 2초 · readback 완료(회수 기한 168초 안) |
| 142초 | post-deny 완료 — **캡처 120초 밖** |

만료 회수와 post-deny까지 관측하려면, 캡처 창 후보에 **각 캡처의 시작 시각 차이 + `run` 사전 GET 2건 + lease + cleanup_window + post-deny + 전달 여유**를 넣어 입력표에서 한 번에 고른다. 숫자는 제안값이며 새 AC를 만들지 않는다. 실제 지연과 파일 동기화에는 끝나는 시각의 보장이 없다.

어느 후보를 쓰든 **배경 구간, 소유 대기, 시험과 후관측, 회수, post-deny가 공통 유효 관측 구간 안에 들어왔는지**를 회차 뒤에 각 캡처의 `cap-start`·`cap-end`와 요청·회수의 시각으로 판단한다. 벗어난 부분은 `NOT_VERIFIED`로 적고, 추가 시험 없이 회수한다. lease와 캡처 창을 현장에서 늘리지 않으며, 창을 맞추려고 요청을 더 보내지 않는다.

### 6.1 회차 전 기준 기록

**control01 (0.2 블록, 기존 관리 인증으로 읽기).** 기존 canary 카드 §4-3의 조회다. guardian SA에는 list 권한을 주지 않는다.

```sh
HEP=/apis/crd.projectcalico.org/v1/hostendpoints/fds-k8s-k8s-worker03
HOSTGNP=/apis/crd.projectcalico.org/v1/globalnetworkpolicies/fds-k8s-host-k8s-worker03
ALLGNP=/apis/crd.projectcalico.org/v1/globalnetworkpolicies
P=pre
$REC 6-$P-hep-get      $KC get --raw="$HEP"
$REC 6-$P-hep-info     $PY -B "$AUX/tools/objinfo.py" "$RES/6-$P-hep-get.out" HostEndpoint fds-k8s-k8s-worker03
$REC 6-$P-hostgnp-get  $KC get --raw="$HOSTGNP"
$REC 6-$P-hostgnp-info $PY -B "$AUX/tools/objinfo.py" "$RES/6-$P-hostgnp-get.out" GlobalNetworkPolicy fds-k8s-host-k8s-worker03
$REC 6-$P-gnp-all      $KC get --raw="$ALLGNP"
$REC 6-$P-gnp-list     $PY -B -c 'import json,sys; [print(i["metadata"]["name"], i["spec"].get("order"), i["metadata"]["uid"], i["metadata"]["resourceVersion"], i["spec"].get("selector")) for i in sorted(json.load(open(sys.argv[1]))["items"], key=lambda i: i["metadata"]["name"])]' "$RES/6-$P-gnp-all.out"
sudo -n cat "$RES/6-$P-hep-info.out" "$RES/6-$P-hostgnp-info.out" "$RES/6-$P-gnp-list.out"
```

확인: 두 `-info`가 `OBJECT_OK`. `gnp-list`에 canary 이름이 없고, worker03 selector를 고르는 다른 GNP나 order 90인 GNP가 없다(host GNP는 order 100). raw 원본(`-get.out`, `gnp-all.out`)은 그대로 보존한다.

**그 밖의 위치 — 기존 정상 계정·도구로 읽는다.** 재인증 절차나 새 도구를 만들지 않는다.

| 위치 | 무엇을 | 어디의 어떤 명령으로 | 결과 위치 |
|---|---|---|---|
| worker03 | `ip -4 route get 10.250.10.30` | 기존 `server07` 경로 | `~/if06b-<session>/worker/route-pre.txt` — 기대 `src 10.1.93.108` |
| worker03 | `sha256sum <CA 파일>`, `curl --version` | 같음 | `ca-sha.txt`(기대 `20ddfa5e…053f`), `curl-version.txt` |
| worker03 | `ss -tan 'sport = :<P443>'`, `ss -tan 'sport = :<P8443>'` | 같음 | `ports-pre.txt` — 둘 다 비어 있음 |
| mgmt-gw01 | 정책·zone·route·NAT 원본 22조회 | 기존 수집기 `infra-kubernetes` `ops/if06b-policy-readonly/`(`92c182f`, `collect.py` SHA-256 `d8c6fdef…0f4b`). ansible01에서 `run-interactive.sh`, 그 README의 조건대로. rc 0=조회 완료, 2=조회 실패·변경 감지, 12=기록 실패 | gateway `/root/if06b-policy-*`, ansible01의 receipt 폴더. **회차 전 1회** |
| mgmt-gw01 | `ip -br addr` | 기존 계정 | ingress(physical)·egress(management) 인터페이스를 입력표 D에 |
| monitor01 | `ss -ltn 'sport = :443'`, `ss -ltn 'sport = :8443'` | 기존 `server01_monitor` 경로 | `~/if06b-<session>/monitor/listen-pre.txt` |
| monitor01 | `sudo firewall-cmd --list-all`, `sudo firewall-cmd --permanent --list-all` | 같음 | `fw-pre.txt` (10/6 `fw-pre.txt`와 같은 형식) |
| MON | targets 수와 up 수, `sum(increase(prometheus_remote_storage_samples_failed_total[15m]))`, heartbeat 나이 | MON 관측자의 기존 명령(10/6 `mon-gate-20261006T1615.txt`·`hb-after.txt`를 만든 것). 그 명령의 위치는 저장소에서 찾지 못했다 → **입력표 D의 현장 입력** | `mon-pre.txt` — 기대 23 / 23 / 0 / 정상 |

gateway 수집기의 README가 적은 대로, 전후 바이트 일치는 그 사이 무변경의 증명이 아니고 nft counter는 자연히 변하므로 바이트 비교로 PASS/FAIL하지 않는다. 비교 대상은 정책·zone·route·NAT 원본이다.

### 6.2 캡처 — 네 지점, 서로 다른 디렉터리

지점 이름은 `worker-out`, `gateway-in`, `gateway-out`, `monitor-in`이다. **지점마다 터미널 하나**, 결과는 `~/if06b-<session>/<지점>/`에 따로 남는다. gateway의 두 캡처도 터미널과 디렉터리가 다르므로 서로 덮어쓰지 않는다.

각 터미널에서(그 호스트의 기존 계정, bash):

```sh
RUNID=<session>
POINT=<worker-out 또는 gateway-in 또는 gateway-out 또는 monitor-in>
IF=<그 지점의 인터페이스>
CAP_WINDOW=<캡처 창 초>
C=$HOME/if06b-$RUNID/$POINT
sudo -v
(
  set -eu
  mkdir -p "$HOME/if06b-$RUNID"
  mkdir "$C"
  set -C
  date -Is | tee "$C/cap-start.txt"
  sudo -n timeout --signal=INT --preserve-status "$CAP_WINDOW" tcpdump -nn -tttt -l -i "$IF" '(host 10.1.93.108 and host 10.250.10.30) and ((tcp and (port 443 or port 8443)) or icmp)' > "$C/cap.txt" 2> "$C/cap-stats.txt" &
  CAP_PID=$!
  echo "cap_pid=$CAP_PID window_s=$CAP_WINDOW point=$POINT if=$IF" | tee "$C/cap-pid.txt"
  if wait "$CAP_PID"; then CAP_RC=0; else CAP_RC=$?; fi
  echo "rc=$CAP_RC" | tee "$C/cap-rc.txt"
  date -Is | tee "$C/cap-end.txt"
  cat "$C/cap-stats.txt"
)
```

- `mkdir "$C"`는 디렉터리가 이미 있으면 실패하고 캡처를 시작하지 않는다. 괄호 안의 `set -e`는 그 서브셸에만 적용되어 터미널은 닫히지 않는다.
- **그 터미널은 캡처가 끝날 때까지 그대로 둔다.** 캡처를 시작한 셸만이 자기 `CAP_PID`를 `wait`해서 실제 종료 코드를 받을 수 있기 때문이다. 셸이 끊기면 그 지점은 `NOT_VERIFIED`다.
- **준비 통보:** 캡처 터미널은 막혀 있으므로, 같은 호스트의 다른 터미널에서 `grep 'listening on' ~/if06b-<session>/<지점>/cap-stats.txt`가 나오는 것을 보고 control01 실행자에게 알린다. 네 지점이 모두 알린 시각이 t0다. 하나라도 준비되지 않으면 `run`을 치지 않는다.
- `-q`·`-A`·`-X`·`-w`를 쓰지 않는다. 이름 기반 `pkill`을 쓰지 않는다.
- 필터는 gateway가 이 흐름을 NAT하지 않는다는 10/8 관측을 전제로 한다. 6.1의 gateway 수집에서 달라졌으면 필터를 다시 본다.
- **유효 조건(지점마다):** `listening on` 있음, `rc=0`, `dropped by kernel` 0, 요청 시각이 `cap-start`~`cap-end` 안.

### 6.3 요청 — worker03, 시작 통보를 받은 뒤, 각 1회

실행 위치: worker03, 기존 `server07` 경로, bash.

```sh
RUNID=<session>
CA=<승인 CA 파일의 절대경로>
P443=<443용 출발 포트>
P8443=<8443용 출발 포트>
W=$HOME/if06b-$RUNID/worker
mkdir -p "$W"

# 443 양성 대조 — 시작 통보 뒤 1회
date -Is > "$W/t443.time"
curl --disable --cacert "$CA" --noproxy '*' --connect-timeout 5 --max-time 10 --retry 0 --local-port "$P443" -sS -o /dev/null -w 'http=%{http_code} remote=%{remote_ip}:%{remote_port} local=%{local_ip}:%{local_port} ssl_verify=%{ssl_verify_result}\n' https://10.250.10.30/ > "$W/t443.out" 2> "$W/t443.err"; echo $? > "$W/t443.rc"
cat "$W/t443.rc" "$W/t443.out"

# 8443 음성 연결 — 443이 기대대로였고, control01에서 다시 "계속" 통보를 받은 뒤 1회
date -Is > "$W/t8443.time"
curl --disable --cacert "$CA" --noproxy '*' --connect-timeout 5 --max-time 8 --retry 0 --local-port "$P8443" -sS -o /dev/null -w 'http=%{http_code} remote=%{remote_ip}:%{remote_port} local=%{local_ip}:%{local_port}\n' https://10.250.10.30:8443/ > "$W/t8443.out" 2> "$W/t8443.err"; echo $? > "$W/t8443.rc"
cat "$W/t8443.rc" "$W/t8443.out" "$W/t8443.err"
```

`--disable`은 첫 인자여야 하며 사용자 `.curlrc`를 읽지 않게 한다. `-k`·`--insecure`를 쓰지 않는다. 재시도는 0이다.

| 요청 | 기대 | 기대가 아닐 때 |
|---|---|---|
| 443 | rc 0, `http=404`, `ssl_verify=0`, local이 `10.1.93.108:<P443>`. **그리고** 같은 5-tuple이 gateway 양쪽과 monitor01에 보임(캡처, 10절) | 기대를 고치지 않는다. 8443을 보내지 않고 control01에 알려 회수한다 |
| 8443 | 연결이 맺어지지 않음(보통 rc 28) | 아래 |

**8443의 rc가 0이 아니라는 것만으로는 차단 성공이 아니다.** rc 28(시간 초과)·7(연결 거부)은 "연결이 안 됐다"는 사실일 뿐이고, 어디서 사라졌는지는 10절의 H04 행렬(gateway ingress에 SYN 있음 + egress에 없음 + 443 양방향 유효 + 누락 0 + 정책 불변)로만 판단한다. rc 35·60·77(TLS·CA 문제), 45(출발 포트 bind 실패), 6(이름 해석)처럼 **연결 시도 이전이나 TLS 단계의 실패는 차단의 근거가 아니며** 그 요청은 `NOT_VERIFIED`다. 어느 경우에도 다시 보내지 않는다.

실제로 보낸 요청 수를 그대로 적는다(0, 1 또는 2). 하나라도 나갔으면 "요청 0건"이라고 쓰지 않는다.

### 6.4 회수 뒤 — post-deny와 전후 비교

worker03(6.3과 같은 터미널, 변수 유지):

```sh
date -Is > "$W/post-deny.time"
curl --disable --cacert "$CA" --noproxy '*' --connect-timeout 5 --max-time 8 --retry 0 -sS -o /dev/null -w 'http=%{http_code} remote=%{remote_ip}:%{remote_port} local=%{local_ip}:%{local_port}\n' https://10.250.10.30/ > "$W/post-deny.out" 2> "$W/post-deny.err"; echo $? > "$W/post-deny.rc"
cat "$W/post-deny.rc" "$W/post-deny.err"
ip -4 route get 10.250.10.30 > "$W/route-post.txt"
```

기대는 새 연결이 맺어지지 않는 것이다(10/6에는 rc 28). 여기서도 TLS·CA·bind 오류는 차단 복귀의 근거가 아니다. 캡처 창 안이면 그 시도가 `worker-out`에 보이는지 함께 본다. 창 밖이면 캡처 대조는 `NOT_VERIFIED`로 적는다. post-deny도 1회다.

control01(0.2 블록): 6.1의 control01 블록을 `P=post`로 한 번 더 실행한 뒤 비교한다.

```sh
$REC 6-diff-hep      /usr/bin/diff "$RES/6-pre-hep-info.out" "$RES/6-post-hep-info.out"
$REC 6-diff-hostgnp  /usr/bin/diff "$RES/6-pre-hostgnp-info.out" "$RES/6-post-hostgnp-info.out"
$REC 6-diff-gnp-list /usr/bin/diff "$RES/6-pre-gnp-list.out" "$RES/6-post-gnp-list.out"
```

세 diff가 rc 0이면 HEP·host GNP의 UID/RV/spec 해시와 GNP 목록이 회차 전과 같다. rc 1이면 `.out`의 차이를 조사한다(canary가 아직 남아 있으면 목록에 나타난다).

나머지 위치는 6.1의 표를 `-post` 이름으로 다시 읽는다: monitor01 `listen-post.txt`·`fw-post.txt`(`fw-pre.txt`와 비교), gateway 수집기 **회차 뒤 1회**(전 수집과 정책·zone·route·NAT 비교), MON `mon-post.txt`(23 / 23 / 0 / 정상), worker03 `route-post.txt`.

원복할 설정 변경은 없다.

---

## 7. 회차

선행: 1~6절, 입력표 F의 시작 조건, 실제로 비어 있는 구간(Harbor 변경·사후 관측과 다른 시간). 순서의 설명은 `MON_IF06B_FIELD_PREP.md` 5.2에 있고 명령은 여기 한 곳에만 둔다.

**7-0 시작 직전 (control01 실행자, 0.2 블록)**

```sh
MAXLIFE=<허용하는 실제 수명 상한 초>
SAUID=<2-3a 영수증의 uid>
NEED=<lease + cleanup_window + 인수 여유, 초>
$REC 7-0-token-claims $PY -B "$AUX/tools/tokeninfo.py" "$TOK/token" "$SA" "$SAUID" "$MAXLIFE" "$NEED"
$REC 7-0-boot /usr/bin/cat /proc/sys/kernel/random/boot_id
sudo -n cat "$RES/7-0-token-claims.out" "$RES/7-0-boot.out"
```

`TOKEN_CLAIMS_OK`가 아니면 시작하지 않는다(2.5의 표). 기존 credential을 쓰는 경우에는 그 credential의 유효기간을 같은 기준으로 확인한다. boot는 입력표의 실측값과 대조한다.

**7-1 실행 (control01 실행자)**

```sh
$REC 7-1-run-launch $G run --config "$SES/input.json"
sudo -n cat "$RES/7-1-run-launch.out"
```

launcher rc 0과 `ARMED`는 **"CREATE_INTENT가 기록됐고 이제 POST를 보낸다"** 는 뜻이다. 생성도 회수도 아니다. rc 4는 `NOT_STARTED`이고 POST는 0건이다(`.out`의 `reason`).

**7-2 감시 (인수자, 콘솔 또는 다른 터미널, 0.2 블록을 먼저 붙여 넣음). `ARMED` 직후에 띄운다**

```sh
$REC 7-2-watch $G watch --journal-dir "$SES/journal" --poll-seconds <초> --window-seconds <초>
sudo -n cat "$RES/7-2-watch.out"
```

이 명령은 감독이 끝나거나 감시 창이 끝날 때까지 돌아오지 않는다. 돌아오면 결과를 실행자와 요청자에게 바로 알린다. `watch`가 락을 보고 "아직 쓰는 중"이라고 판단하는 것은 **감독이 건강하다는 보장이 아니다.**

**7-3 시작 판정 (control01 실행자)**

```sh
NEEDSTART=<시험 + 후관측, 초>
sudo -n $PY -B "$AUX/tools/gate.py" "$SES/input.json" "$SES/evidence/supervisor.jsonl" "$NEEDSTART"; echo "gate_rc=$?"
```

필요한 만큼 다시 읽는다(읽기만 한다). 시작을 전달하기 직전의 한 번은 기록으로 남긴다.

```sh
$REC 7-3-gate-443 $PY -B "$AUX/tools/gate.py" "$SES/input.json" "$SES/evidence/supervisor.jsonl" "$NEEDSTART"
sudo -n cat "$RES/7-3-gate-443.out"
```

| 출력 | 뜻 | 행동 |
|---|---|---|
| `SNAPSHOT_ELIGIBLE pid=N start_remaining_s= …` | 읽은 순간: 이 회차의 session·cluster·boot·감독 프로세스가 맞고, 기록이 `ARMING, ARMED, CREATE`뿐이며 온전하고, `CREATE`가 `OWNED`+UID+RV이고, 시험+후관측 시간이 남음 | 아래 "시작 전달 조건"을 모두 볼 때만 전달 |
| `WAIT_CREATE` | `CREATE`가 아직 없다. 진행 중일 수 있다 | `watch`를 유지하고 다시 읽는다. POST를 다시 보내지 않는다 |
| `WAIT_NO_COMPLETE_SNAPSHOT` | 마지막 행이 아직 덜 쓰였다 | 그 행을 근거로 삼지 않고 다시 읽는다 |
| `STOP_RECLAIM_OR_TERMINAL` | `TRIGGER`·`CLEANUP`·`READBACK`·`FINAL` 중 하나가 있다 | **새 요청 금지.** 회수 또는 종결 중이다 |
| `STOP_INSUFFICIENT_LEASE` | 시험+후관측 시간이 남지 않음 | 새 요청 금지. lease를 늘리지 않는다. 소유가 확정됐으면 7-4로 회수 |
| `STOP_NOT_OWNED` | `CREATE`가 `OWNED`가 아니거나 UID·RV가 없음 | 새 요청 금지. 8절 |
| `STOP_WRONG_SESSION`·`STOP_WRONG_BOOT`·`STOP_PROCESS_IDENTITY` | 다른 회차의 기록이거나, reboot됐거나, 감독이 그 프로세스가 아님 | 새 요청 금지. 8절. reboot이면 8.2a |
| `STOP_EVIDENCE_SEQUENCE`·`STOP_UNEXPECTED_HISTORY`·`STOP_UNREADABLE_STATE` | 증적이 빠졌거나 깨짐 | 새 요청 금지. 8절 |

**시작 전달 조건(모두):** ① 방금 `SNAPSHOT_ELIGIBLE` ② `watch`가 아직 돌아오지 않았음 ③ 이 회차에 abort(USR1·TERM)를 보낸 적이 없음 — **보냈다면 `TRIGGER` 행이 아직 없어도 금지** ④ 네 캡처가 준비 상태이고 배경 구간이 지났음.

`SNAPSHOT_ELIGIBLE`은 그 순간의 진단이다. 그 뒤의 생존을 보장하지 않고, 스스로 요청을 보내지도 않는다. 그래서:

- 시작을 전달한 뒤에도 실행자는 `watch`의 결과와 abort 요청을 **요청자에게 바로 넘겨 다음 요청을 멈추게** 한다.
- **8443 직전에 한 번 더 판정한다**(`$REC 7-3-gate-8443 …`, `NEEDSTART`는 8443 소요+후관측). `SNAPSHOT_ELIGIBLE`이 아니면 8443을 보내지 않는다.
- 판정이 `STOP_…`으로 바뀌기 전에 이미 나간 요청이 있으면 그 수를 그대로 적는다.

**7-4 회수 요청 (control01 실행자). 신호 직전에 감독을 식별한다**

```sh
$REC 7-4-ident $PY -B "$AUX/tools/ident.py" "$SES/input.json" "$SES/evidence/supervisor.jsonl"
sudo -n cat "$RES/7-4-ident.out"
GPID=<방금 GUARDIAN_ALIVE가 낸 pid>
$REC 7-4-complete /bin/kill -USR2 "$GPID"
```

- `GUARDIAN_ALIVE pid=N`일 때만 그 `N`에 신호를 보낸다. pid는 이 회차 `ARMING`의 `guardian_epoch`에서 나오고, 도구가 현재 boot와 프로세스 시작틱을 대조한다. `pgrep`은 참고 목록일 뿐 대상을 고르는 근거가 아니다.
- `GUARDIAN_GONE`·`STOP_…`이면 **신호를 보내지 않는다**(그 pid는 다른 프로세스일 수 있다). 8절.
- 조기 중단은 `-USR1`, 시험 완료는 `-USR2`. `-TERM`도 **abort 요청**이며 강제 종료가 아니다. 신호를 못 보내도 lease가 지나면 감독이 스스로 회수한다.
- 신호 뒤에는 `watch`가 돌아올 때까지 기다린다. 그 사이에 수동 DELETE를 보내지 않는다.

---

## 8. 중단·회수·인수

실행 위치: control01 **콘솔**(또는 인수자가 확보한 세션), 0.2 블록. **기존 관리 인증(`$KC`)** 으로 한다. token에 의존하지 않으며, token이 만료·소실돼도 이 절은 그대로 쓸 수 있다.

### 8.1 상태 읽기 (모두 읽기. 이름 끝의 번호는 다시 읽을 때마다 올린다)

```sh
N=1
$REC 8-1-ident-$N  $PY -B "$AUX/tools/ident.py" "$SES/input.json" "$SES/evidence/supervisor.jsonl"
$REC 8-1-watch-$N  $G watch --journal-dir "$SES/journal" --poll-seconds 1 --window-seconds 0
$REC 8-1-steps-$N  /usr/bin/grep -a -o -E '"step":"[A-Z]+"' "$SES/evidence/supervisor.jsonl"
$REC 8-1-gnp-get-$N $KC get --raw="$GNP"
$REC 8-1-gnp-info-$N $PY -B "$AUX/tools/objinfo.py" "$RES/8-1-gnp-get-$N.out" GlobalNetworkPolicy p1-mon-if06b-worker03-to-monitor01-canary
sudo -n cat "$RES/8-1-ident-$N.out" "$RES/8-1-watch-$N.out" "$RES/8-1-steps-$N.out" "$RES/8-1-gnp-get-$N.rc" "$RES/8-1-gnp-get-$N.err" "$RES/8-1-gnp-info-$N.out"
sudo -n pgrep -af 'guardian.py run'
```

`pgrep`은 보조 목록이다. 현재 객체는 **GET의 원본(`.rc`·`.out`·`.err`)을 먼저 남기고**, 그 원본이 객체일 때만 요약한다.

| `gnp-get` `.rc` / `.err` | `gnp-info` | 뜻 |
|---|---|---|
| 0 | `OBJECT_OK … uid= rv= spec_sha256= finalizers= deleting=` | 객체가 있다 |
| 1, `.err`에 `(NotFound)` | `STOP_EMPTY_RESPONSE` | **명시적 부재** |
| 1, `.err`에 `(Forbidden)` | — | 인증·권한 문제. 부재가 아니다 |
| 1, timeout·연결 오류 | — | 읽지 못했다. 부재가 아니다. 다시 읽는다 |
| 0 | `STOP_…` | 응답을 해석하지 못했다. 부재도 존재도 아니다 |

### 8.2 감독의 상태와 행동

| 관측 | 상태 | 행동 |
|---|---|---|
| `GUARDIAN_ALIVE`, `watch`가 `WRITER_STILL_HOLDING…`, 종결 행 없음 | **감독 진행 중** | 수동 DELETE 금지. 조기 회수는 7-4의 식별 뒤 `-USR1`. `watch`를 유지 |
| `run` launcher가 rc 4, journal 없음 | **`NOT_STARTED`** | POST 0건. 이 회차는 요청 없이 끝. 원인을 고쳐 새 `S`로 |
| `FINAL`이 `ABSENT_BASELINE_UNVERIFIED`, `watch` rc 0 | **자동 회수 종결** | canary 부재만 확정. 6.4와 기준 복귀로 |
| `FINAL`이 `HANDOFF`, `watch` rc 3 `HANDOFF`, `GUARDIAN_GONE` | **HANDOFF** | 8.1의 현재 객체로 8.3 판단 |
| `GUARDIAN_GONE`, `watch`가 `WRITER_GONE_WITHOUT_TERMINAL` | **감독 소실** | 8.1의 현재 객체로 8.3 판단 |
| `GUARDIAN_ALIVE`인데 회수 기한이 지나도 종결이 없음 | **종료 확인 불가** | 새 시험 요청 중단. `-USR1` 또는 `-TERM`으로 abort를 요청하고 기다린다. **종료가 확정되지 않는 동안 수동 DELETE를 하지 않고 콘솔 인수 상태를 유지한다** |
| `ident`와 `watch`가 서로 어긋남(한쪽은 살아 있다, 한쪽은 락이 풀렸다), 또는 `STOP_UNREADABLE_STATE` | **판정 불가** | 다시 읽는다. 어긋남이 풀리지 않으면 수동 DELETE로 넘어가지 않고 인수 상태 유지 |

**수동 삭제(8.3)로 넘어가는 조건은 둘 다다:** `ident`가 `GUARDIAN_GONE`이고 `watch`가 락이 풀린 결과(`HANDOFF`·`WRITER_GONE_WITHOUT_TERMINAL`·`ABSENT…`)를 냈다. 감독을 강제로 끝내는 자동화는 만들지 않았다. 사람이 감독을 끝내기로 정하면 그 결정과 시각을 기록하고, 끝난 것을 위 두 조건으로 확인한 뒤에만 8.3으로 간다. **예외는 하나뿐이다:** control01이 재부팅돼 `ident`가 `STOP_WRONG_BOOT`만 내는 경우에는 8.2a의 확인 기록이 `GUARDIAN_GONE`을 대신한다.

### 8.2a 같은 control01이 재부팅된 뒤 (`ident`가 `STOP_WRONG_BOOT`)

canary가 만들어진 뒤 control01이 재부팅되면 이전 감독은 다시 시작되지 않고, tmpfs의 token도 사라졌을 수 있다. `ident.py`와 `gate.py`는 boot가 다르면 계속 거부한다. **그 거부는 옳고 바꾸지 않는다**(새 요청과 신호를 막는다). 다만 `STOP_WRONG_BOOT`만으로는 삭제를 허용하지 않으므로, 아래를 읽어 "같은 호스트의 재부팅으로 이전 감독이 사라졌다"를 따로 확인한다.

실행 위치: control01 콘솔, 0.2 블록, 기존 관리 인증. 모두 읽기다.

```sh
N=<이 회차에서 쓰지 않은 결과 접미사>
$REC 8-2-reboot-host-$N /bin/sh -c 'hostname; cat /sys/class/dmi/id/product_uuid; cat /proc/sys/kernel/random/boot_id'
$REC 8-2-reboot-arming-$N /usr/bin/head -n 1 "$SES/evidence/supervisor.jsonl"
$REC 8-2-reboot-cluster-$N $KC get namespace kube-system -o json
$REC 8-2-reboot-cluster-info-$N $PY -B "$AUX/tools/objinfo.py" "$RES/8-2-reboot-cluster-$N.out" Namespace kube-system
$REC 8-2-reboot-watch-$N $G watch --journal-dir "$SES/journal" --poll-seconds 1 --window-seconds 0
sudo -n cat "$RES/8-2-reboot-host-$N.out" "$RES/8-2-reboot-arming-$N.out" "$RES/8-2-reboot-cluster-info-$N.out" "$RES/8-2-reboot-watch-$N.out"
```

**다섯 가지가 모두 맞을 때만** "동일 호스트 재부팅으로 이전 감독 소실 확인"이라고 기록하고, 그 기록으로 8.3에 들어간다.

| 확인 | 근거 | 맞는 경우 |
|---|---|---|
| 같은 호스트 | `reboot-host`의 hostname·product UUID | 회차 기록(입력표의 실측 근거: `k8s-control01`, `80724d56-7c17-f8a0-b2ea-ece7a154e24b`)과 같음 |
| 재부팅됨 | `reboot-host`의 boot ID, `reboot-arming`의 `binding.host_boot_id` | **서로 다름** |
| 같은 회차 | `reboot-arming`의 `binding.session_id`, `$SES/input.json`의 `session_id` | 같음 |
| 같은 cluster | `reboot-cluster-info`의 `OBJECT_OK … uid=`, 입력의 `expected_cluster_uid`, `reboot-arming`의 `binding.cluster_uid` | 셋이 같음 |
| 이전 writer 없음 | `reboot-watch` | journal을 읽을 수 있고 락이 풀린 결과(`HANDOFF`·`WRITER_GONE_WITHOUT_TERMINAL`·`ABSENT…`) |

하나라도 어긋나면 들어가지 않는다: 락을 아직 누가 쥐고 있음(`WRITER_STILL_HOLDING…`), 다른 호스트·cluster·회차, 식별 값을 읽지 못함, journal을 읽지 못함(`HISTORY_UNREADABLE`·`NO_SESSION_FILES`), 어느 명령이든 조회 실패. 그때는 수동 DELETE를 하지 않고 콘솔 인수 상태를 유지하며 원인을 조사한다.

- 이전 boot의 PID에 신호를 보내지 않는다. 그 번호는 지금 다른 프로세스일 수 있다.
- journal·`ARMING`·`input.json`의 boot 값을 현재 값으로 고치지 않는다. 이전 감독을 다시 실행하지 않고, 쓴 `$SES`에서 `run`을 다시 하지 않는다.
- 이전 boot의 `expires_mono`를 현재 boot의 시계와 비교하지 않는다(boot마다 기준이 다르다). 그 회차의 시각은 증거로만 보존한다.
- 8.3은 그대로 적용한다: `watch`가 돌려준 UID와 현재 객체의 UID·spec pin·finalizer·삭제 상태를 대조하고, 수동 DELETE는 **현재 조회의 UID+RV 조건**을 유지한다. 409·403·timeout에서 force나 이름만 쓴 삭제로 우회하지 않는다.
- 현재 객체가 명시적 NotFound면 삭제 없이 부재를 기록한다. DELETE의 성공 응답과 부재를 구분한다.
- token을 다시 발급하거나 SA를 다시 만드는 단계는 없다. 남은 임시 RBAC 객체는 회수가 끝난 뒤 9.1로 정리한다(token 파일이 사라졌어도 SA가 남아 있으면 그 token은 만료 전까지 유효할 수 있다).
- 이 분기는 실제 재부팅으로 시험한 적이 없다. 카드의 연결만 확인했다.

### 8.3 현재 객체에 대한 판단과 조건부 수동 삭제

| 현재 객체 (8.1) | 판단 |
|---|---|
| 명시적 부재 | 삭제할 것이 없다. journal·증적과 함께 기록 |
| `OBJECT_OK`이고 UID가 journal의 `uid`(`watch` 출력)와 같고, `spec_sha256`이 검토 pin과 같고, `finalizers=False deleting=False` | 이 회차의 객체. 아래 조건부 삭제 |
| journal에 `uid`가 없음(소유 미확정) | `unowned_create_response`의 UID는 단서일 뿐이다. 이 회차가 만든 것인지 사람이 다른 근거와 함께 판단한다. 근거가 모자라면 **지우지 않고 인수 상태로 남긴다** |
| UID나 spec이 다름, finalizer 있음, 삭제 중 | 삭제하지 않는다. 출처 조사 |
| 부재도 존재도 아닌 결과 | 다시 읽는다. 읽지 못한 것을 부재로 적지 않는다 |

```sh
DUID=<8.1 gnp-info의 uid>
DRV=<8.1 gnp-info의 rv>
printf '%s' '{"apiVersion":"v1","kind":"DeleteOptions","preconditions":{"uid":"'"$DUID"'","resourceVersion":"'"$DRV"'"}}' | $REC 8-3-gnp-delete $KC delete --raw="$GNP" -f -
N=2
$REC 8-1-gnp-get-$N  $KC get --raw="$GNP"
$REC 8-1-gnp-info-$N $PY -B "$AUX/tools/objinfo.py" "$RES/8-1-gnp-get-$N.out" GlobalNetworkPolicy p1-mon-if06b-worker03-to-monitor01-canary
sudo -n cat "$RES/8-3-gnp-delete.rc" "$RES/8-3-gnp-delete.out" "$RES/8-3-gnp-delete.err" "$RES/8-1-gnp-get-$N.rc" "$RES/8-1-gnp-get-$N.err"
```

- DELETE는 UID와 **방금 읽은 RV**를 조건으로 한다. DELETE가 성공 응답을 줘도 그것은 ACK일 뿐 부재가 아니다. 부재는 그 뒤 GET의 rc 1 + `(NotFound)`다.
- 409면 조건을 빼거나 force로 바꾸지 않고 8.1부터 다시 읽는다. 403이면 인증 경로를 본다.
- 삭제 뒤 GET이 실패(timeout 등)했으면 `NotFound`로 적지 않는다. 다시 읽는다.
- journal·증적·`$RES`의 파일은 고치거나 지우지 않고, 쓴 `$SES`에서 `run`을 다시 하지 않는다.

---

## 9. 정리와 증적

### 9.1 임시 권한 정리 (회차 종결 뒤)

**시작 조건:** 8.2에서 감독이 끝났음이 확인됐고(자동 회수 종결, 또는 인수 완료) canary가 명시적으로 부재다. **감독이 그 token으로 회수하는 중에는 시작하지 않는다.** SA나 binding을 먼저 지우면 감독의 요청이 인증·인가 실패가 될 수 있다.

2.6과 같은 명령을 단계 이름만 `9-1c`·`9-1b`·`9-1a`로 바꿔 Binding → Role → SA 순으로 한다. 대상은 2.3의 영수증 UID와 현재 UID가 같은 객체뿐이다. 준비 중 실패로 2.6을 이미 했다면 다시 하지 않는다.

```sh
# token 파일 (쓰기). 삭제는 무효화가 아니다. 무효화는 만료 또는 위의 SA 삭제다
sudo -n sh -eu -c 'rm -f "$1/token"; rmdir "$1"; test ! -e "$1"' sh "$TOK"; echo "token_cleanup_rc=$?"
$REC 9-1-tok-absent /usr/bin/test ! -e "$TOK"
```

UID가 영수증과 다르거나 UNKNOWN인 객체는 지우지 않고 보고한다. 기존 credential을 쓴 회차라면 이 절에서 지울 객체가 없다.

### 9.2 증적 모으기

| 원본 위치 | 내용 |
|---|---|
| control01 `$SES/journal/` | `journal.jsonl`, `writer.lock` |
| control01 `$SES/evidence/` | `supervisor.jsonl` |
| control01 `$SES/results/` | 단계별 `.time`·`.out`·`.err`·`.rc` (validate, preflight, run launcher, watch, gate, ident, RBAC 영수증, 수동 GET·DELETE, 전후 비교) |
| control01 `$SES/input.json`, `$SES/supply/SHA256SUMS`, `$SES/aux/*/SHA256SUMS` | 입력과 공급 대조 |
| control01 `$SURV/` | `survival.jsonl` |
| worker03 `~/if06b-<session>/worker/`, `…/worker-out/` | 요청 결과, route, 캡처 |
| mgmt-gw01 `~/if06b-<session>/gateway-in/`, `…/gateway-out/`, `/root/if06b-policy-*` 2회분 | 캡처, 정책 원본 |
| monitor01 `~/if06b-<session>/monitor-in/`, `…/monitor/` | 캡처, listener, firewalld 전후 |
| MON 관측자 | `mon-pre.txt`, `mon-post.txt` |

```sh
# control01: 원본의 해시 목록 (읽기)
$REC 9-2-sums /bin/sh -c 'cd "$1" && find journal evidence results input.json supply/SHA256SUMS aux -type f ! -name "9-2-sums.*" -print0 | LC_ALL=C sort -z | xargs -0 sha256sum' sh "$SES"
```

- 순서: 각 위치에서 해시 목록을 만든다 → 기존 승인 전송 경로로 내보낸다 → 받은 사본에서 `sha256sum -c`로 대조한다 → 검토용 목록과 한계를 적는다. 새 archive 서비스나 exporter를 만들지 않는다.
- **내보내지 않는 것:** `$TOK`(token), 관리 kubeconfig, CA 개인키류. `$RES`에는 token 값이 없다(2.5가 token을 `$REC` 밖에서 다루기 때문이다).
- 빠졌거나 깨진 파일은 숨기지 않고 `NOT_VERIFIED`로 적는다. 유리한 결과를 얻으려고 다시 실행하지 않는다.
- `$SES`·`$SURV`의 보존·폐기는 증적 편입 뒤에 따로 정한다.

---

## 10. 판정 연결 — 무엇을 어느 파일로 판단하는가

네 가지를 **따로** 판정한다: canary 부재, 기준 복귀, 증적 완전성, AC. 앞의 것이 됐다고 뒤의 것이 된 것이 아니다.

| 판정 | 근거 파일 | 기준 |
|---|---|---|
| canary 부재 | `journal.jsonl`의 종결, `7-2-watch.out`, 수동 인수면 `8-1-gnp-get-N.rc`·`.err` | 명시적 NotFound만. DELETE ACK나 읽기 실패는 부재가 아니다 |
| 기준 복귀 | `6-diff-*.rc`, monitor01 `fw-pre`/`fw-post`, gateway 수집 2회, `mon-post.txt`, worker03 `post-deny.*` | HEP·GNP·firewalld·gateway 정책·NAT가 전과 같고, 새 연결이 다시 막히고, MON이 23 / 23 / 0 / 정상 |
| 증적 완전성 | `supervisor.jsonl`, `$RES`, 각 캡처의 `cap-rc`·`cap-stats` | 분리 실행에서는 온전한 FINAL 줄만으로 그 줄의 fsync를 확인할 수 없다. 회수 상태는 journal 기준 |
| AC | 위 전부 + 증적 PR과 담당 리뷰 | 회차가 통과해도 자동으로 체크하지 않는다 |

**8443 귀속 — H04가 정한 행렬.** 요청의 5-tuple(`t8443.out`의 `local=…`, `remote=…`), rc, 시각을 네 캡처와 잇는다.

| 캡처에서 본 것 | 허용되는 결론 |
|---|---|
| `gateway-in`에 그 SYN 있음, `gateway-out`에 없음, 같은 창의 443이 네 지점에서 양방향 유효, 네 캡처 모두 유효(6.2), gateway 정책·route가 전후 같음 | gateway 구간에서 소실되는 것과 정합. 특정 rule의 DROP 확정은 아니다(요구되지도 않는다) |
| `worker-out`에 없거나 `gateway-in`에 없음 | gateway 귀속 불가. 상류·캡처·경로 조사 |
| `gateway-out`에 있음, `monitor-in`에 없음 | 두 지점 사이 또는 관측 공백. PASS 아님 |
| `monitor-in`에 SYN 도착, SYN-ACK 없음 | 수신 노드 단계 조사. 특정 firewalld 규칙 귀속 불가 |
| 연결 성공, SYN-ACK, 예상 밖 응답, 캡처 무효, 요청이 TLS·CA·bind 단계에서 실패 | 차단 PASS 아님. `NOT_VERIFIED`. 추가 요청 없이 회수 |

**단계별로 실패했을 때 어디로 가는가:**

| 실패한 곳 | 다음 변경 | 부분 정리 | 인수·보고 | 남는 증적 |
|---|---|---|---|---|
| 1 배치 | 중단 | 없음(`$SES`를 그대로 두고 새 `S`) | 화면의 `…_rc` | `$SES` |
| 2.2 사전·dry-run | 생성 0 | 없음 | 기존 객체가 있으면 조사 | `2-2-*` |
| 2.3 생성 중 | 뒤 객체·token·run 0 | 2.6 (영수증 있는 것만) | UNKNOWN 객체는 인수 상태 | `2-3*`, `2-6*` |
| 2.4 권한 불일치 | token 0 | 2.6 | 어느 검사가 달랐는지 | `2-4-*` |
| 2.5 token | run 0 | 수명 초과면 2.6, 나머지는 보존 | 앞 token의 유효 가능성 | `2-5-*` |
| 3 validate / 5 preflight | run 0 | 없음(서버 상태 불변) | 실패한 검사 | `3-1-*`, `5-1-*` |
| 4 survival | A안 불가 | 없음 | B안으로 | `$SURV`, `4-*` |
| 6 관측 준비 | run 0 | 없음 | 준비 안 된 지점 | 그 지점 디렉터리 |
| 7 `NOT_STARTED` | 요청 0 | 없음 | 원인, 새 `S` | `7-1-*` |
| 7 소유 미확정·중단 | 요청 0(이미 나간 수는 그대로 기록) | 감독의 자동 회수 또는 8절 | 8.2의 상태 | `7-*`, journal, 증적 |
| 7 회수가 HANDOFF·감독 소실 | 요청 중단 | 8.3(조건이 맞을 때만) | 현재 객체, 귀속 판단 | `8-*` |
| 7 도중 control01 재부팅 | 요청 중단. 신호·재실행 없음 | 8.2a의 다섯 확인이 모두 맞을 때만 8.3 | 어긋나면 인수 상태 유지, 조사 | `8-2-reboot-*`, `8-*`, 보존된 journal·증적 |
| 9.1 정리 | — | UID가 같은 것만 | 다른 UID·UNKNOWN은 보고 | `9-1*` |

---

## 11. 이 초안이 아직 모르는 것

- 모든 명령은 실행해 본 적이 없다. 로컬에서 확인한 것은 도구의 MOCK, `record.sh`의 실제 동작(Git Bash), 셸 블록의 구문뿐이다(`verification-local.json`). root 0700 아래에서의 동작, `kubectl`의 실제 오류 문구, `create token`의 실제 수명, `loginctl`·`tcpdump`·`curl` 출력은 현장에서 본다.
- `.err`의 `(NotFound)`·`(Forbidden)`·`AlreadyExists` 문구는 kubectl의 통상 출력을 전제로 했다. 다르면 관측한 원본에 맞춰 표를 고친다.
- `monitoring-api` namespace가 지금 있는지는 2.2에서 읽는다(10/6 선례로만 안다).
- `.109`의 구성은 조회되지 않았다.
- MON 기준선을 읽는 기존 명령의 위치, gateway·monitor01·worker03의 인터페이스·계정·포트·live 기대값은 현장 입력이다.
- 콘솔 인수자가 control01 콘솔 로그인·sudo·`$KC`를 실제로 쓸 수 있는지는 확인되지 않았다.
- 후보 숫자는 전부 미승인이며 입력표의 한 표에서 채택한다.
- `gate.py`의 `SNAPSHOT_ELIGIBLE`과 `ident.py`의 `GUARDIAN_ALIVE`는 읽은 순간의 사실이다. 읽기와 요청·신호 사이의 틈은 절차(감시 유지, 중단 전달, 직전 재확인)로 좁힐 뿐 없애지 못한다.
- 8.2a(재부팅 분기)와 6.0의 시간 예는 문서상의 연결과 산술이다. 재부팅을 실제로 일으켜 보지 않았고, 실제 회차의 지연은 예와 다를 수 있다.
