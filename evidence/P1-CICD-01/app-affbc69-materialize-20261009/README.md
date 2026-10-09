# P1-CICD-01 — affbc69 공급 배치 및 승인 config 대조

2026-10-09 KST · CODEX_ASSISTED · 이권욱. 상태: **PRE_RUNTIME_MATERIALIZE=PASS / CONFIG_BYTE_MATCH=PASS / APP_RUNTIME=NOT_RUN**.

[APP 입력 확정](https://github.com/321Team/infra-cicd/issues/11#issuecomment-6074515472) → [CICD73](https://github.com/321Team/infra-cicd/pull/73) config 독립 승인·병합 후, 사용자의 후속 구축 착수 요청에 따라 정상 계정의 새 공급 경로를 준비했다. 코드 리뷰를 Runtime GO로 확대하지 않는다. 별도 Test/Build/Scan dispatch는 하지 않았다.

## 대상·버전

- host/account: cicd-runner01 / server01_cicd-runner / UID1000. sudo 미사용.
- CICD 실행 도구 main `c9eff5fb2e50a690818a3e67347ab4a1bfc88f51`, 승인 HEAD `b27210ee90521216ecd6eecae68737407e3aec86`. 전달한 도구·입력·config41파일 bytes가 두 Commit에서 동일함을 대조했고 `source-files.json`에 SHA256 보존.
- APP Source `affbc69beef9967f7977d09a6fec14f7fb6c0e94`, supply tool `8eac4c982076e3c219840a13686b15c46879981f`. APP29의 주석 병합 SHA로 공급 Source를 교체하지 않았다.
- 원본 artifact11585741989, 109786915bytes, ZIP SHA256 `2f13771909415439bc5a4c83036284e665b47d023b6447b37e3e18c24ea2e3fd`, manifest `6ab02000437a7b5f7d3c99e5202d40b663056a998018a1894360c58de68b73d4`. 기존 증적183 연결을 유지하며 새 ZIP은 만들지 않았다.

## 실제 실행·판정

- 14:48:19 metadata 사전 조회: 계정/hostname 확인, /home 및 홈/공급부모 경로의 링크·소유·권한 대조. 홈·부모 UID1000/0700, 새 대상 부재, 여유56439181312bytes, filesystem 쓰기 가능. CICD 대기/실행0, 기존 Runner2 online/busy=false; Ansible Runner0. 이는 순간 관측이며 전체 호스트 동시 작업 배제의 증명은 아니다. 사용자 단독 창은13:20~17:00이고 Harbor는 타 세션 범위다.
- 별도 새 staging `/home/server01_cicd-runner/app-affbc69-prepare.0IlSd9td`에 원 ZIP과 reviewed 도구/입력을 전달했다. 서버에서 원ZIP hash·41파일 hash 및 전용 사용자 lock을 확인 후 materializer1회 실행. 명령과 UTC 시각은 `RESULT.json` 원문에 있으며 KST14:50:54~14:50:55, rc0.
- 새 공급 경로 `/home/server01_cicd-runner/FDS_CICD_Runtime/FDS_CICD_ApkoSupply.affbc69beef9.6ab02000437a` UID1000/0700. 내부 manifest125파일 hash 대조.
- 생성 config bytes = CICD73 승인 config = 병합 main config. SHA256 `72eb52594048aa713ade12621f4545def0395f3f1603adec7bab3385b24f13e3`.
- 기존 adc90410 공급 폴더 dev/inode/mtime/ctime 불변을 확인했다. 이는 디렉터리 metadata 대조이며 기존 공급의 모든 하위 파일 bytes를 재검증한 것은 아니다. 기존 폴더 삭제·덮어쓰기를 수행하지 않았다.

## 보존·경계·실패 시 조치

원 ZIP과 이미지/wheel은 이 PR에 넣지 않는다. 이권욱 PC의 기존 비공개 원ZIP을 유지하고, 새 staging에도0600 사본이 있다. 정상 계정 홈0700 안에만 보존한다. 팀 장기보관 수신자·인수 기록은 별도 미확정이며 서버 사본 생성으로 장기 인수를 완료 처리하지 않는다. 후속 실행 입력인 새 공급과 staging은 자동 삭제하지 않았다.

materializer가 실패하면 출력·rc·남은 경로를 보존하고 기존 경로 삭제로 재시도하지 않는다. 이번은 rc0와 config 일치까지 확인했다. 배포·Podman load/build·앱 테스트·DB 갱신·스캔·Harbor Push·K8S 변경·Runner dispatch는 모두 NOT_RUN. 결과를 이미지 Build/Scan PASS나 전체 AC 인수로 사용하지 않는다. `prepare-only.py`와 orchestrator는 수행 절차 추적용으로 보존하며 이 증적폴더에서 재실행할 안내가 아니다.

다음은 개별 Test→Build→Scan 회차 GO, fresh main/config/Runner/비중첩 확인 후 실행이다. 제안은15:30 이전 시작,16:20 미완료 시 취소 판단,17:00 내 결과·잔존 자원 확인이다. workflow180분 timeout은17:00 종료 보장이 아니다. Push/Deploy는 여전히 별도다.

보존 형식: Windows에서 생성한 일부 수신 메타데이터·절차 파일은 CRLF 원본을 그대로 보존했다. 이 파일들의 git diff whitespace 경고는 CRLF 때문이며 manifest는 실제 보존 bytes 기준이다. 서버 원본 로그·생성 config는 수신 bytes를 유지한다.
