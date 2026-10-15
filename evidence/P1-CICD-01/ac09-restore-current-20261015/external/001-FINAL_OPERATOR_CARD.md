# AC09 R1→R2 및 유한 수동복구 최종 검토 카드

2026-10-15T15:27:04.491983+09:00 · 중앙 최종 검토 후보 · **Runtime GO 없음 / W 미확정 / 서버 공급·실행 없음**

**ROUND5 반영:** [중앙 재검토 R2](../../../reviews/phase1-ac09-helpers-review-20261015/REVIEW_R2.md)에서 B1/B2 해소·새 기술 차단 없음, 실제 main22/HTTP18/동일raw1 검증을 확인했다. helper3개 해시 불변. 이하영 [15:02:48 시각 방식 수용](https://github.com/321Team/infra-cicd/issues/11#issuecomment-6185621755)도 반영했다. 아래 작성자 회귀는 이전 수행 기록이다.

**작성자 검증 이력:** 중앙이 재현한 승인 바이트 변경 결속·HTTP 원문 파서의 실질 결함 2건을 수정했다. 실제 main 제어 흐름 모의21개·HTTP wire16개와 기존 local5개 검증을 통과했다. [수정·검증 기록](../round4/FIXES_APPLIED.md)의 정확 source 해시는 중앙 재검토 완료본과 일치하며, 이 로컬 수정 검증을 독립 승인이나 Runtime 성공으로 표시하지 않는다.

이권욱 본인의 “내가 할거고, 바로 착수 가능” 및 실제 `k8s-control01/server02` VM 콘솔·두Deployment3/3 회신을 [중앙 원문](../../phase1-central-control-20261015/AC09_OPERATOR_CONSOLE_RECEIPT.txt)에 연결했다. 사람·가용성·콘솔 로그인·DB 입력은 다시 묻지 않는다. 이 카드는 남은 **정확 창·회차·복구 권한**을 중앙이 한 번에 확인하기 위한 구체안이다.

## 1. 확정 입력과 아직 미승인인 범위

- 코드: infra-cicd main `fddc76e1c261cd938f06211b7ed035fdcb32e606`, PR86 승인·병합 완료. 14:33 재조회 동일, 작업tree clean. 기존 CI754/skip0 재사용, 재실행0.
- R1 request `cd01e613-d576-41eb-8354-8e9283d0f60d`, plan SHA `6e622c0bf539830c77cc841beb6852b0db65a9652822754d30141e587ca71d2d`.
- R2 request `3451e56c-57bc-490e-8d15-6cede958229f`, plan SHA `3b928b2c74600d81066f4577a0b3095df027351434137249a67ef5e328720183`.
- native bundle SHA `16366261081cf95639480cfb9256255541bc1099fde717225e4ad8f6e322ae8b`.
- APP14:00 DB 정적 진입조건 충족 유지. 추가SQL·migration·DB재인수 요청 없음. 구버전 실제 업무 호환성은 미래 승인된 R1에서 검증.
- SEC 이하영 [6185120164](https://github.com/321Team/infra-cicd/issues/11#issuecomment-6185120164)의 조건부 수용 및 [SEC addendum](../../../reviews/phase1-sec-20261015/AC09_SEC_ACCEPTANCE_ADDENDUM.md) 적용. 이는 Runtime GO나 전체 외부경로 차단 확인이 아니다.

| 대상 (namespace `fds-app`) | 고정 UID | R1 이전 / R2·긴급복구 현행 digest |
|---|---|---|
| transaction-api | `8a2af808-ec33-41f2-80b5-addde4e28910` | 이전 `a7093136d12640da00570c18ed278eacbb8e9ba3637c7d509571346eac45cc33` / 현행 `338b8a2871507ce8b42deedc916b26e350577ee6efd18df23d7ff2dd4b17dff0` |
| fds-engine | `bf825dec-465b-4603-8b71-f768d195531c` | 이전 `5e2a081cd51a957c3fad038b3eab07884c446ea3c2a814a905e3f41c24f67369` / 현행 `8b257adb08b6d381f72b66d3386efea6112a8f072ecfafcbcd463bcd1c3be89d` |

모든 image는 `10.1.93.54/fds/<service>@sha256:<digest>`이다. replicas3·기존 전체 spec 중 image 이외 필드는 그대로 둔다. 정확 SHA·UID 또는 non-image spec이 바뀌면 이 후보로 쓰지 않는다.

## 2. 권장 콘솔·인증·공급

[MANAGEMENT_CONSOLE.md](../round4/MANAGEMENT_CONSOLE.md)의 **기존 control01 VM / server02**를 사용한다. 14:35:56 정상 SSH의 기존 kubeconfig/CA/API GET·인증서/RBAC 확인과 사용자 실제 VM 콘솔 출력을 함께 연결했다. kubeconfig는 `/home/server02/.kube/config`, API는 `https://10.1.93.109:6443`, CA는 `/home/server02/FDS_CICD_PublicCA.uua3ecs6/kubernetes-ca.pem`이다. 기존 client certificate의 `kubeadm:cluster-admins` binding은 기술적 PATCH 경로이며 이번 작업의 운영 권한은 아래 유한 scope로 제한한다. sudo·새 계정·새 권한·개인키 복사 불필요.

[RUNNER_AUTH_READINESS.md](../round4/RUNNER_AUTH_READINESS.md): 기존 **native Runner #2 `cicd-runner01` online/idle**, Listener PID1988·Worker0·정확 label 확인. **false2+true2 최대4job을 기존 Runner에서 순차 실행, 신규 Runner 등록0**을 권장한다. 이전 “최대4ephemeral 공급” 후보를 실제 경로에 맞춰 정정했다. Ansible 일회 Runner 인증을 재사용하는 방식이 아니다. sudo 비대화식 점검은rc1이지만 선택한 workflow/broker/staging은 정상 계정만 사용하므로 sudo 재입력 요구 없음. 14:45:33까지 CP1 SA UID GET와 Runner API TLS/CA 확인, TokenRequest/TokenReview 미실행.

W 시작 전에 CICD가 fresh 유휴·비중첩·HEAD/해시·normal SSH·입력 경로를 확인하고, 승인 후 정확 입력/이 카드의 helper를 정상 계정의 새0700 경로에 배치·해시 대조한다. 공급/false검증 시간을 창 밖 무승인 실행으로 빼지 않는다. 사용자에게 W가 시작된 뒤 새 인증을 갑자기 요청하는 안은 채택하지 않는다. 새로운 인증 실패가 발견되면 창 진입 전에 보고한다.

## 3. 정상 회차·시간·수량

중앙이 exact KST `W`, `W+25`, `W+40`, `W+45`, 별도 `W+60`을 계산·확정한다. 지금 시각부터 카운트하지 않는다.

1. 승인 바이트·댓글·최종record를 결속하고 **R1/R2 execute=false 각1회**. `SUPPLIED_BYTES_MATCH`, Token false, Deploy NOT_EXECUTED 확인. 새Run/Attempt1로만 진행하며 dispatch 응답 불명 시 재전송 금지.
2. pre edge2GET 원문·앱baseline/비중첩 확인 후 **R1 execute=true1회**, 실제Run binding과 CP1 broker 연결1회. TokenRequest 명령1회/TTL900. 현행→이전 API→engine 순. R1 `allow_rollback=true`는 명확 실패 때 반영된 대상을 **현행으로** 보상하는 범위.
3. 이전 두서비스Ready 후 during edge2GET·기존 승인경로 Health·P01deposit1건·동일ID DB/동일Pod계측 대조. POST 유실/timeout은 재POST하지 않고 DB확인. 새 DB catalog수집·마이그레이션 없음.
4. **R2 execute=true1회**, 별도Run/승인·TokenRequest 명령1회. 이전→현행. `allow_rollback=false`: 실패 때 구버전 역복귀를 하지 않고 아래 콘솔 인수.
5. 현행 두Ready3·이전Pod부재·업무metrics404·전용metrics200/target6·현행P01deposit1건/동일ID DB·계측 대조, 원본/claim보존·임시socket/credential참조·Job종료·점유반환 확인.

정상 회차 총 최대4job/Attempt1, TokenRequest 명령2회(TTL각900), 업무POST2건, 추가 edge4GET. 정상imagePATCH4회, R1명확실패의 현행보상은 최대2회. **별도 콘솔 수동 현행복원은 최대각1회/총2PATCH 후보**이며 정상 회차 실행권한에 숨겨 포함하지 않는다. 이 상한들은 각 경로의 허용 최대이며 모두 의도적으로 실행하는 시험은 아니다.

- `P≤W+10`; R2 **첫현행PATCH≤P+15**; 노출회수≤P+30; 정상정리≤W+45.
- R1 승인창 후보W~W+25, R2 W~W+40. 기존 시작예산630초·broker발급전640초·TokenTTL900/실제expiry 검사 유지. 승인창/토큰 부족 시 자동재발급·재실행 없음.
- R1 Ready지연/관측오류로 P+15를 위협하면 추가업무시험·POST를 멈추고 현행복귀 우선. 검증2POST를 채우려고 복원을 지연하지 않는다. 이 경우 미수행 검증은 미완료로 기록.
- **P+30 미회수는 즉시 SEC 이하영 통지·현행복원 최우선. W+45 이후 잔여노출은 사고기록+SEC 재판단**, 자동 위험수용 연장 없음. 연락/외부기록은 중앙·이권욱이 담당하며 이 준비 세션은 메시지를 발송하지 않았다.

## 4. edge 원문4GET — 실질 보완

기존 `fds-ansible01/server01_ansible → edge01/svc_ansible` 일반 권한. edge가 자기 IP **`http://10.1.93.50:80/metrics`**, **`http://10.1.93.50:80/metrics/`**를 GET, **Host `10.1.93.50`** 고정. sudo/새 source/Runner NodePort·NP/GNP/RBAC/edge 변경 없음.

- pre: R1 시작 전 각1건. during: 이전두Ready·실제노출 상태를 연결한 뒤 각1건. 총4건, 자동redirect추적·재시도0. 기존엔 해시만 남겼지만 이번은 [edge_metrics_raw.py](../round4/edge_metrics_raw.py)가 request와 **HTTP status/header/Location/body wire 원문**을 보존한다.
- 요청당 전체deadline4초, 응답상한262144B. 상한 초과·timeout·빈 HTTP 응답·잘린 framing·403/5xx·200은 PASS가 아니다. 유효한 0길이 body는 HTTP 상태·경로로 판정한다. `/metrics`404, `/metrics/`404 또는301/302/303/307/308 + 동일 `.50:80`의 `/metrics` Location만 정상. 다른호스트/포트/경로·Location누락은 STOP, 자동방문 없음.
- pre오류: R1 금지. during오류: 추가시험/POST중단·중앙/SEC통지·현행복원 우선. 두이전Ready와 유효권한이면 R2, mixed/unknown이면 콘솔절차. 실패했던 GET을 자동추가해서4건을 넘기지 않는다.
- phase/실제Run/source계정·로컬socket/목적지/Host/경로/시작종료KST/HTTP/RC/원문bytes/SHA를 비공개 보존. 공개는 요약·해시. 이2경로 표본을 모든URI/Host/외부Client 차단으로 확대하지 않는다.

Windows CICD 실행 위치는 형제 `../round4` 폴더이며, 실제GO후 정확승인과 during 노출기록을 결속해야만 실행한다:

```powershell
python -B run_edge_capture.py --phase pre --authorization runtime-observation-authorization.json
python -B run_edge_capture.py --phase during --authorization runtime-observation-authorization.json
```

위 두 명령은 서로 다른 시점에 CICD가 실행한다. 기본python이 없으면 확인된 번들Python을 사용한다. `[phase].claim`은 재실행 차단용이며 삭제해서 재사용하지 않는다. 승인 template은 실행을 거부한다. 아직 collector를 edge에 실행하지 않았다.

## 5. 실패 분기 및 별도 유한 긴급복구 권한 후보

| 상태 | 정확 행동 |
|---|---|
| 정상 R1/R2 | 병합된 workflow/broker와 각회차 승인만 사용. 별도 콘솔PATCH 없음 |
| R1 명확한 실패·권한유효 | 기존 승인범위의 adapter 현행보상 결과/claim을 확인. 현행2Ready이면 추가PATCH 없음. 보상실패/혼합이면 writer정지 후 콘솔 인수 |
| R1 성공 뒤 업무검증 실패 | 자동보상 발생으로 가정하지 않음. 두이전Ready·시간/승인유효면 별도R2를 앞당김. 조건불충족이면 콘솔 인수 |
| mixed/Ready불량 | 정상R2의 두이전Ready baseline을 우회하지 않음. 전체spec의image외 불변·exactUID·old/current pair를 읽고 **남은old→current만**별도수동복구. 이미current인데불량이면image재PATCH/restart하지않고관측·사고인수 |
| PATCH UNKNOWN/체크포인트실패 | 기존Job/adapter/broker 추가writer 종료를 실제확인, 원본/claim보존. 마지막요청의10초기한 뒤 적어도10초가 지난 상태를 새GET으로대조. 미확인인채 재PATCH금지. 판명된old/current·동일UID/spec에만별도후속판단. 동일수동target의claim은 결과불명/거부라도 재시도금지 |
| Runtime승인/단기Token만료 | 기존Token·R1/R2 작업은중단. **별도승인된**관리인증서·수동복구scope가유효할때만아래명령. 기술적cluster-admin보유로실행권한을추정하지않음 |
| W+45 노출잔여 | SEC수용범위밖사고기록·재판단. 아래별도W+60권한이승인됐다면그정확현행복원만유효. 시험/POST/구버전적용·위험수용자동연장없음 |
| 별도권한만료/철회·UID/spec/이미지불명 | 추가PATCH중단·이미확인된사고/상태/원본을중앙·SEC에인계. 새로운유한복구승인없이강행하지않음 |

**긴급복구 후보:** 이권욱, 정상 `server02@k8s-control01` 관리콘솔, **W~W+60**. 위exact2UID의 old→current image필드만 각최대1PATCH/총2회. current→old·다른UID/replicas/환경/Service/DB·새Token/권한·rollout undo/restart/force·Pod삭제·물리호스트종료는없다. 기존 자동writer가멈췄고현재결과가판명된뒤만허용한다.

15분 추가상한의 산출: 두대상 PATCH 각8초 + rollout관측 각300초 + 사전GET/명령20초 + 직접metrics/health관측120초 + 보고120초 = **876초(14분36초)**. 이는 안전조건이유지되는경우의실행/관측예산이지복구성공보장이아니다. helper는 남은old수×308+260초가남지않으면 **새PATCH자체를시작하지않는다**. 2개old이면876초,1개old이면568초. 연장권한이있어도늦게시작해예산이모자라면STOP한다. API/서비스장애·사람지연이길면별도인계·재판단이필요하다.

## 6. 콘솔의 실제 수동복구 명령

[console_restore_current.py](../round4/console_restore_current.py)는 로컬 준비물이며 **아직서버에배치하지않았다**. 최종GO후 CICD가 정상SSH로 `/home/server02/FDS_AC09_ConsoleRestore_20261015/` 새0700 폴더에 helper·실제승인 `recovery-contract.json`만0600으로공급하고해시를대조한다. 기존경로가있으면덮어쓰지않는다. [recovery-contract.TEMPLATE.json](../round4/recovery-contract.TEMPLATE.json)은승인아니며실행거부. 사용자에게코드입력/암호공유를요구하지않는다.

이권욱은 **CICD가 기존writer실제종료·원본인수·현재결과판명과아래4개변수를전달한후** 콘솔에서명령을한줄씩사용한다. 변수는현재원본에서CICD가작성한다. `UNSET`이남은경우시작하지않는다.

```bash
cd /home/server02/FDS_AC09_ConsoleRestore_20261015
python3 -B console_restore_current.py prepare --contract recovery-contract.json
```

이명령은두Deployment GET만실행하고private plan경로/해시와 `OLD_TO_CURRENT_CANDIDATE` 또는 `CURRENT_NO_PATCH`를출력한다. 정확UID·전체spec에서image외해시·old/current허용집합을검사한다. `prepare`가성공해도복구성공은아니다.

```bash
PLAN_PATH='UNSET_직전_prepare의_절대경로'
PLAN_SHA='UNSET_직전_prepare의_SHA256'
WRITERS_STOPPED_AT='UNSET_실제_writer종료_KST_ISO8601'
OUTCOME_RECONCILED_AT='UNSET_종료후10초이상_현재GET판명_KST_ISO8601'
python3 -B console_restore_current.py apply --contract recovery-contract.json --target transaction-api --plan "$PLAN_PATH" --plan-sha256 "$PLAN_SHA" --writers-stopped-at "$WRITERS_STOPPED_AT" --outcome-reconciled-at "$OUTCOME_RECONCILED_AT"
kubectl --kubeconfig=/home/server02/.kube/config --server=https://10.1.93.109:6443 --certificate-authority=/home/server02/FDS_CICD_PublicCA.uua3ecs6/kubernetes-ca.pem --request-timeout=6s -n fds-app rollout status deployment/transaction-api --timeout=300s
```

첫대상이이미current면해당apply를하지않는다. engine도복원이필요하면 **prepare를새로실행해새경로/해시를사용**, `--target fds-engine`·`deployment/fds-engine`으로동일한각1회명령을수행한다. 자동for-loop로두개를강행하지않는다. 첫PATCH가확정성공했으나Ready실패라면그상태를인계하고남은old만복원할지유효예산/현재GET으로판단한다. UNKNOWN은판명전다음PATCH없음.

helper는최대60초된plan만사용하고GET후UID/RV/generation/name/image test를넣은JSON PATCH1회만수행한다. 원spec SHA확인과atomic RV/generation test로image외동시변경을막는다. request5초/process8초, durable target별claim을먼저생성하고어떤오류에도claim삭제·자동재시도·자동보상없음. 비0/timeout/예상밖응답은STOP. 성공출력도 `PATCH_CONFIRMED_READINESS_NOT_VERIFIED`이며Ready/metrics는별도판정한다. 파일mtime/해시및결과projection보존,전체API원문이나개인키를공개하지않는다.

완료관측:

```bash
kubectl --kubeconfig=/home/server02/.kube/config --server=https://10.1.93.109:6443 --certificate-authority=/home/server02/FDS_CICD_PublicCA.uua3ecs6/kubernetes-ca.pem --request-timeout=6s -n fds-app get deployment transaction-api fds-engine
kubectl --kubeconfig=/home/server02/.kube/config --server=https://10.1.93.109:6443 --certificate-authority=/home/server02/FDS_CICD_PublicCA.uua3ecs6/kubernetes-ca.pem --request-timeout=6s -n fds-app get pods -o wide
```

CICD는별도로각Pod의UID/imageID·이전Pod부재·직접업무404·전용metrics200/target6를기존관측경로로결속한다. 위GET의3/3만으로전체종료/AC09인수를선언하지않는다.

## 7. 수용된 시각 방식과 실제 회차 원본

SEC의 [결정6185621755](https://github.com/321Team/infra-cicd/issues/11#issuecomment-6185621755)으로 구간 증적 방식 수용·정확 계측 코드 변경 불요를 확인했다. **실제 회차 시한 준수는 아직 미판정**이다.

[TIMING_CONTRACT.md](TIMING_CONTRACT.md)에 실제6호스트/계정·원문수집 명령·전후 각1회·원 journal inode/mtime_ns/size/bytes SHA 보존·Run/approval/UID/chain 결속·오차 계산·미입증 분류를 확정했다. 준비 조회는 실제 회차 증적을 대신하지 않는다. 오차는 시작을 앞당기고 완료를 늦추며, 근거 부족은 '시한 미입증 / SEC 사후검토'로 남긴다. 실제P+30 통지/W+45 만료는 그대로다. 새 시계 설정·전체 노드 시험·계측PR를 요구하지 않는다.

## 8. 중앙이 한 번에 확인할 문안 후보

> 이권욱이확인한관리콘솔과이카드의정확두UID/이미지·해시를사용한다. 중앙이확정한KST W부터45분단독창에서false각1/true각1·TokenRequest각1·P01각1·edge원문4GET, R1현행보상true/R2역복귀false를승인한다. 별도긴급복구는W+60까지exact2UID old→current각최대1PATCH만위사전GET/상태판명/타writer종료/시간예산조건으로허용한다. W+45 위험수용을연장하지않고초과노출은사고기록·SEC재판단한다. 15/30분판정의시각구간증적방식과정확송신시각미계측한계를검토했다. 카드·helper최종SHA와exact시각을승인원문에결속한다.

이 문안은 **미승인 초안**이다. 시각 방식 수용과 helper 중앙 재검토는 완료됐고, 남은 것은 중앙의 exact 창·비중첩·정상회차 및 별도 유한 복구권한 확인이다. 이미 확인한 수행자/콘솔/DB를 다시 묻지 않는다. 실제 approvalJSON/Run/record는 권한 확정 뒤 생성하며 template을 승인으로 사용하지 않는다.

중앙의 [15:35 후보 결정 카드](../../phase1-central-control-20261015/AC09_RUNTIME_DECISION_CARD_20261015_1535.md)는 10/15 15:35~16:20, 별도 현행복구16:35까지인 **미승인·미예약 후보**다. 이 상세 카드와 대상/수량/고정 입력/중단·복구 조건의 중대한 충돌은 발견하지 않았다. 준비/공급/false 검증도 허용창에 포함하며 시작조건 미충족 시 자동연장하지 않는다.
