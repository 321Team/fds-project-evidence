# SEC isolated Probe 재시험 — 2026-10-08 22:51 KST

CODEX_ASSISTED. 실행자 GWONUK, 사전 Runtime 승인 이하영(hayeounglee). **격리 exec Probe T0~T3 관측·UID 정리·봉인 완료**, script_rc=0 / driver_rc=0. 실제 APP HTTP probe 또는 AC 전체 인수는 이 증적의 판정 범위가 아니다.

## 승인·시각·출처

- [독립 GO](https://github.com/321Team/fds-project-baseline/issues/19#issuecomment-6061273634) 및 [시간 정정 GO](https://github.com/321Team/fds-project-baseline/issues/19#issuecomment-6061331520). 정정 게시22:49:34 → window_start22:51, precheck상한22:55/run상한23:02/종료23:30. 늦은 승인 시각을 소급하지 않았다.
- session `probe-20261008t2245`는 식별자이며 실제 시작은22:51이다. 사용자가 이 채팅에서 비중첩·콘솔 및 복구 인수 가능(22:29), 단톡 공지 완료·비중첩 유지(22:48)를 직접 확인했다. 사람 확인 기록이며 전역 분산 lock이나 독립 서명은 아니다.
- source [infra-kubernetes#76](https://github.com/321Team/infra-kubernetes/pull/76) merge `781fd53d73a06def899524537b92868ef1bbd3bc`, BUNDLE SHA256 `67d109a7883d00e429f389622b72dfc80ad944263b29830d8331d68c8666ba65`. 실행 소스 원본은 `executed-bundle/`에 포함했다.
- root `/root/sec01-probe-20261008t2245/bundle` 배치 후 source bytes 검증, root:root 0700 디렉터리/0600 파일 확인. 정상 관리 경로 PC→ansible01/server01_ansible→control01/svc_ansible→기존 sudo -n을 사용했다. 권한/키/계정은 추가하지 않았다. foreground SSH를 유지하며 driver 종료를 기다렸고 nohup/별도 daemon/outer timeout은 사용하지 않았다. 사용자는 복구 콘솔 인수를 대기했다.

| 단계 | 실제 KST | 결과 |
|---|---|---|
| root staging | 22:51:21 확인 | bundle bytes VERIFIED, root ownership/mode 확인 |
| precheck | 22:51:35.694~22:51:36.298 | script0/driver0, seal VERIFIED |
| run | 22:52:12.104~22:53:06.369 | script0/driver0, seal VERIFIED |
| collect/회수 | run 종료 후, PC 수신22:54경 | 원본20개 해시 대조 완료 |

승인 최신 원문·작성자·게시/수정시각을 mode 실행 전 재조회했다. permit의 body 해시는 **정정 GO 원문 UTF-8 바이트**이며 원 GO는 정정 본문에 연결된다. `operator-records/go-*.json`에 두 원문을 보존했다. 같은 session/source/boot_id이며 run은 precheck 종료36초 뒤 시작했다. 각 mode 1회, 영속 claim 보존, 자동 재시도 없음.

## 실제 관측

고정 범위: k8s-control01에서 `fds-app` / k8s-worker01에 시험 Pod·Service 각1개. imagePullPolicy Never, digest `a7093136d12640da00570c18ed278eacbb8e9ba3637c7d509571346eac45cc33`, interpreter `/usr/local/bin/python3.12`를 그대로 사용했다. DB/Edge 후속 변경 전의 baseline을 재사용하지 않고 새 precheck/run에서 수집했다.

| 단계 | 원본 결과 |
|---|---|
| T0 | Ready=True, Endpoint ready=true, restart0 |
| T1 readiness 실패 | Ready=False, Endpoint ready=false, restart 변화 없음 |
| T2 readiness 복원 | Ready=True, Endpoint ready=true, restart 변화 없음 |
| T3 liveness 실패·회복 | restart0→1, container ID 변경, 이후 Ready/Endpoint true |
| SA token | projected source0, automountServiceAccountToken=false |
| 정리 | 생성한 Pod·Service 각각 UID precondition DELETE rc0, 이후 둘 다 NotFound |
| 사후 | 6/6 nodes Ready, 운영 Pod/EndpointSlice baseline diff 각각0 |

run archive의 `50-cleanup.txt`·`poll-T*.txt`·`T*-inject.rc`·`nodes-*.txt`·`diff-*.txt`로 대조 가능하다. `99-summary-provisional.txt`의 PROVISIONAL 문구는 원본 그대로 두었다. 최종 종료/봉인 판정은 archive 밖 `*.completion.txt`, `*.sealcheck.txt`, driver `result.json`으로 연결한다.

## 원본·무결성·한계

- `server-originals/`: reviewed driver collect가 허용목록으로 복사한 20파일+SHA256SUMS. 전송용 tar는 로컬에서 안전한 일반 파일만 추출했으며 **내부 원 archive는 재압축/수정하지 않았다**.
- precheck archive SHA256 `12bbe547b2b14eb48bb454bfab4331e4dfb4331244b18d3d584b9f8f149cb336`; run archive SHA256 `9ea9a3c2e61a7c4fc963e6cb359e00d1fa1749a36858cfbb92f83844a6116716`. sidecar/driver/수신 bytes 모두 일치.
- 내부 manifest 19/19 및75/75, manifest 자체를 포함한 archive 파일20개/76개 일치. allowlist 외 추가 파일·링크·경로탈출 없이 확인했다. 목록/크기/해시는 저장소 ARCHIVE_CONTENTS에 등록했다.
- private-key/GitHub token/DB credential URI/JWT 형태의 내용 패턴을 archive 내부 파일에서 검사해 검출0. 이것만으로 모든 형태의 비밀정보 부재를 보장하지 않으며 독립 리뷰 대상이다. kubeconfig·키·Secret 값·전체 환경은 수집하지 않았다.
- 로컬 전송 도구 최초 호출은 `operator.py` 이름이 표준 라이브러리와 충돌해 **SSH 전 import 단계에서 실패**했다. `python -I`로 실행 경로 격리 후 정상 전달했으며 서버 실행 코드 변경은 없었다.
- precheck 원본 확인 때 실제 이름이 `99-summary-provisional.txt`인데 `99-summary.txt`를 추가 조회해 cat rc1이 났다. 함께 읽은 stdout/stderr와 이후 archive 내부 검증으로 실제 내용을 확인했다. 이것은 운영자 파일 조회 실패이며 **precheck script/driver rc0과 혼합하지 않는다**. 해당 조회 stdout/stderr를 보존했다.

이전 실패 증적[#158](https://github.com/321Team/fds-project-evidence/pull/158)은 수정하지 않는다. 시험 객체는 삭제됐지만 원본·root bundle·세션/claim은 추적성·재사용 방지를 위해 보존한다. 본 회차 이후 Backup·etcd·키·운영 앱 HTTP Probe·추가 장애 주입은 실행하지 않았다. Runtime 창을 반환하며 독립 증적 리뷰·AC 판정은 대기한다.
