# P1-MON-01 — 승인 관리 단말 port-forward 경로 확인 (2026-09-29 17:02~17:08 KST)

[#17](https://github.com/321Team/fds-project-baseline/issues/17)에는 이 확인과 관련된 줄이 둘 있다.
- 핵심 요구사항: "Grafana 관리 접근은 승인 관리 단말의 `kubectl port-forward`만 허용한다."
- AC: "승인 관리 단말의 Port-forward는 성공하고 비승인 외부 접근은 실패한다."

두 줄이 말하는 승인 관리 단말에서 port-forward가 가능한지 확인했다. 정본 v3.1.20의 기준은 다음과 같다.
- **700행:** 승인된 `ansible01(.10)` 또는 `cicd-runner01(.20)`에서 API LB `.109:6443`을 경유한 `kubectl port-forward`로만 관리 접근한다.
- **40·1108행(OID-01):** 승인 관리자는 `ansible01 10.250.10.10/32 + svc_ansible`이다(APPROVED_INPUT 2026-09-16, Runtime 미인수).

앞서 [`received-20260929T0656Z/ansible01/pf.txt`](../received-20260929T0656Z/ansible01/pf.txt)(16:16:23)에서 ansible01 로그인 계정 `server01_ansible`에는 kubectl과 kubeconfig가 없음을 확인했다. 이번에는 나머지 두 경로를 확인했다.

**운영 변경:** 없음.
- 두 번 모두 조회만 했다. kubeconfig가 없어서 port-forward는 실행되지 않았다.
- sudo가 출력한 "감사 플러그인 초기화 오류"는 없는 사용자로 실행하려 할 때 sudo가 내는 메시지다. 아무것도 실행되지 않았다.

## 수신·대조

| 폴더 | 서버 원본 (생성 시각 KST, 실행 계정) | archive | 대조 |
|---|---|---|---|
| `cicd-runner01/` | `~/p1-mon-pf-20260929/pf.txt` (17:02:06, `server01_cicd-runner`) | `mon-pf-runner.tar.xz` 292 B, SHA-256 `d26fa975…4b4535c4` | 서버 `sha256sum`과 일치, `pf.txt`는 archive 내부와 바이트 동일 |
| `ansible01/` | `~/p1-mon-pf-20260929/svc.txt` (17:08:41, `server01_ansible`에서 `sudo -u svc_ansible` 시도) | `mon-pf-svc.tar.xz` 332 B, SHA-256 `bb81d58e…633a9fea` | 서버 `sha256sum`과 일치, `svc.txt`는 archive 내부와 바이트 동일 |

- archive는 base64로 채팅에 붙여 받아 디코드했다.
- `mon-pf-svc.tar.xz`의 첫 base64는 마지막 줄이 잘려 있었다(422자). 그래서 디코드가 실패했다. 같은 파일을 다시 출력받아 대조했고, 실패본은 편입하지 않았다.

## 결과

| 승인 경로 (정본 근거) | 결과 | 원본 |
|---|---|---|
| ansible01 `svc_ansible` (40·1108행) | 계정 없음: `id svc_ansible` → "이 사용자는 없습니다", `sudo -u svc_ansible` → "알 수 없는 사용자 svc_ansible" | `ansible01/svc.txt` |
| ansible01 로그인 계정 `server01_ansible` (700행 `.10`) | `kubectl=없음`, `server=없음` | `../received-20260929T0656Z/ansible01/pf.txt` |
| cicd-runner01 로그인 계정 `server01_cicd-runner` (700행 `.20`) | `kubectl=없음`, `server=없음` | `cicd-runner01/pf.txt` |

정본이 정한 승인 관리 경로 세 곳 모두 kubectl이나 kubeconfig가 없다. 그래서 port-forward를 시험할 수 없다.

Grafana port-forward가 실제로 확인된 경로는 control01(Control Plane, `admin.conf`)뿐이다.
- 9/26 `received-20260926T0445Z/run2-20260926T0425Z`
- 9/29 `received-20260929T0656Z/control01/collect.txt`

## 판정 영향

- **핵심 요구사항** "Grafana 관리 접근은 승인 관리 단말의 `kubectl port-forward`만 허용한다"는 체크하지 않은 상태를 유지한다.
- **이미 체크된 AC** "승인 관리 단말의 Port-forward는 성공…"의 근거는 control01 port-forward다. 정본 700행의 승인 단말 기준과 맞지 않는다. 이 AC의 처리는 #17에서 따로 기록한다.
- **다시 판정할 조건:** 승인 관리자 경로(OID-01: ansible01 `svc_ansible`, kubectl, `.109:6443` 경유 kubeconfig)를 실제로 구성한 뒤, 그 경로에서 port-forward가 성공하고 비인증 접근이 거부되는지 시험한다.

## 한계

- 각 서버에서 로그인 계정과 `svc_ansible`만 조회했다. 그 밖의 계정은 조회하지 않았다. root나 서비스 계정에 kubeconfig가 있는지도 확인하지 않았다.
- API LB `.109:6443`까지의 네트워크 도달성은 이번에 시험하지 않았다.

AI 사용: CLAUDE_ASSISTED (명령 준비·수신 대조·정본 대조·문서화, 서버 명령 실행은 담당자 본인)
