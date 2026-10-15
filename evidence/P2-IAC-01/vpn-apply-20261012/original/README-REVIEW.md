# #11 vpn(Relay) Apply·readback 원본 — 독립 readback 검토용 (하영 → 권욱, 2026-10-12)

- 결과 보고: infra-terraform#11 6120492825 / GO 6120046778 / 시작 기록 6120338125
- 실행: CloudShell ~/iac11-vpn-20261012-020352 (321team-hayeoung → FDS-IaC-Operator, 새 MFA 세션), 17:17:05–17:21:08 KST, Apply 17:17:50–17:18:15 RC0 8 added
- 승인 Plan vpn.tfplan 0bb10dc983b46b0145c94f8e26f553fe2487d175452d6f40a17e3d1116c01e23
- 전달: tar.gz(iac11-vpn-apply-20261012.tar.gz, 159c08af2376cb09551c347754d1ffa87640297bcb6fa256b72b2aa2875537df, 22,935 B) → 번호 base64 화면 출력 → PC 복원, 해시 일치
- CloudShell·PC 모두 evidence-apply/SHA256SUMS 73/73 OK. 실제 비밀값 패턴 검사(AKIA/ASIA 키, SecretAccessKey/SessionToken 값, aws_secret_access_key=, PRIVATE KEY) 0건
- 주요 파일: apply.stdout, output-relay.stdout(relay_handoff), output-session-doc.stdout, state-list.stdout, rb-*(EC2·볼륨·SG 규칙·EIP·RT·SSM 문서·문서 내용·Agent 폴링), pre-*(trust·access key·EIP quota·transport subnet·태그 EC2·SSM 문서 부재), libreswan-repomd.xml·libreswan-versions.json(17:17:14 repo 조회), before/after/network-keys, execution-summary.json
- iac11_vpn_apply.py(1d972411576f305d22cbc36fff25935c85b167bc4c586afa2293c534385f0347): CloudShell에 붙여 넣은 실행 스크립트 로컬 원본
- 첫 시도(17:14:57)는 WORKDIR 밖 실행으로 AWS 호출 전 STOP — 기록은 CloudShell ~/iac11-failed-start-20261012/ (이 묶음 미포함)
- 포함하지 않음: state 원문, credential, MFA 코드
