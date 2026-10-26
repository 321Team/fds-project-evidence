# 10/26 최종 회수 인계 — 기존 승인·담당·순서 연결

현재 준비 문서이며 아래 Runtime 회수는 아직 수행하지 않았다. **소비종료08:30, 정리·복구·원본반출·보고 완료12:00 KST** 유지. 권욱·재환08:30~12:00 가용 회신은 기존 확인을 재사용하며 재요청하지 않는다.

근거: [하영 작업창6378716458](https://github.com/321Team/infra-rosa/issues/8#issuecomment-6378716458), [재환 회수 가용6397638740](https://github.com/321Team/fds-project-baseline/issues/55#issuecomment-6397638740), [P8 기승인 saved Plan6357457266](https://github.com/321Team/infra-rosa/issues/12#issuecomment-6357457266), [#55 신규 작업파일 인계6402064218](https://github.com/321Team/fds-project-baseline/issues/55#issuecomment-6402064218).

## 순서와 실제 완료 조건

| 기존 목표/순서 | 실행·인수 | 실제 확인할 결과 |
|---|---|---|
| 08:30 소비종료 | 하영 앱0/Pod0, 재환 DB 조회, 권욱 인수 | 두 Deployment 기존 UID/승인 대상·replicas0, Pod0 뒤 **그 시점의** P2 출발지 DB세션0. 과거 앱0/DB0를 재사용하지 않으며 기존 내부 서비스 세션을 일괄 종료하지 않는다 |
| 08:35~08:55 | 하영 SA2 pull 참조 원복→정상 pull Secret→동일 P2 Robot 회수→DB Secret 회수 | 같은 기존 RUN의 자기 추가분/정확 UID·자원만. Robot 부재/인증거부, Secret·참조 readback. 만료시각 도래를 수동 회수 완료로 바꾸지 않는다 |
| DB Secret 회수 후 ~08:55 | 재환 같은 DB_RUN `20261023T1248` A2-OFF·tcpdump 종료/반출 | 승인된 rollback 경로, pg_hba/rich rule의 W0 해시 대조. 실제 현재 해시·RUN 불일치/결과 불명확이면 자동 재시도 없이 상태 인계. 이미 A3/API 시험 거래가 생성됐으므로 ‘10/23 이후 새 거래0’ 기준선을 현재로 오용하지 않는다 |
| ~09:05 | 하영 Harbor guard P2 줄·harbor01 반환 경로 원복 | 소유한 C2/C3 줄만, 기존 P1 서비스/다른 경로 보존·readback |
| ~09:30 목표, 기존10:10 전 착수 조건 | 하영 P8 saved Plan Apply1회 | 소비 종료·같은 Plan/state/대상 ID·승인 조건 유효성을 실제 확인. **SG 규칙2+route1 정확3 delete**, 보존 자원 readback. 변동이 있으면 기존 saved Plan을 임의로 재사용하지 않는다 |
| P8 실제 완료 뒤 | 재환 V9 | 기존 VPN_RUN `20261022T1500`, 자기 Relay/vpn-gw01 규칙·MSS h14/h15만 회수, 터널/자기 허용표 부재 및 원본 반출 |
| 마지막 검증·원본 반출 뒤, namespace/클러스터 삭제 전 | 하영 기승인 임시 권한 회수, 권욱 인수 | 아래 named get2 권한의 **Binding2→Role1** 및 기존 `gwonuk-p2-admin-temp`2를 각각 실제 UID/정의 대조 후 회수. 현재 권한 부족은 STOP/인계하며 이 문서가 새 cluster-admin 부여를 허용하지 않는다 |
| 기존 삭제 단계 | 하영 ROSA v8.1·승인 namespace3/클러스터/종속 자원 정리 | 당일10-inventory→정확 대상·기존 삭제GO 범위 확인. 코드 검토 수용·이 문서가 삭제 GO를 대신하지 않는다. 이미 없어진 클러스터의 조회 실패를 개별 자원 부재 readback으로 바꾸지 않는다 |
| 원본 반출 후,12:00 전 | 각 작업 소유자·권욱 취합 | 자기 P2 전용 후보/checkout/private input/추가 수집기·캐시만 정리. 공용 backend/state/lock, SSH key/known_hosts, 다른 작업파일·공유 증적 원본은 보존. 잔존 자원/비용 책임·실패·지연도 실제 결과로 보고 |
| 마지막 원본 소비 후,12:00 전 | 권욱 | GitHub 원본 읽기 PAT 관리ID21758739 **수동 폐기**. UI 만료10/27과 구분해 확인. 자격 문자열을 출력하거나 저장하지 않는다 |

## 본인·배포 SA named get2 권한 — 실제 생성 기록

근거: 10/26 00:31 실제 생성/UID readback 및 infra-rosa PR54 HEAD57bb1efb0600e4cb3d097149fdda4218d62cea25. 현재 관리자 전체 권한은 이미 회수됐고 이 3개는 한정 조회2를 추가한 객체다. expiry annotation은 자동 TTL이 아니다.

| 회수 순서 | Kind / name | 생성 UID |
|---|---|---|
| 1 | ClusterRoleBinding `fds-p2-delivery-target-reader` (배포 SA) | `5f705687-d9b9-4ed9-96a7-cf60f00635ee` |
| 1 | ClusterRoleBinding `fds-p2-delivery-target-reader-gwonuk` (본인) | `0ea8edc8-4516-4c70-88e4-1904f2f0269c` |
| 2 | ClusterRole `fds-p2-delivery-target-reader` | `440f91a9-c687-4867-ba9f-101a450d8b2a` |

삭제 전 현재 UID/정의·그 Role을 참조하는 다른 binding 유무를 확인한다. 자기 생성분과 다르면 멈추고 기존 상태를 기록한다. Forbidden·timeout·클러스터 소멸을 NotFound로 바꾸지 않는다. 본 문서에는 새 실행 명령·권한 확대를 추가하지 않고 기존 검토·승인된 회수 경로를 연결했다.

## 원본 보존과 남은 시간 위험

- A1/A2 claim/journal·수동중단 marker, A3 finish/정상완료 원본·B1 실패 원본은 비공개 공유 보관본과 SHA 대조 후 작업 사본만 정리한다. active0은 상태 원본 전체 삭제 허가가 아니다.
- 공유 폴더 ev252의 큰 원본5개 및 DR 사본은 보존한다. `FDS_P46_A3_*`·`FDS_P46_Validation_20261026_0410-v2.zip`와 기존 최종관리 ZIP도 보존한다.
- 하영 기존 카드의 **P8→V9/삭제/보고 약110분·ROSA 삭제 자격 잔여120분 요구**와 12시 초과 위험을 그대로 인계한다. 10-inventory 읽기 조기 준비와 실행 비중첩을 활용하고, 실제 진행에서12시 내 불가 위험이 보이면 즉시 상태·잔존자원·필요 복구를 보고한다. 자동 연장·무리한 동시 삭제로 해결하지 않는다.
- 버전 복구는 사용자 결정에 따라 미검증·미결로 보존한다. 이 미결 때문에 같은 digest 재배포·새 버전 제작을 추가하지 않는다. 원 AC·독립 인수·#46/G5/Project Close는 별도 판정이다.

## 선후관계 보충 — 기존 원본에 근거한 검토 반영

1. **반출과 경로 회수:** 각 단계 원본은 그 단계의 관리 경로가 살아 있을 때 먼저 반출/해시 확인한다. 기존 Codex 관리 경로는 PC→ansible01→Runner의 on-prem 관리 SSH이며, 실제 A3에서 사용한 ROSA API는 승인된 public API다. P2 Harbor 반환 경로/VPN을 다른 관리 경로와 동일시하지 않는다. 현장 실행자는 inventory 때 자신의 실제 접근/반출 경로가 회수 대상에 의존하는지 확인하고, 의존하면 먼저 반출·별도 관리 경로 인수 후 해당 경로를 회수한다. 모든 단계가 경로 단절과 무관하다고 단정하지 않는다.
2. **RBAC 회수의 주체:** 회수 대상은 gwonuk·배포 SA 권한이며 삭제 실행자는 하영이다. 하영의 실제 삭제/마지막 조회 권한은 당일 inventory에서 기존 승인 범위대로 확인한다. 대상 gwonuk 임시 권한을 먼저 지운 뒤 같은 gwonuk 권한으로 클러스터 삭제를 계속하는 구성은 아니다. 권한 공백이 확인되면 STOP/인계하며 이 문서에서 새 cluster-admin이나 fallback을 부여하지 않는다.
3. **PAT의 종료 순서:** 이 별도 source PAT는 #46 마지막 원본 인증 이후 로컬참조 종료됐고 버전복구도 미결로 보류됐다. 새 원본 소비가 없으면 ROSA/VPN 삭제 종료를 기다리지 않고 12시 전에 수동 폐기할 수 있다. 일반 PR/메타데이터 기록에 사용하는 기존 GitHub 연결과 이 별도 source PAT를 혼동하지 않는다. 어떤 후속이 이 PAT를 실제로 필요로 하면 폐기 전에 명시적으로 인수하고, 12시를 자동 연장하지 않는다.
4. **회수 후 실패:** Secret/Robot/경로 회수 뒤 원복·삭제가 실패하면 원본·현재 잔존 상태를 보존해 STOP/담당자 인수로 처리한다. 이미 회수한 자격을 자동 재발급하거나 scope 밖 재개로 되돌리지 않는다. 조치 권한/범위가 새로 필요하면 실제 차이와 복구안을 갖춰 판단한다.

Claude Code Opus5.5/high(실제 모델 동일)·Grok4.7/high(실제 grok-4.7-build)의 명세 검토 응답을 반영했다. 실제 effort 별도 metadata는 미제공. 운영 raw/자격은 외부에 제공하지 않았다. 외부 의견은 실제 네트워크/권한/회수 성공이나 사람 독립 인수가 아니다.
