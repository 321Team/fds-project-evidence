# 실제 consumer 파일 검증 — 2026-10-09 08:44 KST

CODEX_ASSISTED · 이권욱. **BYTE COMPATIBILITY PASS / 전체 config·현장 Runtime 미실행 / 독립 REVIEW PENDING**.

현재 Windows에는 consumer가 필요한 POSIX 모듈/실행 환경이 없어 모의 대체하지 않고 기존 ansible01의 정상 `server01_ansible` 계정·Python3.12.14에서 수행했다. 새 권한·sudo 없이 전용0700 임시 폴더에서만 파일을 다뤘다. 이는 실제 CICD Runner의 경로·계정·SELinux·Podman·app test 검증이 아니다.

## 고정 입력과 실제 호출

- consumer source: infra-cicd main `04e49811e46ffcd3f35183c2cfb9493901f84dc5`의 offline_supply_v3/offline_supply 및 필요 trivy helper3개, 원 Git blob 그대로.
- APP source: `affbc69beef9967f7977d09a6fec14f7fb6c0e94`의 requirements/locks8개·apko4개·Dockerfile2개, 원 Git blob 그대로. APP Python 코드는 반출/실행하지 않았다.
- 입력20파일(consumer5+APP14+검증기1) SHA를 실행 전 대조했다. 실행 입력은 `executed-inputs/`에 바이트 보존하고 INPUT_HASHES/result를 연결한다. 전달 tar SHA는 invocation에 있으며 tar를 재압축하여 원본이라고 제출하지 않는다.
- 공급은 상위 README의 원 artifact11585741989 / ZIP SHA2f13771909415439bc5a4c83036284e665b47d023b6447b37e3e18c24ea2e3fd. 원본의 경로/링크/크기/파일집합/125개 hash를 검증한 뒤 임시 입력 폴더로 풀었다.
- **기존 consumer 함수** `validate_record`, `stage`, `verify_staged`, `validate_source`를 실제 bytes에 호출해 모두 통과했다. POSIX nofollow 복사·읽기 전후 안정·archive identities·4프로필 wheels/lock·source roots·source hash 및 Dockerfile 고정 형식 일치를 확인했다.

## 실패 경로와 최종 재확인

| 검증 입력만 바꾼 경우 | 실제 거부 코드 |
|---|---|
| builder 예상 hash를 잘못 지정 | STAGED_IMAGE_CHANGED:builder |
| API test profile 예상 roots hash를 잘못 지정 | STAGED_PROFILE_CHANGED |
| source apko builder 입력 예상 hash를 잘못 지정 | SOURCE_APKO_INPUT_CHANGED:ci/apko/wolfi-python313-builder.apko.yaml |

위3건은 메모리상의 검증 입력 사본만 바꿨다. 공급 bytes/원본/활성 config를 변조한 시험이 아니다. 세 경우 모두 예상 오류로 거부되었고 원래 입력의 verify_staged/validate_source를 마지막에 재확인해 PASS했다. MOCK 없이 현재 consumer 함수를 호출했지만 전체 가능한 실패 경로를 전수 검증했다는 뜻은 아니다.

## 실행·회수·정리

PC 실행08:44:13~18 KST, 원 stdout의 서버 시각은 별도로 보존한다. SSH rc0·stderr0, 결과 SHA12e5088449bf462543a729a4f68c180e612b3bc1cbfa1184e7b2091b1a9bbf63. PC와 서버의 시각 오차를 새로 검증한 것은 아니다.

08:45:03 KST 임시 `/home/server01_ansible/app-supply-check.vbuuk32j`의270파일 전체를 로컬 입력·수신 결과의 hash 및 정확한 파일/디렉터리 집합과 대조한 뒤 제거했다. 정리 원본 stdout/rc/script/payload/hash를 함께 보존한다. 새로운 공급물은 로컬 원 ZIP으로 계속 보관한다. 다른 담당자·Runner에 공급 인계한 상태가 아니다.

검증기는 host/정상계정/고정09시 종료 gate와 전용 폴더 검사를 사용했다. 원본 검증기의 고정 시간을 지우거나 수정한 뒤 같은 검증으로 취급하지 않는다. 재현은 원 Source/tool/blob·ZIP/manifest hash를 확인한 새 전용 작업 폴더와 허용된 회차로 수행하고, 그 회차의 검증기 SHA와 결과를 별도 기록한다. 현재 임시 경로는 정리되어 재실행 대상이 아니다.

## 남은 범위

검증용 dictionary에는 승인자·승인참조·APPROVED 상태가 없고 실행 config 파일을 만들지 않았다. `materialize_app_build_scan_v3` 및 전체 `build_scan.validate_config`는 호출하지 않았다. 신규 검증기 독립 리뷰도 아직이다. APP 승인, API Unit 처분, 공급 tool 승인 연결, 실제 Runner 경로·freshness·이미지 load·패키지 설치·테스트·Build/Scan·Push/Deploy 및 AC 인수를 대신하지 않는다. 시스템 서비스·방화벽·보안정책·운영파일 변경은 없다.
