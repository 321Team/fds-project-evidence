# 배치·실행 연결 — 제안이며 미실행

CODEX_ASSISTED. README의 사용자 결정·정확 입력 검토와 직전 조건 충족 후에만 사용한다. 아래 미생성 값은 임의로 채우지 않는다.

## 고정 공급물

- controller source: `147f760298dd4a683ea58f2a887483769352b97d`
- archive: `deploy-controller-147f760.tar`, 13 regular members, SHA256 `92b5a57bf9f0030db1c7b0e74276cc645e6041f6eec18257285ee8d6a4d02f0f`
- bundle: `native-source-147f760.json`, 정확 SHA는 `DEPLOY_CONTROLLER_PACKAGE.json`의 `remote_bundle_sha256`
- ansible01/server01_ansible 새 root: `/home/server01_ansible/FDS_CICD_DeployController.37a528cd-184a-4e0f-8f17-62416ca2e4e4`
- Runner/server01_cicd-runner 새 record: `/home/server01_cicd-runner/FDS_CICD_DeployInputs/deploy-37a528cd-184a-4e0f-8f17-62416ca2e4e4.json`
- approval/record는 아직 미생성이다. 사용자 결정 후 exact JSON·SHA를 추가 검토하고 이 문서의 입력표를 별도 결정 기록에 완성한다.

부모의 소유/비쓰기·symlink 부재를 확인하고 `umask 077`, 새 root0700, 파일0600/owner1000/nlink1/regular를 요구한다. 기존 root/record가 있으면 덮어쓰지 않는다. archive를 먼저 hash 대조하고 경로 탈출/링크 없는13member만 `tar --no-same-owner --no-same-permissions --keep-old-files`로 풀어 각각 SHA/소유/권한을 읽는다. 서버 공급과 기존 loader 기본모드의 임시 폴더 생성은 Runtime 쓰기로 기록한다.

## Workflow

`.github/workflows/app-deploy.yml`, `ref=main`, 위 `record_name`, 독립 검토된 `record_sha256`, `execute=false`로1회. Attempt1/source147f760/원본의 `SUPPLIED_BYTES_MATCH`, token false, Deploy미실행 확인 후 같은입력 `execute=true` 새Run1회.

실제 Job 시작은 제안23:15~23:25 KST, 정리00:15까지다. Workflow 대기열 진입을 실제 시작으로 표시하지 않는다. 마감 초과면 token broker 미연결·해당Run 취소. 응답 불명 시 재전송하지 않고 Run 목록·입력·dispatch.json을 대조한다.

## broker 연결

실제 true Run의 `dispatch.json.binding`에서 execution·record hash·plan hash·SA UID를 대조하고 해당Run socket owner1000/mode0600을 확인한다. 실제 binding 객체를 canonical JSON+LF로 만들고 SHA를 기록해 ansible 새 root의 `binding-<actualRun>.json`0600으로만 배치한다. 실제 RunID를 미리 만들지 않는다.

controller root 아래 `deploy-controller-147f760`에서 기존 `transfer_deploy_credential.main()`을 호출한다. 필수 인자는 `--bundle <절대 native-source 경로> --bundle-sha256 <manifest 값> --source-sha 147f760298dd4a683ea58f2a887483769352b97d --binding <실제 binding 절대경로> --binding-sha256 <실제 hash>`다. 기본 모드의 `LOCAL_INPUTS_VALIDATED`를 먼저 확인한다. 이 기본모드는 공급 임시 폴더를 만들지만 Token·Deploy는 하지 않는다.

execute 추가 인자(제안 창 채택 시):

```text
--execute
--authorization-expires 2026-10-13T15:15:00+00:00
--cp1-key /home/server01_ansible/.ssh/id_ed25519
--runner-key /home/server01_ansible/.ssh/p1_ansible_ed25519
```

`10/14 00:15 KST = 10/13 15:15 UTC`를 파서로 사전 대조한다. 기존 strict-host-key·CA 검증·계정은 유지한다. 실행기는1회만 호출하며 private protocol/token은 출력·파일에 남기지 않고 sanitized 최종 receipt만 받는다. broker 완료를 rollout 완료로 대신하지 않는다.

실제 원본·claim/checkpoint·Pod imageID와 Ready·socket/credential 정리는 README 기준으로 별도 수집한다. 기존 claim을 삭제하거나 구승인·구token을 재사용하지 않는다.
