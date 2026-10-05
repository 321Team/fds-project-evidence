# worker02 복원 시험 준비안 — 실행 전

상태: PLAN_ONLY / NOT_RUN. 새로운 Runtime 코드나 실행 지시가 아니다. 이번 작업은 증적 편입 준비이며 worker02를 변경하지 않았다.

## 범위·현재 한계

현재 authorized_keys와 NXrcqAmF 백업의 해시는 동일하다. 동일 내용을 덮어쓰는 시험은 복사/접근 경로를 확인할 수 있지만 상태가 실제로 되돌아오는 실패 복구 분기를 입증하지 못한다. 시험을 만들기 위해 운영 키의 restrict/from을 제거하거나 유효 키를 삭제하지 않는다. 기존 .pre-p1-restrict는 최신 기준으로 검증되지 않았으므로 사용하지 않는다.

## 실행 자료에 고정할 사항

- 대상 worker02/10.1.93.107 1대, source5454b77d508cdbfd0eef13e489cbc0322d11c653, controller server01_ansible.
- 원본: /var/lib/ansible-issue9-worker02.NXrcqAmF/authorized_keys.
- 목적지: /home/svc_ansible/.ssh/authorized_keys.
- 기대 hash b7923e8c646b7a7dd2ccba1ac48ddf02d264780db9100317644dcf87216cc834.
- 기대 uid/gid1001:1001, mode0600, SELinux context unconfined_u:object_r:ssh_home_t:s0.
- 사용자 확인한 VMware 콘솔 복구 가능성과 동시 변경 없음은 실행 직전 유지 여부 확인. 키/파일 변동이 있으면 오래된 백업을 즉시 덮어쓰지 않고 차이를 재판정.
- 복원 도구가 신규 코드이면 해당 정확한 SHA를 기존 코드 리뷰 절차로 검토. 임시 파일/소유권/권한/context/원자적 교체/실패 처리/대상 제한을 포함.

## 권고 검증 순서

1. 격리된 파일 fixture에서 정상·백업 해시 불일치·링크·권한 불일치·중간 실패와 실제 내용 복원을 검증한다. 이 결과는 대상 authorized_keys 복원 Runtime PASS가 아니다.
2. 현장 복원 시험이 필요하면 Lead가 안전한 변경 범위와 콘솔 사용 계획을 구체화한다. 별도 승인 없이 운영 키 제한을 해제하거나 SSH 연결을 고의로 끊지 않는다.
3. 실제 복원 수행 시 변경 전후 hash/uid/gid/mode/context, 기존 연결을 재사용하지 않는 fresh SSH와 OS/DNS 기준을 확인한다.
4. 엔진 선택 복귀는 별도 시험이다. 지금은 일회성 절대 경로 실행만 했으며 시스템 RPM·PATH·운영 wrapper를 전환하지 않았다. /usr/bin 엔진 복귀 확인을 파일 상태 복원과 혼동하지 않는다.

## 중단·인수

대상/백업/source 불일치, 동시 변경, 콘솔 미확보, 연결 손실, 예상 밖 파일/서비스 변경 시 추가 진행 중단. 실패 증적을 보존한다. 결과가 없으면 NOT_RUN으로 유지하며 현재 멱등성 PASS로 rollback AC를 대체하지 않는다.
