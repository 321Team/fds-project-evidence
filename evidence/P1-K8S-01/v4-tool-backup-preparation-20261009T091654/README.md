# v4 도구 원본 사본·복귀 메타데이터 준비

CODEX_ASSISTED · 이권욱. 2026-10-09 수신 PC **09:16:54~09:16:57 KST**, 호스트 기록 **09:16:56~09:16:58 KST**. 시계 동기 정확도는 별도 미검증이다. 사용자 연장 창09:10~12:00에서 기존5대 고정45개 파일을 읽었다. [K8S78](https://github.com/321Team/infra-kubernetes/pull/78)의 준비 보완이며 실제 교체·복귀는 **NOT_RUN**이다.

## 결과와 한계

| 항목 | 관측/수행 결과 |
|---|---|
| 파일 hash | 45/45 이전 계획과 동일, 승인 기준28 MATCH / 17 DIFFERENT 유지 |
| 원본 내용 사본 | 변경 후보17개·168,782bytes, PC 수신 bytes17/17 hash 일치·구문 compile 성공, 실행 없음 |
| 파일·부모 metadata | 파일45개 + 부모20개 =65개. 전체 열람 가능한 xattr 목록은 모두 security.selinux만 존재 |
| 숫자 ACL | 파일 root0:0/0750 기본 ACL. 각 호스트 /opt·/opt/fds는0755, 패키지 root·code는0750, 모두 root0:0 기본 ACL |
| filesystem | 관측 부모 filesystem readonly=false, 가용 bytes/inode 기록. 실제 쓰기·복귀 가능성은 시험하지 않음 |
| SELinux |5대 enforcing. 파일 type worker01의9개 user_home_t, 나머지36개 usr_t 유지. 이번 회차는 정책 기본값을 다시 조회하지 않음 |
| 서버 변경 | 파일 저장·교체·relabel·서비스/정책 변경0. 동시 작성자/호출 배제 미확정 |

이 사본은 **PC 보관 원본 내용+복귀용 관측 metadata**다. 운영 서버의 실행 직전 백업, 복구 경로 가용성, metadata 적용·실제 복원 성공, 승인된 기대 SELinux 값은 아직 아니다. Windows 보관 파일의 권한/시간이 Linux 원본 속성을 재현한다는 뜻도 아니다. inode/dev/ctime은 관측 식별값이며 파일 복원으로 원래 값까지 복구할 수 있다고 주장하지 않는다. 구버전 bytes에는 알려진 도구 결함이 남으므로 원복 시 `RESTORED_WITH_KNOWN_TOOL_DEFECT` 및 사용 보류 판단이 필요하다.

## 보존 구조와 공개 범위

- 수신 원본 stdout 및17개 실제 코드 bytes는 실행자 PC의 비공개 `phase1-work-20261009/private/k8s-backup-20261009T091654/`에 보존한다. 원격 서버에는 백업 폴더나 임시 수집기를 만들지 않았다.
- 비공개 보관 archive: `k8s-tool-backup-20261009T091654.tar.gz`,162,981bytes, SHA256 `a86024b31d9433e1fdb63127f4a30e7360138d69cd682988b97409acd37a2dfa`. archive의 모든 member를 로컬 수신 파일과 byte 대조했다. archive를 Git에 올리지 않았고 다른 담당자 보관 인수는 미완료다.
- 이 Git 폴더의 `receipts/<host>/projection.json`은 **원 stdout이 아니라 files[].content_base64만 제외한 투영본**이다. metadata/xattr/ACL·파일 hash는 유지한다. `source_stdout_sha256`은 별도 비공개 원 stdout의 hash로, 투영본 파일의 hash가 아니다.
- collector.py·invocation.json·빈 stderr.txt는 수신 기록의 원본 사본이다. source/stdout hash10/10 검증 결과는 `local-verification.json`에 기록한다. 저장소만 가진 검토자는 비공개 stdout/17개 원본 내용을 독립 재검증할 수 없으며 필요 시 기존 비공개 전달 경로로 인수해야 한다. 서명·진위 인증·완전한 공개 원본 증적이라고 표시하지 않는다.
- `plan.json`은 K8S78 HEAD `74ae4a5f6c815a683c22161367b950205bba465b`의 계획 Git blob과 byte 일치한다. 이전 미수집/미백업 필드는 당시 계획 이력이며 수정하지 않는다.

## 오프라인 대조

`python3 analyze_k8s_backup.py .` 출력은 `analysis.json`과 일치한다. Git에 있는 projection·collector hash·plan·xattr bytes/size/hash·45개 이전 hash·17개 후보 집합을 대조하며 `private_receipt_check=NOT_INCLUDED`를 유지한다.

비공개 원본을 인수한 검토자는 `python3 analyze_k8s_backup.py . <private-receipt-root>`로 원 stdout SHA·투영 변환 일치·17개 사본 bytes/hash/구문을 추가 확인할 수 있다. 이 출력은 `local-verification.json`과 일치한다. 두 경로 모두 서버 명령·복원·운영 도구 실행을 하지 않는다. collector 재실행은 현재 시간/대상·권한과 새 필요성을 별도 확인해야 하며 기존 관측을 갱신하기 위해 무조건 반복하지 않는다.

## 수집 통제와 남은 실행 조건

기존 `fds-ansible01`→`svc_ansible`→`sudo -n /usr/bin/python3 -B -`, 엄격한 SSH 호스트키 검증으로5회 실행했다. rc0/stderr0, 고정 호스트/euid/09:10~12:00 gate,9개 파일/4개 부모만 허용했다. 모든 경로 요소를 O_NOFOLLOW로 열고 O_NOATIME로 읽었다. 파일당128KiB, xattr16개/각16KiB/총64KiB 상한과 inode/metadata/xattr 전후 대조를 사용했다. getfacl은 해당 열린 FD를 `/proc/self/fd/`로 조회하고3초 제한을 적용했다. 수집기는 사전 독립 리뷰 미실시인 **REVIEW=NOT PERFORMED (Pre-check)**이며, 기존 비교 대상 도구 승인과 구분한다.

파일별 읽기 안정과 부모 전후 대조는 확인했지만45개가 동일 시각의 원자적 snapshot인 것은 아니다. 기대 라벨 처리, 실제 도구 호출 주체·동시 사용 배제, fresh 관측·서버 백업/복귀 검증, 정확한 교체 부분집합·복구 인수·GO가 남는다. worker01의 보존5개를 relabel 범위에 자동 편입하지 않는다. control02, 운영 정책·AVC·PortMatrix·AC 인수는 범위 밖이다. 리뷰는 연장 작업창 이후 회수한다.
