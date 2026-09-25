# Ansible #9 호출 경로 수집 결과 검토 v1.0

검토일: 2026-09-24 KST. 대상: [infra-ansible #9](https://github.com/321Team/infra-ansible/issues/9).

**판정: 수신 무결성·수집기 식별 대조 완료 / 현장 메타데이터 부분 확보 / 운영 전환 PENDING.** 전체 수집 AC를 완료 처리하지 않는다. 이번 수신으로 같은 기본 수집을 반복할 필요는 없다.

## 1. 원본과 단계

| 항목 | 확인 결과 |
|---|---|
| 원본 | REPORT.json 177,653 bytes, SHA256SUMS 78 bytes |
| REPORT SHA-256 | `b6d2383e077261dee8b36a7a9b0f3cdd65b92eed88e1180b52c428a22369e69f` — 제출 SHA256SUMS와 일치 |
| 수집 시간 | 2026-09-24 06:14:55.370237–06:14:55.490125 KST |
| 서버·계정 | ansible01 / server01_ansible / UID1000 |
| 수집기 | version 1.0, SHA256 `ef85fdb6609bdc3e860d77ed311ba5fddce46b96cdbd0240d29ebfeef936f1ce` |
| 수집기 출처 | [PR48](https://github.com/321Team/infra-ansible/pull/48), source `03d8ca003f6945f2df92794326cb0855553911ad` |
| 배포 | v1.1 ZIP `d437cd0240a15612b0cf28f0b41740af4efb77307613e6007d837d80eb8cc537`; v1.0과 수집기 bytes 동일 |
| 보고서 상태 | `completed=true`, `COLLECTED_REVIEW_REQUIRED` |
| 확인 단계 | 제출된 실서버 순수 수집 결과의 기술 검토. 검토자가 서버에 접속해 재실행한 것은 아님 |
| 별도 미수행 | Ansible CLI/SSH 실행, 실제 apply·멱등성·rollback, 운영 엔진 전환 |

보고서의 `runtime=NOT_RUN`은 수집기 구현상 Ansible/운영 실행 미수행을 뜻한다. 이번 서버 수집 자체를 미실행으로 표시하지 않는다. 전체 수집기의 최종 프로세스 exit code·콘솔 원문은 미첨부지만, 보고서의 completed/status와 내부 3개 query rc는 확인했다. 보고된 수집기 SHA가 배포 bytes와 일치하며 실행 서버의 파일을 별도 재수집·재해시한 것은 아니다.

## 2. 확인된 운영 메타데이터

| 항목 | 수집 사실 | 판단 범위 |
|---|---|---|
| Ansible RPM | `ansible-core-1:2.16.19-2.el10.noarch`, Vendor CentOS | 설치 RPM 확인. 후보 2.21.3 전환 아님 |
| Python RPM | `python3-0:3.12.14-1.el10.x86_64`, Vendor CentOS | 9/8 기록의 3.12.13과 달라짐. 이 수집으로 변경 주체·시점은 알 수 없음 |
| 수집기 Python | `/usr/bin/python3.12`, 3.12.14 | 실제 수집기 실행 환경 |
| PATH 후보 | `/usr/bin/ansible`, `/usr/bin/ansible-playbook`, `/usr/bin/ansible-galaxy` | 실행 가능한 파일, shebang은 `/usr/bin/python3`; CLI 실행/alias·function 해석은 하지 않음 |
| Python 경로 | `/usr/bin/python3` → `/usr/bin/python3.12` | 링크 해석 관찰 |
| 저장소 checkout | `/home/server01_ansible/p1-ans-01`, HEAD `da7f2ccd52ee407e61376d11375a1361f076f112` | `git rev-parse` rc0. 전체 working tree clean·untracked 상태는 수집하지 않음 |
| 환경 변수 | 수집기 관찰 대상 11개 모두 미설정 | 해당 프로세스 환경만 확인. 다른 shell/cron/서비스 환경에는 확대하지 않음 |
| yum repo 정의 | 활성값 1: baseos, appstream, crb, extras-common, epel, gh-cli | 정의 파일 관찰. 해당 RPM을 실제 설치한 repo나 backport 지원 증거가 아님 |

## 3. checkout 차이와 재작업 판단

GitHub 원본의 운영 보고 HEAD `da7f2ccd…`와 현재 main `fa12a355…`를 비교했다. 두 tree는 각 217개 blob이며, 차이는 아래 **문서 2개**다.

- `docs/REVIEW_POLICY.md`
- `docs/ci/ACTIONS_ACCEPTANCE.md`

나머지 215개 blob/mode는 같다. 이는 GitHub 두 commit의 비교이며 서버의 전체 파일 검증이 아니다.

실제 보고서에서 수집한 `ansible.cfg`, DNS/MON/NTP/Gate0 wrapper 4개, `verify-ssh-main.py`의 **6개 SHA-256은 운영 보고 HEAD의 GitHub 원본과 모두 일치**한다. 이 6개 Git blob은 현재 main과도 같다. 출처 Git blob 해시를 먼저 검증한 뒤 SHA-256을 비교했다.

따라서 이번 HEAD 차이만으로 운영 코드가 낡았다고 판정하거나, git pull·재배포·46/46 구문 재실행을 요구하지 않는다. 다음 실제 실행에서는 지정 source SHA와 해당 실행 범위의 clean 상태를 기존 계약대로 확인한다.

관찰 파일 권한은 DNS 0700, MON 0644, NTP 0755, Gate0 0600, verify-ssh-main.py 0644다. Git 실행 비트와 모순되지 않으며, 비실행 파일은 `bash`/`python`으로 호출할 수 있다. 실제 invocation이 미확정이므로 편의상 chmod를 수행하거나 요구하지 않는다.

## 4. 수집 범위와 미확인

전체 336개 파일 항목 중 READ 309개, 링크 미수집 21개, 민감 경로 이름 제외 4개, 파일 부재 2개다. 읽은 본문 합계 240,988 bytes가 보고서 집계와 일치한다. 중복 `(path, category)`는 없고, 25개 coverage gap은 모두 해당 파일 항목과 연결된다.

기본 system cron·unit·drop-in·사용자 shell 파일의 **수집된 본문에서 직접 Ansible/Python 참조를 찾지 못했다**. 임의 이름의 wrapper를 통한 간접 실행, 다른 계정 crontab, 활성·일시 생성 unit 전체 부재를 뜻하지 않는다. 일반 서비스 링크 21개와 이름상 제외 4개는 수집기 제한이며 Ansible 장애 25건으로 집계하지 않는다.

`crontab -l`은 rc1, stdout0 bytes, stderr32 bytes다. stderr 원문을 보존하지 않아 ‘개인 crontab 없음’과 조회 오류를 구별할 수 없다. **이 한 항목은 미확인으로 유지한다.** 전량 수집 대신 해당 명령의 오류 원문만 보완하면 된다.

| 남은 항목 | 최소 후속 | 현재 AC 영향 |
|---|---|---|
| 수동 실제 경로·유효 config/collections | 기존 로그인 shell에서 alias/function 종류와 실행 경로, `ansible-playbook --version`, collection 목록 확인 | CLI 파일/RPM만으로 유효 실행 환경 전체를 확정하지 않음 |
| 개인 예약 작업 | 같은 계정의 `crontab -l` rc 및 오류 문구 보완 | rc1을 ‘작업 없음’으로 완료 처리하지 않음 |
| root/다른 계정·간접 예약/서비스 | 기존 담당자가 실제 사용 중인 관련 경로와 활성 상태 확인 | 권한 확대·sudo 추가 없이 기존 담당 범위로 확인 |
| Runner | infra-ansible 격리 Runner와 infra-cicd 영구 Runner 각각 실제 workflow/source/image/venv 명령 연결 | 현재 첨부는 ansible01 자료이므로 Runner 확인을 대신하지 않음 |
| RPM 실제 설치 공급원/backport | 설치 이력·공급자 근거 확인 | 활성 repo 정의만으로 설치 원인·지원 상태를 추정하지 않음 |

## 5. 다음 조치

1. 수집 결과와 이번 비교를 원본 그대로 증적 PR에 편입한다. 독립 검토·병합·#9 최종 인수는 별도다.
2. 아래 짧은 읽기 조회로 수동 경로와 개인 crontab만 보완한다. 기존 shell에서 직접 실행하며 수집기 전체 재실행은 불필요하다. 비밀 값이 포함될 수 있는 전체 env/history/config dump는 요청하지 않는다.
3. Runner·다른 계정 예약 경로·RPM 실제 공급원은 기존 담당 자료로 채운다. 미확인 항목이 남으면 첫 수집 AC는 미완료를 유지한다.
4. 확인된 호출 경로를 기준으로 고정 venv 절대 경로를 선택할 최소 wrapper 변경을 준비한다. 후보 경로와 운영 canary 대상은 아직 미확정이며 임의로 설치·전환하지 않는다.

실행 위치: ansible01 / server01_ansible, 기존 로그인 shell. 아래는 `--version` 및 설치 collection 목록 조회이며 playbook·SSH·설치·서비스 변경을 실행하지 않는다. 실패하면 rc·메시지를 보존하고 설정을 수정하지 않는다. 작업 디렉터리는 기존 repo로 한정한다.

```bash
(
  cd /home/server01_ansible/p1-ans-01 || exit 1
  printf 'ansible-playbook command kind: '
  type -t ansible-playbook || true
  printf 'ansible-playbook PATH file: '
  type -P ansible-playbook || true
  /usr/bin/ansible-playbook --version
  printf 'ansible_version_rc=%s\n' "$?"
  /usr/bin/ansible-galaxy collection list
  printf 'collection_list_rc=%s\n' "$?"
  /usr/bin/crontab -l >/dev/null
  printf 'crontab_rc=%s\n' "$?"
)
```

`type -t`가 alias/function이면 정의를 그대로 공유하지 말고 선택되는 실행 파일·wrapper 경로만 확인한다. `crontab -l`의 stdout은 숨기고 stderr와 rc만 받으므로 기존 작업 명령·인수를 공유하지 않는다. rc0이면 crontab 조회 성공이며 비어 있음을 증명하지 않는다. rc1이면 stderr의 실제 원인을 확인한다. 위 블록의 각 rc와 출력 원문을 전달한다.

일반 Ansible CI #5는 여전히 별도 인수 단계다. 이번 결과로 canary apply·운영 엔진 전환을 시작하거나 기존 AC·담당·일정을 변경하지 않는다. PR48 소스는 `REVIEW=NOT PERFORMED (Pre-check)`이며, 실제 운영 변경 코드와 증적 저장소의 독립 검토 기준을 유지한다.
