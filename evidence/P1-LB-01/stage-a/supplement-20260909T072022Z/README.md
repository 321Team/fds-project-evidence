# FUP-09 Permanent Supplement 수신 검토 v1.0

판정: **현재 시각 Permanent 출력 수신·무결성·6443 rich rule 정합성 PASS / 독립 검토·인수 조건 판단 대기**.

편입 상태: 사용자에게 이번 내부 IP·호스트·계정을 포함한 증적과 검토 결과를 비공개 `321Team/fds-project-evidence`에 Draft PR로 등록할 승인을 요청했고, 사용자가 “승인”으로 응답했다. 이에 따라 원격 등록을 진행한다. 실제 PR·Commit은 PR 본문과 후속 이슈 #4에 연결한다. 독립 검토·인수 조건 판단·최종 병합은 별도 대기다.

수집: 2026-09-09 07:20:22~23 UTC / 16:20:22~23 KST. 호스트 `k8s-api-lb01`, 계정 `server01_k8s-api-lb`. 제출 자료를 직접 대조했으며 검토자가 서버 명령을 재실행한 것은 아니다.

## 직접 검증

| 항목 | 결과 |
|---|---|
| 원본 tar.gz | 1,560 bytes · SHA-256 `ee5021db732caaa2892dd17ecdf6f08aff86eef5f1cd3b9776d433680b7409b9` · 제출 sidecar 일치 |
| 내부 원본 | 텍스트 7개 + 원래 SHA256SUMS, 원본 바이트 보존. 7/7 체크섬 일치 |
| 조회 | 5/5 명령·scope·UTC·종료코드 확인, 전부 EXIT_CODE=0 |
| 버전·활성 zone | firewalld 2.4.3 / public(default), ens160 |
| 6443/tcp 규칙 | Runtime, Permanent 전체 조회, Permanent rich-rule 조회가 각각 동일한 /32 accept 8개 |
| 기존 수신 Runtime 대조 | 동일한 8개 규칙, public 필드도 동일. 순서·앞 공백만 정규화 |
| 서비스·일반 포트 | 양쪽 public은 dhcpv6-client·ssh, ports 공란. 소켓 Listening 검사는 이번 범위 밖 |
| 인터페이스 차이 | Runtime=ens160, Permanent=공란. 전체 설정이 동일하다고 판정하지 않음 |

허용 source: CP `10.1.93.102/32`, `.103/32`, `.104/32`; Worker `.105/32`, `.107/32`, `.108/32`; Runner `10.250.10.20/32`; Monitor `10.250.10.30/32`. 이는 [기존 수신 Runtime](https://github.com/321Team/fds-project-evidence/blob/39ead0567327cf45ed9f8b81cecdf9848f542d5d/evidence/P1-LB-01/stage-a/received-20260907/10_firewalld.txt)과의 대조이며 새 허용 정책 승인이 아니다.

## 인터페이스 관찰 해석

Permanent의 interfaces 공란만으로 저장 실패라고 단정할 수 없다. [firewalld 공식 설명](https://firewalld.org/documentation/zone/connections-interfaces-and-sources.html)에 따르면 NetworkManager가 연결 프로필의 zone 또는 기본 zone에 인터페이스를 배정할 수 있다. 이번 묶음에는 해당 프로필이 없어 실제 원인이 그 방식이라고 확정하지 않는다. 재부팅 후 지속성도 시험하지 않았다. 현재 8개 규칙 수신·정합성 검토는 완료하며 이 관찰만으로 설정 변경이나 재부팅을 요구하지 않는다.

## 증적 보존과 판정 범위

- [원본 내부 Manifest](raw/SHA256SUMS)와 [검증 세부 기록](VERIFICATION.json)을 연결한다. source 디렉터리의 sidecar도 제출 바이트 그대로다.
- tar.gz 원본은 제출 보관본 `libfile_8ef49db06ac88191932240cd269412eb`, sidecar는 `libfile_76826d7e992081919a0e1bdb525aa64e`로 보존했다. Git에는 검토 가능한 원본 텍스트·Manifest·sidecar를 편입한다. 이 기록은 다른 팀원의 tar.gz 보관본 접근을 확인했다는 뜻은 아니다.
- 현재 조회는 과거 8/31~9/3 상태를 소급 증명하지 않는다. FUP-09 Permanent의 현재 시각 Supplement 수신 대기는 해소됐고, 이 자료로 기존 인수 조건을 해소할 수 있는지는 이하영의 실제 판단 대기다.
- LB-A-01 IP 중복검사는 과거 응답 0개 대화 이력만 확인됐으며 원본 바이트·고정 참조가 아직 미수신이다.
- 기존 Stage A 원본 21개·콘솔 보완 3건·조건부 인수·PASS 및 Bootstrap HOLD를 유지한다.

## 후속 검토

추적: [이슈 #4](https://github.com/321Team/fds-project-evidence/issues/4). 조건부 인수 정정 [PR #5](https://github.com/321Team/fds-project-evidence/pull/5)의 HEAD `0461d5c5736d5b24ccc8b282aefc7620701bdea7`를 기준으로 이 새 수신 회차만 분리한다. 기존 PR #5 검토 HEAD를 변경하지 않는다.

이재환: 새 원본 텍스트·체크섬·비교 결과·관찰 및 범위 제한의 독립 검토. 이하영: 새 시각 Supplement의 인수 조건 충족 범위 판단. 이권욱: 원본 연결 및 최종 편입 결정. 타인 명의의 확인·승인이나 조건 종결은 작성하지 않았다.
