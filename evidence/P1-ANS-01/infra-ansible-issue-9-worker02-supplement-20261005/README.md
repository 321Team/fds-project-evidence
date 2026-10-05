# Issue #9 worker02 — PTY 실패·백업 receipt 보완 수신

수신일 2026-10-05 03:04 KST, 책임 https://github.com/321Team/infra-ansible/issues/9. AI usage: CODEX_ASSISTED.

## 검증 결과

사용자 archive issue9-supplement.EXLlWsaa.tar.gz: 2256 bytes, SHA256 1ef7b3e8eb12a44f857906f9e45adb555fbf484f4aca4871d16579dab2dcf37e. 별도 수신 sidecar와 일치. 경로 검증 및 일반 파일만 허용하여 메모리로 읽었고 실행하지 않았다. 파일11개, 내부 SHA256SUMS의10항목 모두 일치. receipt-fetch.stderr.log는0bytes, 콘솔 RECEIPT_FETCH_RC=0.

original/은 압축본 내부 일반 파일의 바이트를 그대로 보존한다. 최초 편입에서는 압축본을 제외했으나, B-113-01 후속으로 2026-10-05 17:41 KST 사용자가 재첨부한 동일 압축 원본과 같은 이름의 .sha256 sidecar를 재압축 없이 추가했다. 원본 크기·SHA256 및 압축 내부 11개 파일과 기존 original/ Git blob의 일치를 확인했다. registry/ARCHIVE_CONTENTS.json에 내부 목록을 연결한다. 바깥 SHA256SUMS는 수신 후 작성한 편입 manifest다. 내부 original/SHA256SUMS는 사용자 수집 단계의 manifest이며 변경하지 않았다.

## 미수신 해소 및 범위

- failed-run/apply-1.log 원본 수신: 첫 Count 태스크에서 PTY allocation request failed, UNREACHABLE, recap ok0/changed0/unreachable1. 기존 콘솔과 일치.
- 최초 실패 apply-1.rc는 원래 실행 명령에서 저장하지 않았다. MISSING.txt가 미수집을 명시하며 rc4는 기존 사용자 콘솔 근거로만 유지한다. .rc를 임의 재생성하지 않고 실패 재현도 요구하지 않는다.
- failed-run engine/hosts/source/input sums/backup-preflight는 앞선 성공 수신본의 대응 파일과 바이트 동일. source5454b77d, core2.21.3, worker02 1대, 동일 키/백업임을 연결한다.
- backup-RECEIPT.txt 원본 수신: HOST worker02, SOURCE /home/svc_ansible/.ssh/authorized_keys, hash b7923e8c646b7a7dd2ccba1ac48ddf02d264780db9100317644dcf87216cc834, metadata1001:1001:600:unconfined_u:object_r:ssh_home_t:s0.
- receipt 생성 시각 2026-10-04T17:29:49Z = 2026-10-05 02:29:49 KST. 앞선 02:33은 콘솔 수신 시각이므로 모순이 아니다.
- 원격 receipt는 /var/lib/ansible-issue9-worker02.NXrcqAmF/RECEIPT.txt. authorized_keys 원문은 포함하지 않음.

## 이전 기록 연결

[적용·사후검증 수신](../infra-ansible-issue-9-worker02-canary-20261005/README.md)의 ‘실패 로그/receipt 원본 미수신’은 이 보완 전 이력이다. 이번 수신으로 두 항목이 해소됐으며 해당 원본을 성공 로그로 대체하지 않았다. 이전 수신 파일은 수정하지 않는다.

후보2.21.3 실제 무변경 apply2회·멱등성·fresh SSH·사후 기준 PASS를 유지. 실제 변경 분기·백업 복원 시험·운영 엔진 전환·전체 Issue9 AC는 미완료. 독립 증적 리뷰와 병합은 별도다. 이번 수신은 서버 재실행/복원 시험이 아니다.
