# Robot23 전환·임시4쌍 정리 보존 증적 — 2026-10-18

CODEX_ASSISTED. P1-HBR-01 / [baseline #13](https://github.com/321Team/fds-project-baseline/issues/13). 이 collection은 **실행 당시 소스44개와 실제 공개 기록117개, 총161개 원본 바이트의 보존·추적** 목적이다. 새로운 실행 코드 채택·설치·Runtime 승인·HBR AC 인수가 아니다. 소진된 invocation/scope로 재실행하지 않는다.

## 구성·읽는 순서

1. [context.json](context.json): 책임·시각·실제 candidate/cleanup/STOP 식별과 단계 구분.
2. [SOURCE_TARGET_MAP.json](SOURCE_TARGET_MAP.json): 모든161개 원본의 workspace 출처·새 경로·전체SHA·길이. 원 파일 내용 변경0.
3. `inactive-source/`: 실행 당시 소스의 비활성 사본44개. Python41개는 **내용 bytes를 유지한 `.py.txt`** 이름이다. 공개 CA도 저장소의 `*.pem` 제외 규칙을 우회하지 않도록 같은 bytes의 `.pem.txt` 사본으로 보관한다. 개인키는 포함하지 않는다. 원래 파일명과의 대응은 위 map에 있다. 원 manifest 안의 경로는 역사 데이터이며 수정하지 않았다. 따라서 원 manifest를 새 폴더에서 그대로 실행 검증 입력으로 쓰지 않는다.
4. `originals/`: 공급 readback·실제31전환 원장68개·최초 finish STOP 분석·별도 cleanup 공급/관측/retire/retain·실제 rc·콘솔 종료 확인 등117개. 모의시험·AI 기술검토 자료와 실제 원출력은 각 원문 상태를 유지한다.
5. [CURRENT_DECISION.json](CURRENT_DECISION.json): 10/19 최신 Push/ID3·.102 보존 방향. 과거 관측을 덮지 않는 현재 주석이다.
6. [VALIDATION_SCOPE.json](VALIDATION_SCOPE.json)과 [SHA256SUMS](SHA256SUMS): 현재 편입 바이트 검사 범위.

## 실제 결과와 실패 이력

- 10/18 20:06:42~45 공개31파일×5호스트 공급 readback. `candidate-manifest.json` SHA256 `4b337f9e69c2f01262cc5cd593cb2f6f3df75214143a5d8c1f640439cd3cdfe5`와31파일 전체를 연결했다.
- 20:38:54~20:42:15 invocation `27bef91a07a64a0f92c779fe47bcf66c`의 실제31전환은 CONSUMERS_VERIFIED. Worker3 인증·시험Pod5·Secret3/worker01파일 전환 결과다. 기존 운영 Pod 재배포 결과로 확대하지 않는다.
- 20:43:43 원 finish는 RELAY_BUDGET_OR_INPUT STOP. 입력37122B가32768B 한도를 넘었다. 당시 시간초과로 바꾸거나 성공을 소급해 쓰지 않는다. 최초 attempt031/STOP/claim·원 기한을 유지했다.
- 22:18:24~28 새 cleanup `667a9adb4c9f449890b316eaab94f620`으로 CP/Worker3의 정확 임시 credential/owner4쌍(8파일)을 정리했다. 실제 rc0와 원출력·transport 기록을 연결한다. 수집 파일 존재만으로 원 실행 성공을 판정하지 않는다.
- source2 Worker 발급 원본2개는 별도 보호 보존이다. 이 collection에 본문·그 본문의 공개 digest·Secret/dockerconfig/backup·키·암호를 넣지 않았다. 공개 metadata/경로가 있다는 사실을 원본 본문 포함으로 해석하지 않는다.

연결된 [전환](https://github.com/321Team/fds-project-baseline/issues/13#issuecomment-6249538316)·[정리](https://github.com/321Team/fds-project-baseline/issues/13#issuecomment-6250402176)·[최신 보존 결정](https://github.com/321Team/fds-project-baseline/issues/13#issuecomment-6256908369)을 구분한다.

## 형상·승인 경계

PR66의 사람 승인 HEAD4232b94/merge3822b38b는 당시 준비 코드 범위다. 실제 로컬 후보4b337과 동일한 것으로 표시하지 않는다. “1파일3줄”은 직전 로컬 후보476d386f→4b337의 reboot_contract.py +3/-0이며 나머지29항목 동일을 뜻한다. PR66 대비 전체 차이나 이후 부모 라벨 공급기 변경의 크기가 아니다. 실제 후보30+manifest1, 부모 비교 renderer·기대값 입력, 만료 후 정리 wrapper를 각각 보존한다. 관련 바이트는 이 collection의 source map으로 재현할 수 있다.

이 소스를 모델/기존 실행 경로/workflow에 편입하지 않는다. portable CI adapter·새 Runtime 제품화도 하지 않는다. 향후 능동 실행 코드로 채택하려면 그때 실제 diff·기존 코드 리뷰/실행 권한을 적용하며 이 증적 PR 병합을 실행 허용으로 사용하지 않는다.

## 현재 방향·남은 인수

사용자는 Phase2 Push 가능성 때문에 Push 관련 계정·자료 보존과 `.102` 현재 유지를 결정했다. 만료 계정 갱신/신규발급·권한 확대·영구 source 승인·새 무기한 위험수용은 포함하지 않는다. Phase2 실제 소비 경로·권한·유효기간 확정 전에 재검토하며 이를 Phase1 새 구현 Gate로 추가하지 않는다. Worker source2는 Push 자료와 별도이며 10/19 08:00 Owner 재검토 이후 실제 처분은 미확인이다.

HBR AC04 IPv6/INPUT 경계·기존 한계 수용, AC05/06 공유 인수와 정확 계정/원본 처분 판단은 기존 Lead 권한으로 남는다. 과거 H4 단회 자동복구/H7 단일 proxy 저장·Scan·CICD PR240 rollback 결과는 재사용하며 이 편입으로 재시험하지 않는다.

## 로컬 확인과 저장소 CI

원본과 대상161개 byte/SHA 일치를 확인했다. root `.gitattributes`의 `* -text` 규칙을 유지하며 자체 SHA256SUMS를 root REGISTRY_SHA256SUMS에 연결한다. 새 archive를 만들거나 원본을 재압축하지 않았다.

```text
sha256sum --check SHA256SUMS
python3 -m unittest discover -s tests -q
python3 tools/check-evidence-layout.py --base origin/main
```

첫 명령은 이 collection, 나머지는 저장소 루트에서 실행한다. CI/독립 검토·병합은 실제 수행 단계로 따로 기록하며 현재 후보는 미제출이다. 해시/형식 검사는 Runtime 진위·전체 AC·위험수용을 자동 증명하지 않는다.
