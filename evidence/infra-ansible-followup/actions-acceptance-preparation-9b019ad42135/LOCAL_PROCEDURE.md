# 로컬 실행 절차 기록

재현 기준 source64파일은 TESTED_SOURCE_FILES.json에 기록됐다. 원격 tree와 Git blob을 대조한 뒤 새 scratch checkout에만 썼다.
기존 실행기의2.16.19 venv를 사용했으며 이것은 fresh offline 설치 또는 실제 Runner 실행의 재검증이 아니다.

실제 사용 경로:

- base: `/workspace/scratch/d7770f5e34f6/acceptance-preparation-validation/source`
- python: `/workspace/scratch/d7770f5e34f6/ansible-ci-linux-1/runtime/venv-2.16.19/bin/python`
- CLI: 같은 bin의 `ansible-playbook`
- 결과: `/workspace/scratch/d7770f5e34f6/acceptance-preparation-validation/{normal-216,negative-216,negative-unit}`

단계:

1.64개 파일 bytes/mode와 `git write-tree`의 `a63c5392d5930f29c77772b6a608f3a1c060a96b` 일치.
2. 두 patch에 `git apply --check`; 활성화 patch 적용 후 템플릿과 새 파일 bytes 일치.
3. 기존 `tests/test-ssh-key-guards.py`를 `--source <base>/playbooks/harden_svc_ansible_key.yml`,
   `--output <normal>/summary.json --export-dir <normal>/fixtures --expect-engine 2.16.19 --ansible-playbook <CLI>`로 실행.
4. count patch 적용, `git diff --numstat`가 대상1파일의1줄 추가/1줄 제거인지 확인.
5. 같은 harness로 negative 결과 생성. 실제 CLI 종료2, harness 종료1과 정확한 FAIL5·ERROR0 확인.
6. 결함 checkout에서 같은 venv Python의 `-B -m unittest discover -s tests -p 'test_*.py'` 실행: 57 OK/rc0.
7. patch 역적용 후 원본 bytes 확인. 활성화 patch도 역적용; tracked diff 및 untracked 파일 없음.

실제 CLI 명령은 localhost fixture를 생성하는 harness에 한정했다. 원본 운영 hardening playbook을 ansible-playbook으로 실행하지 않았다.
테스트 환경에서 ANSIBLE_/PYTHON/GIT_ 환경변수를 제거했고 원본 쉘 HOME을 덮어쓰지 않았다.

생성 전제조건 확인은 별도 모의 검사다. 기존 `tests/run-ssh-guard-matrix.py` 모듈을 읽고 argv에 임시 output을 지정한 뒤
`subprocess.run`의 첫 호출을 사용자 정의 예외로 가로챘다. subprocess는 실행하지 않는다.
새 count source에서는6개 variant가 생성되고 첫 CLI 경계에 도달했다.
기존 OR→AND source에서는 `ValueError: Source changed: mutation requires explicit OR`로 그 전에 중단했다.
각 변형 후 원본 bytes를 복구했다. 이 과정의 결과는 RESULTS.json에 있으며 실제 양 엔진 matrix 실행이라고 표시하지 않는다.

이 절차는 원 수행 기록이다. 다른 호스트에서 그대로 붙여넣는 명령 묶음이 아니다.
실제 서버 실행은 검토된 활성화/세션 절차를 따르고 증적을 기존 로그인 홈의 신규 경로에 수집한다.
