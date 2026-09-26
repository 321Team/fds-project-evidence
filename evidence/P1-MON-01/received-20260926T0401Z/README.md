# P1-MON-01 — infra-monitoring#12 승인 리뷰 증적 요청 3건 대응 (2026-09-26)

[infra-monitoring#12 승인 리뷰(이권욱)](https://github.com/321Team/infra-monitoring/pull/12#pullrequestreview-5324080351)의 "증적 요청 — @supreme33-kr" 3건에 대한 원문이다. 수집은 MON Lead(이재환)가 콘솔에서 했고, 모든 명령은 읽기 전용이다(생성·변경 없음).

## 폴더와 출처 구분

| 폴더 | 내용 | 출처 구분 |
|---|---|---|
| `worker03-20260921/console-transcript.txt` | 9/21 15:04 KST worker03 PV 준비 실행 출력 | **콘솔 제출 자료.** 당시 Claude 채팅에 붙여넣은 원문(대화 기록 2026-09-21T06:04:15Z)을 그대로 옮겼다. 서버 파일·서버 Hash는 없다 |
| `worker03-20260926/pv-recheck.txt` | 9/26 13:01:59 KST worker03 PV 상태 재확인 | 서버 생성 파일. base64로 받아 서버 출력 SHA-256과 일치 확인(`server-SHA256SUMS.txt`) |
| `control01-20260926/` 4개 파일 | Grafana Deployment env·resources, Grafana Pod lastState, LimitRange YAML·관리 주체 | 서버 생성 파일. tar.gz(`dd208c44…b459b0`)를 base64로 받아 archive·개별 파일 SHA-256 모두 서버 출력과 일치 확인 |

- 각 `server-SHA256SUMS.txt`는 서버에서 출력한 `sha256sum` 결과를 옮겨 적은 것이다(수신 측 작성).
- control01 수집 폴더명은 `~/mon12-followup-20260926T035707`(서버 `date` 기준, 시간대 미표기)이다.

## 요청별 결과 (판정 아님)

### 1. PV 준비 실측 (9/21)
- 9/21 원문: `getenforce`=Enforcing, `df -h /home` 163G 가용(2%), `ls -la` owner nobody/472/nobody·mode `drwxr-x---`, `restorecon -Rv` relabel 4건 → `container_file_t`.
- 9/21에는 `semanage fcontext -l` 등록 조회를 하지 않았다. 9/26 재확인에서 `/home/fds-local-pv(/.*)?` → `container_file_t` 등록을 확인했다.
- 9/26 mode는 `drwxrws---`(2770)로 9/21의 750과 다르다. owner·라벨은 같다. `grafana.yaml`의 `fsGroup: 472` 등 Pod `fsGroup` 적용에 따른 변화로 추정하며 원인은 확인하지 않았다(NOT VERIFIED).
- 9/21 당시 `mkdir`·`chown`·`chmod`는 출력이 없는 명령이라 원문에 나타나지 않는다. 결과는 같은 원문의 `ls -la`로 보인다.

### 2. Grafana 현장 대조
- `grafana-deploy-env.txt`: image `10.1.93.54/fds/grafana:latest`, `GF_ANALYTICS_*` 3개 `false`, `GF_PLUGINS_PREINSTALL_DISABLED=true`, `GF_AUTH_ANONYMOUS_ENABLED=false`, `GF_USERS_ALLOW_SIGN_UP=false`, resources requests 200m/256Mi·limits 1/1Gi.
- infra-monitoring main(`72e952c`) `kubernetes/monitoring/grafana.yaml`의 이름·값과 같다(수신 측 대조).
- `GF_SECURITY_ADMIN_*`는 Secret 참조라 값이 빈 문자열로 출력된다. 비밀값은 포함되지 않는다.
- 9/22 OOMKilled 기록: 현재 Pod `grafana-6cd7cbccbc-78m22`는 `restarts=0`, `lastState={}`다. 당시 Pod는 교체돼 현장에 남은 기록이 없다(NOT VERIFIED).

### 3. LimitRange 관리 위치
- 현장 `monitoring-api-default-limits`: `default` 500m/512Mi, `defaultRequest` 200m/256Mi, **`max` 없음** → Grafana limit 1Gi를 제약하지 않는다.
- 생성 2026-09-22T00:17:38Z, 관리 주체 `kubectl-client-side-apply`.
- 소스: [infra-kubernetes PR#7](https://github.com/321Team/infra-kubernetes/pull/7) `manifests/05-limitrange.yaml`(커밋 `de40366`, 이하영, 2026-09-17)에 같은 spec이 있다. **PR#7은 main 미병합**이라 main 기준으로는 소스가 없다. PR#7 병합 시 소스가 생긴다.

AI 사용: CLAUDE_ASSISTED (명령 준비·수신 대조·문서화, 실행은 담당자 본인)
