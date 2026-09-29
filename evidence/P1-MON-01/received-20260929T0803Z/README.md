# P1-MON-01 — 승인 관리 경로 Grafana port-forward 확인 (2026-09-29 17:02~17:24 KST)

[#17](https://github.com/321Team/fds-project-baseline/issues/17)에는 이 확인과 관련된 줄이 둘 있다.
- **AC 5번째 항목:** "승인 관리 단말의 Port-forward는 성공하고 비승인 외부 접근은 실패한다."
- **핵심 요구사항 섹션 1:** "Grafana 관리 접근은 승인 관리 단말의 `kubectl port-forward`만 허용한다."

두 줄이 말하는 승인 관리 경로에서 port-forward가 되는지 확인했다. 정본 v3.1.20의 기준은 다음과 같다.
- **700행:** 승인된 `ansible01(.10)` 또는 `cicd-runner01(.20)`에서 API LB `.109:6443`을 경유한 `kubectl port-forward`로만 관리 접근한다.
- **40·1108행(OID-01):** Approved Admin → API LB는 `ansible01 10.250.10.10/32 + svc_ansible`이다.
- **1053행:** IF-07의 관리 Source/identity는 `.10/32 + svc_ansible`이다.

**`svc_ansible`은 ansible01의 계정이 아니다.** ansible01에서 K8s 노드로 SSH 접속할 때 쓰는 노드 쪽 관리 계정이다.
- infra-ansible `ansible.cfg`에 `remote_user = svc_ansible`로 설정돼 있다.
- 접속 키는 ansible01 `server01_ansible` 계정의 `~/.ssh/p1_ansible_ed25519`다.
- [#9](https://github.com/321Team/fds-project-baseline/issues/9)(P1-LB-01)는 같은 경로로 API LB 접근을 검증했다. ansible01 → control01의 `svc_ansible` → `sudo kubectl --kubeconfig=/etc/kubernetes/admin.conf --server=https://10.1.93.109:6443`이고, 인증 계정은 `kubernetes-admin`이었다. 방식은 infra-lb `tools/stage-b/collect_api_precheck.py`와 같다.

**운영 변경:** 없음.
- port-forward는 `timeout 12`로 12초 뒤 자동 종료됐다(`pf_exit=124`).
- sudo가 출력한 "감사 플러그인 초기화 오류"는 없는 사용자로 실행하려 할 때 sudo가 내는 메시지다. 아무것도 실행되지 않았다.

## 수신·대조

| 폴더 | 서버 원본 (생성 시각 KST, 실행 계정) | archive | 대조 |
|---|---|---|---|
| `cicd-runner01/` | `~/p1-mon-pf-20260929/pf.txt` (17:02:06, `server01_cicd-runner`) | `mon-pf-runner.tar.xz` 292 B, SHA-256 `d26fa975…4b4535c4` | 서버 `sha256sum`과 일치, `pf.txt`는 archive 내부와 바이트 동일 |
| `ansible01/` | `~/p1-mon-pf-20260929/svc.txt` (17:08:41, `server01_ansible`에서 `sudo -u svc_ansible` 시도) | `mon-pf-svc.tar.xz` 332 B, SHA-256 `bb81d58e…633a9fea` | 같음 |
| `ansible01/` | `~/p1-mon-pf-20260929/oid01.txt` (17:24:05, `server01_ansible` → SSH `svc_ansible@k8s-control01`) | `mon-pf-oid01.tar.xz` 404 B, SHA-256 `26fde210…754ce1a4` | 같음 |

- archive는 base64로 채팅에 붙여 받아 디코드했다.
- `mon-pf-svc.tar.xz`의 첫 base64는 마지막 줄이 잘려 있었다(422자). 그래서 디코드가 실패했다. 같은 파일을 다시 출력받아 대조했고, 실패본은 편입하지 않았다.

## 결과

| 경로 | 결과 | 원본 |
|---|---|---|
| ansible01 로그인 계정 `server01_ansible` 자체 | `kubectl=없음`, `server=없음` | `../received-20260929T0656Z/ansible01/pf.txt` |
| cicd-runner01 로그인 계정 `server01_cicd-runner` 자체 | `kubectl=없음`, `server=없음` | `cicd-runner01/pf.txt` |
| ansible01의 `svc_ansible` | 계정 없음(`id svc_ansible` → "이 사용자는 없습니다"). 위 설명대로 노드 쪽 계정이라 정상이다 | `ansible01/svc.txt` |
| **OID-01 경로:** ansible01 `server01_ansible` → SSH(`p1_ansible_ed25519`) `svc_ansible@k8s-control01` → `sudo -n kubectl --kubeconfig=/etc/kubernetes/admin.conf --context=kubernetes-admin@kubernetes --server=https://10.1.93.109:6443 --tls-server-name=10.1.93.109` | `whoami=kubernetes-admin`<br>`port-forward svc/grafana 13000:3000` → `Forwarding from 127.0.0.1:13000 -> 3000`<br>`/api/health` **200**, 비인증 `/api/search` **401**<br>`pf_exit=124`(12초 뒤 자동 종료), `ssh_rc=0` | `ansible01/oid01.txt` |

## 판정 영향

- **AC 5번째 항목** "승인 관리 단말의 Port-forward는 성공하고 비승인 외부 접근은 실패한다"
  - 승인 관리 경로(OID-01: ansible01 출발, `svc_ansible`, API LB `.109:6443` 명시)에서 port-forward 성공, `/api/health` 200, 비인증 401을 관측했다.
  - 비승인 외부 경로 차단은 9/26 [`received-20260926T0445Z/run2-20260926T0425Z`](../received-20260926T0445Z/run2-20260926T0425Z/)에서 관측했다. Ingress 0건, Worker IP:3000 직접 접근 3/3 실패다.
  - 두 조건이 모두 관측됐으므로 AC 판정 근거가 된다.
- **핵심 요구사항** "Grafana 관리 접근은 승인 관리 단말의 `kubectl port-forward`**만** 허용한다"
  - 체크하지 않은 상태를 유지한다.
  - 같은 날 control01 로컬 계정(`server02`, sudo `admin.conf`)으로도 port-forward가 됐다(`../received-20260929T0656Z/control01/collect.txt`).
  - 이 경로를 승인 관리 경로의 일부로 볼지, 막아야 할 비승인 경로로 볼지는 판정하지 않았다.

**정정:** 이전 HEAD `555eacb`의 README는 ansible01에 `svc_ansible`이 없다는 점을 "OID-01 미구성"으로 해석했다. 그 해석은 틀렸고 이 버전에서 바로잡았다.

## 한계

- kubectl과 port-forward listener, `curl`은 SSH 원격 쪽인 control01에서 실행됐다. 세션은 ansible01에서 승인 identity로 시작됐고, API 경로는 `.109:6443`으로 명시했다. ansible01 화면으로 Grafana UI를 여는 SSH 터널은 시험하지 않았다.
- 사용한 인증 계정은 `kubernetes-admin`(admin.conf)이다. port-forward 전용 최소 권한 여부는 판정하지 않았다.
- 각 서버에서 로그인 계정과 `svc_ansible`만 조회했다. 그 밖의 계정은 조회하지 않았다.

AI 사용: CLAUDE_ASSISTED (명령 준비·수신 대조·정본 대조·문서화, 서버 명령 실행은 담당자 본인)
