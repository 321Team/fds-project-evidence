# 재부팅 후 신규 SSH 사용자 콘솔 제출 기록

출처: 사용자 대화 제출. 이 파일은 2026-09-08 검토 시 정리한 전사본이며 서버가 생성한 원본 로그가 아니다. 실제 명령 실행 시각과 종료 코드가 별도 제출되지 않았으므로 새로 채우지 않았다. 이 기록의 SHA-256은 전사 파일의 바이트만 식별하며 실행 사실을 독립 서명하지 않는다.

두 명령은 ansible01에서 제출됐고 출력 호스트명이 각각 일치했다. 각 after TAR의 원래 REMOTE_PENDING 보고서는 수정하지 않는다.

## k8s-control01

```bash
ssh -T \
  -i "$HOME/.ssh/p1_ansible_ed25519" \
  -o BatchMode=yes -o PreferredAuthentications=publickey \
  -o PasswordAuthentication=no -o KbdInteractiveAuthentication=no \
  -o StrictHostKeyChecking=yes \
  -o "UserKnownHostsFile=$HOME/.ssh/known_hosts" \
  -o IdentitiesOnly=yes -o IdentityAgent=none \
  -o ControlMaster=no -o ControlPersist=no -o ControlPath=none \
  -o ConnectTimeout=10 \
  svc_ansible@10.1.93.102 hostnamectl --static
```

출력:

```text
k8s-control01
```

## k8s-control02

```bash
ssh -T \
  -i "$HOME/.ssh/p1_ansible_ed25519" \
  -o BatchMode=yes -o PreferredAuthentications=publickey \
  -o PasswordAuthentication=no -o KbdInteractiveAuthentication=no \
  -o StrictHostKeyChecking=yes \
  -o "UserKnownHostsFile=$HOME/.ssh/known_hosts" \
  -o IdentitiesOnly=yes -o IdentityAgent=none \
  -o ControlMaster=no -o ControlPersist=no -o ControlPath=none \
  -o ConnectTimeout=10 \
  svc_ansible@10.1.93.103 hostnamectl --static
```

출력:

```text
k8s-control02
```
