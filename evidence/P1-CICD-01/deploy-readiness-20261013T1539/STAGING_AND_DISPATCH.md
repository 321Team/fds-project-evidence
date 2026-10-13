# 확정 입력의 배치·실행 명령 연결

기존 source2d8a14c 도구와 표준 파일 전달 명령만 사용한다. 새 배포 실행기를 만들지 않는다. 이 문서도16:15 이전 또는 독립 입력 검토·Harbor 비중첩 조건 확인 전에는 실행하지 않는다. 모든 경로는 이번 UUID에 한정한다. 기존 파일 존재·symlink·소유/권한 불일치면 덮어쓰지 않고 중단한다.

## 1. 보호 배치

- ansible01/server01_ansible의 새 경로: `/home/server01_ansible/FDS_CICD_DeployController.2fb09791-d0ca-443f-9c1b-77747c3f3a73`(0700). 기존 HOME/부모 소유·그룹/다른 사용자 쓰기 부재를 먼저 조회한다. `umask 077`, `mkdir -m 700`으로 새 디렉터리를 만들고 기존13-file archive를 전달한다. 이미 존재하면 재사용하지 않는다.
- `sha256sum`으로 archive SHA `67df6be5d7f935f2618e55365b7c3f0250bea99b771a579873e7961f9061f261`를 먼저 대조한다. archive의 검증된13개 regular member만 `tar --no-same-owner --no-same-permissions --keep-old-files -xf <이번 archive> -C <이번 root>`로 배치한다. 경로 탈출/링크 member는 없다. 추출 후13파일 SHA와 새 경로 권한/소유를 읽어 원 package와 대조한다. 원본 archive는 보존한다.
- Runner/server01_cicd-runner의 `FDS_CICD_DeployInputs`는 없을 때만0700으로 생성하고, 기존이면 owner1000/mode0700·symlink 부재를 확인한다. 승인 record를 `umask 077`와 noclobber(`set -C; cat > <이번 record>`)로 생성한다. 파일명 `deploy-2fb09791-d0ca-443f-9c1b-77747c3f3a73.json`, SHA `11c94e5c28e1b22bc8df2d8f686fb61ff2f0c04b7bb9dd810496c4b1f63f0e50`,0600/owner1000/nlink1/regular를 확인한다. 개인키·기존 kubeconfig는 전달하지 않는다.
- 기존 strict host-key SSH/원래 키 경로를 쓴다. 전달 실패·결과 불명확이면 같은 경로에 재전송하지 않고 수신 파일/크기/hash를 읽어 조정한다. 불명확한 수신물을 삭제해 재시작하지 않는다.

## 2. 기존 Workflow dispatch

현재 main이 `2d8a14c55ea4b61f53b7ac6d682cd5e97575dda7`인지 직전에 확인한다. 사용자 허용 시간창 안에서 다음 입력을 사용한다.

```text
workflow: .github/workflows/app-deploy.yml
ref: main
record_name: deploy-2fb09791-d0ca-443f-9c1b-77747c3f3a73.json
record_sha256: 11c94e5c28e1b22bc8df2d8f686fb61ff2f0c04b7bb9dd810496c4b1f63f0e50
execute: false
```

false 성공 Run/Attempt1/HEAD 및 해당 Runner receipt의 `SUPPLIED_BYTES_MATCH`/tokenfalse/Deploy미실행을 확인한 후에만 같은 입력·`execute=true`로 **별도 새 Run 1회** dispatch한다. dispatch HTTP 결과 불명확 시 자동 재전송하지 않는다. 새로운 Run 목록과 실제 dispatch.json을 대조한다.16:30 이후 새 dispatch하지 않는다.

## 3. broker 연결

true Run이 Runner에서 출력한 `FDS_CICD_Deploy.<임의값>/dispatch.json`을 읽는다. Run ID/Attempt1/Workflow SHA/plan/record/SA UID가 모두 맞고 해당 Run socket이 만들어졌음을 확인한다. `binding` 객체만 local UTF-8 JSON으로 저장해 SHA를 고정하고 ansible01의 이번 root 아래 **새** `binding-<실제RunID>.json`0600으로 전달한다. 다른 Run의 binding을 쓰지 않는다.

ansible01에서 이번 root의 `deploy-controller-2d8a14c`로 이동한 뒤 기존 broker를 사용한다. `BINDING`/`BINDING_SHA256`는 위 실제 생성값이며 실행 전에 별도로 대조한다. token/TokenReview protocol은 기록하지 않고 최종 sanitized broker receipt만 수집한다.

```sh
python3 -I -B -c 'import sys; sys.path.insert(0,"tools/delivery"); import transfer_deploy_credential as t; raise SystemExit(t.main())' \
  --bundle /home/server01_ansible/FDS_CICD_DeployController.2fb09791-d0ca-443f-9c1b-77747c3f3a73/deploy-controller-2d8a14c/native-source-2d8a14c.json \
  --bundle-sha256 8cfdcce5e4b5eb95001d27e35606e5121edf77d8c2c1f5f481016c79933baa5c \
  --source-sha 2d8a14c55ea4b61f53b7ac6d682cd5e97575dda7 \
  --binding "$BINDING" --binding-sha256 "$BINDING_SHA256" \
  --execute --authorization-expires 2026-10-13T08:00:00+00:00 \
  --cp1-key /home/server01_ansible/.ssh/id_ed25519 \
  --runner-key /home/server01_ansible/.ssh/p1_ansible_ed25519
```

먼저 위 명령에서 `--execute`, `--authorization-expires`, 두 key 인자를 제외한 기존 기본모드로 `HANDOFF=LOCAL_INPUTS_VALIDATED`/tokenfalse/Deploy미실행을 확인한다. 이 기본모드도 source 임시 폴더를 만들므로 순수 read로 표시하지 않는다. 이어 위 execute 명령1회만 실행한다. 별도 native token 진단 회차를 추가하지 않는다. bundle/binding 경로는 기존 loader가 요구하는 절대경로다.

## 4. 결과 수집·중단

broker 종료를 rollout 결과로 대신하지 않는다. 해당 Run/result.json과 지속 claim/journal 및 fresh Deployment/Pod digest·readiness·socket 정리를 확인한다. claim과 원본은 보존한다. token원문·Secret·환경 전체·개인키는 수집하지 않는다. 자동 발급 재시도/Run rerun/claim삭제는0회다. 실패 시 처음 확정한 두 이전 image 외 추가 변경은 하지 않는다. 전체 APP/HA/DB 인수는 별도다.
