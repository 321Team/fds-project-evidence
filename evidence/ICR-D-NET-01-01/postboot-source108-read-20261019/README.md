# ICR 재부팅 후 source108→관리Harbor — 실패를 포함한 실제 관측

## 현재 판정

2026-10-19 12:38:49~54 KST, Worker03의 기존 승인 접근과 root 순수 조회로 정확 공개 CA를 결속한 후 제한 GET 명령을1회 실행했다. **curl rc28 / HTTP000 / TCP 연결0 / TLS handshake 미성립**이다. 결과를 수집한 outer rc0을 서비스 성공으로 표시하지 않는다. 타임아웃 원인/차단 지점은 미확인이다. 재시도·설정/서비스/계정·방화벽·신뢰 변경0이다.

## 실제 범위

- worker03의 host/machine/boot 전·직전·사후 일치, source10.1.93.108 ens160·route via10.1.93.58 확인. 실제 명령은 source를bind하고 목적지를10.250.10.30:443으로 지정했다. 연결 실패로 실제 local/remote socketIP가 비어 있어 요청값을 관측IP로 바꾸지 않았다.
- 기존 root0600 공개 CA1개2004B DER SHA `6a75baf4dbe03ef24cce944e616384d318f7ca919cd7bd914624b4cebac06b10` 일치. CA내용·개인키·인증본문은 수집하지 않았고 trust import나 `-k`가 없다. 상세 argv·정확 PEM전후SHA·rc·시각은 `originals/RAW/`와 `RESULT.md`에 있다.
- GW 현재 신원은 별도 **사용자12:30:58 콘솔 제출**이다. machine6720cbd7c6494f48b7991d25f2fc1a2a / boot7144f978-8f70-43ac-98bc-6502885ee47b이며 [기존09:41/43 정책 기록](https://github.com/321Team/fds-project-baseline/issues/14#issuecomment-6257388796)과 같은 boot다. 서버 원본 파일을 수신·해시 검증한 자료로 표시하지 않는다. GW 중앙 SSH 계정인증거부는 해소하지 않았고 이번 재접속0이다. GET 당시까지 GW boot 연속불변도 따로 실측하지 않았다.

## 검토 요청·경계

이하영: 원본/코드/요청·반환·CA 및 신원 결속, 실패를 성공으로 바꾸지 않았는지 독립 증적 검토를 요청한다. 이권욱(ICR Lead)은 이 자료와 기존 원AC18/19 행별 처분을 연결해 필요한 후속 진단·원조건의 현재 판정을 별도 결정한다. 본 PR 승인으로 실패한 정상흐름·재부팅 후 재시험·rollback 전체를 MET로 만들지 않는다. 새 Runtime·추가 GET·전노드 재부팅/재설치·보안해제를 승인하는 입력이 아니다.

수집회차는 원본 사본·중앙 설명·manifest만 편입한다. 실제 원본은 바이트 불변이며 COPY_MAP으로 추적한다. 정책 변경·새 AC/일정·인수/위험수용은 없다. CODEX_ASSISTED.
