# P1-K8S-01 T19 노드별 복구 시험 — 부분 실행·중단 기록 (2026-10-02)

[fds-project-baseline#10](https://github.com/321Team/fds-project-baseline/issues/10) AC "…복구…" 항목의 시험(T19, `k8s-worker01` 대상)을 2026-10-02에 시도했으나, **사전에 합의한 중지 조건**(앱 Pod 재시작)에 걸려 Review Owner(권욱) 결정으로 **중단**하고 설계 상태로 원복한 기록이다.

> **2026-10-02 정정:** 중단 당시 Pod 재시작의 원인을 firewalld 복원으로 보았으나, 이후 worker01 journal에서 **18:29:56 시험 외 재부팅**(`systemd-logind: The system will reboot now`)이 확인됐다. 재시작은 그 재부팅의 결과이며 firewalld 복원 때문이 아니다. 아래 "확인한 사실 5"와 "한계 7"을 이에 맞춰 고쳤다. 중단 결정이 이 오인에 근거했는지의 판단과 재시험 여부는 Review Owner가 한다.

**이 문서는 T19 완료나 AC 충족을 주장하지 않는다.** T19의 결과는 `ABORTED_BY_PREDEFINED_STOP_CONDITION`이며, 노드 보호 해제(HEP 삭제·node Felix failsafe 복원)와 `rollback-node` 단계는 실행하지 않았다. 재시험은 별도 승인된 창에서 한다.

## 자료 구분

세 압축 파일은 **서버에서 만든 원본 묶음**이다(`CONSOLE_SUBMITTED / RECONSTRUCTED_COPY`가 아니다). 서버에서 `sha256sum`으로 계산해 화면에 보고한 값과 이 폴더의 파일 SHA-256이 일치한다. 압축은 풀지 않은 채 보관하고 `.sha256` sidecar와 `registry/ARCHIVE_CONTENTS.json`으로 고정한다.

| 파일 | 만든 곳 | SHA-256 (서버 보고값 = 이 폴더) | 내용 |
|---|---|---|---|
| `t19-control01-final.tgz` | control01 `/root/t19-20261002` | `533bf1a7954f75e83a443823a0ec731280353e7dc0299b2dcf124da6ea09463b` | 시험 전 기준선·행렬, 9/22 번들·state 백업(`*.bak`), 도구 반영 기록, 원복 전·후 기준선, 보호 receipt(NOT_REVIEWED), 하위 증적 tgz 2개 |
| `t19-worker01-final.tgz` | worker01 `/var/log/fds-evidence/P1-K8S-01/t19-20261002` | `6e997547c7c7c4eb885b6cae5bd04442f2501d4c18083016a70b74482b418868` | 방화벽 복원 전·후, nft/iptables 스냅샷, tcpdump(Negative 시도 3종) |
| `t19-ansible01-final.tgz` | ansible01 홈 | `2942c536685781845f6515ef053e33cb4010b0e50b6d494ca9d9a35ec89cea44` | 접속 시도 기록(성공·실패 모두), 수집 기록 |

전달 경로: 서버 → ansible `fetch`/`tar` → ansible01 `~/t19-final/` → 공유 폴더 → 증적 저장소. 전송 후 이 PC에서 SHA-256을 다시 계산해 서버 보고값과 대조했다. 수집 시각 2026-10-02T19:37:51+09:00(ansible01 `collect-final`). 암호·토큰 값은 묶음에 없음(키워드 검색으로 확인).

## 시험 대상과 경위

| 항목 | 값 |
|---|---|
| 대상 | `k8s-worker01` (10.1.93.105) |
| 번들·state | `/root/generated-gate2-attempt01`, `/var/lib/fds/P1-K8S-01/gate2-state.json` (attempt `gate2-attempt01`, cluster_uid `e1669cff-1435-423f-a6c4-28bc44f488de`, config_sha256 `b42e7e80590ac6fb03e1934499c3f0ceeeab33557ecdf3033c3e206936c8ec43`) |
| 도구 | infra-kubernetes `ops/p1-k8s-01-v4/code/cluster-change.py` (#52 병합본, sha `e955a6f9…2df162`, 반영 14:58:36 — `tool-deploy.txt`) |
| 실행자 | 이하영(K8S/SEC Lead), Review Owner 권욱 입회·결정 |
| 시험 전 기준선 | 14:49~15:36 (`baseline-before.txt`, `matrix-*-before.txt`) |
| 방화벽 복원(firewalld enable) | 18:30~18:32 (`01-before-restore.txt`, `02-after-restore.txt`) |
| 복원 후 관측 | 18:34~19:07 (ssh, 행렬, Negative 시도) |
| 중단 결정 | 19:20 (`03-pre-decision.txt`) |
| 원복(firewalld disable) | 19:33:24 (`04-after-abort-off.txt`) |
| 원복 후 기준선 | 19:35 (`baseline-after-abort.txt`, `matrix-cp-after-abort.txt`) |

## 확인한 사실

1. **원복 확인**: firewalld `UnitFileState=disabled ActiveState=inactive`(19:33:24). HEP `fds-k8s-k8s-worker01`(UID `aa7effb8-d409-4da5-ab84-6a066ac5036b`), GNP `fds-k8s-host-k8s-worker01`, Felix `node.k8s-worker01`이 시험 전과 동일(`baseline-before.txt` ↔ `baseline-after-abort.txt` 대조, 콘솔 보고 `HEP_GNP_FELIX_IDENTICAL`). 노드 6/6 Ready, API `/readyz` 통과(콘솔 보고).
2. **Positive**: 방화벽 복원 후 control01 → worker01 `10250` OK (`matrix-cp-restore.txt`, 18:50:24). 시험 전·원복 후와 같은 결과다(`matrix-cp-before.txt`, `matrix-cp-after-abort.txt`: 9100 FAIL, 10250 OK).
3. **Negative**: 승인되지 않은 같은 서브넷 비노드 호스트 `edge01`(10.1.93.50) → worker01 `10250`이 FAIL. worker01 `ens160` 캡처에 SYN 5개, SYN-ACK 0, RST 0(`matrix-edge-restore.txt`, `neg-edge-10250.txt`). 한계 2번 참고.
4. **방화벽 복원 후 SSH 제어 유지**: ansible01 → worker01 ansible ping 성공(`ssh-after-restore.txt`).
5. **중단 사유와 정정**: 중단 당시에는 firewalld 복원 직후 worker01 앱 Pod가 재시작된 것(`fds-engine` 2→3, `transaction-api` 3→4, Pod IP 변경)을 방화벽 복원의 영향으로 보았고, 사전 합의한 중지 조건(앱 Pod 재시작)에 걸려 권욱이 조건 완화를 거부했다(Option C). 이후 확인 결과: worker01 노드의 **모든 컨테이너**(앱 2개, calico-node, kube-proxy, node-exporter)가 같은 시각 18:30:07(UTC 09:30:07)에 `Unknown`/종료코드 255로 끝났고, containerd·kubelet이 18:30:07에 새 프로세스로 시작했다. journal에 18:29:56 `The system will reboot now`가 있고 부팅은 18:30:01(`uptime -s`, `last -x`의 `shutdown 18:29 - 18:30`)이다. 재부팅은 SSH 세션(`server05`)에서 일어났다. firewalld 상태 확인은 18:30:43, 복원은 그 이후이며, 복원 이후 재시작 수는 3·4로 64분간 변동이 없었다. 따라서 앱 Pod 재시작은 **시험 직전 재부팅의 결과이며 firewalld 복원의 결과로 관측되지 않았다**. (근거: 사용자가 worker01·control01 콘솔 출력을 화면 캡처·붙여넣기로 제출한 관측이며 이 폴더에 서버 원본 파일은 없다 — `CONSOLE_SUBMITTED`.)
6. **MON 영향**: 방화벽 복원 구간에 worker01 `9100`을 허용하는 firewalld 규칙이 없어 모니터링 수집이 끊겼다(재환 확인 요청: [#22 코멘트](https://github.com/321Team/fds-project-baseline/issues/22#issuecomment-5950509653)).

## 한계

1. **부분 실행**: T19 전체(복구 후 HEP 삭제, node Felix failsafe 복원, 사후 검증, receipt `PROTECTION_RESTORED_REVIEWED`)는 수행하지 않았다. receipt `k8s-worker01-protection-receipt.json`은 `NOT_REVIEWED`이며 승인되지 않았다.
2. **Negative 차단 지점 미특정**: tcpdump는 netfilter 이전 지점(`ens160`)에서 패킷을 본다. SYN-ACK 부재는 확인했으나 차단이 firewalld인지 Calico HEP/GNP인지 가리지 못한다(`ENFORCEMENT_POINT=NOT_ATTRIBUTED`). 이 시점에는 Calico 보호와 firewalld가 함께 켜져 있었다.
3. **실패한 Negative 시도 포함**: 앞선 두 시도는 유효한 시험이 아니어서 `edge01`을 택한 이유로 남긴다. ansible01 출발(`neg-10250.txt`, `matrix-ans-*`)은 ansible01에 상위에서 TCP 22만 승인돼 worker01에 10250 SYN이 도달하지 않았고, worker02 출발(`neg-w02-10250.txt`, 캡처 0건)은 출발 노드 HEP egress가 막았다. 두 경우 모두 worker01 방화벽의 차단을 증명하지 않는다.
4. **시험 전 행렬 일부 오류**: `matrix-before.txt`의 probe-w01/w02는 Pod가 완료(Failed) 상태여서 `exec` 오류다. probe-w03만 유효(9100·10250 OK)하다.
5. **재구성·덮어쓰기**: 방화벽 복원 후 첫 Negative 실행 파일 일부는 재실행으로 덮어써졌다. 이 묶음의 파일이 마지막 실행이다.
6. **무해한 경고**: `BACKUP_SHA256SUMS` 자기 항목 불일치와 `iptables-save` 경고는 수집 방식에 따른 것으로 증적 값에 영향이 없다.
7. **Pod 재시작 원인**: 위 확인한 사실 5와 같이 시험 외 재부팅으로 확인됐다. 재부팅 시점이 시험 직전(18:29:56)이었다는 점은 시험 절차의 사전 상태 확인이 부족했음을 뜻하며, 재시험 절차에 "시험 창 중 재부팅 금지·재부팅 후 기준선 재수집"을 넣을 것을 제안한다. firewalld 복원이 앱 Pod에 영향을 주는지는 이번 시험으로는 판단할 수 없고 재시험에서 확인한다.
8. **시험 전 부분 묶음 미편입**: 시험 전 시점의 부분 묶음(`t19-pre-20261002.tar.gz`, SHA-256 `7371d211e9977eb76f6e474cabd4fa39dbc7ae7ebce4a538355e679d1f1ea222`)은 `t19-control01-final.tgz`에 포함된 파일의 부분집합이어서 따로 편입하지 않았다.
9. 이 증적은 **수집 시각 한 시점**의 관측이다.

## 판정 경계

- `T19_ATTEMPT_20261002 = ABORTED_BY_PREDEFINED_STOP_CONDITION`
- `POD_RESTART_CAUSE = NODE_REBOOT_18:29:56 (시험 외, firewalld 무관으로 관측)` — 콘솔 제출 자료 기준.
- 원복 상태: 설계 상태(Calico 보호 + firewalld 비활성)로 확인됨, 검토자 확인 필요.
- 이 문서와 증적은 AC "복구" 충족을 주장하지 않는다. 충족 판정과 재시험 일정은 Review Owner·Lead가 한다.

## 검토 상태

AI 세션(Claude Code)의 편입 작성이며, `governance/EVIDENCE_POLICY.md`의 독립 검토는 아직 없다. 증적 PR 검토자 지정은 PR에서 확인한다.
