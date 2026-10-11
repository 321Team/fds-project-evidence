#!/usr/bin/env bash
# infra-terraform#8 S10 — bootstrap stack 실제 템플릿의 Retain 확인 v1
# 성격: 조회만 (sts get-caller-identity, cloudformation describe-stacks, get-template). AWS 변경 없음.
# 실행: AWS CloudShell (ap-northeast-2), 321team-hayeoung 본인 로그인. set -e 미사용(명령별 RC 기록).
# 범위: "Original 템플릿에 Retain이 적혀 있는가"만 판정한다. 실제 자원 설정 전체·drift 무변경 증명이 아니다.

ACCOUNT=774055931866
REGION=ap-northeast-2
STACK_ID="arn:aws:cloudformation:ap-northeast-2:774055931866:stack/FDS-Central-Bootstrap-v1/79b25940-c211-11f1-ab33-0a7d3f30f8ff"
EXPECTED='["RelayProfile","RelayRole","StateBucket","StateBucketPolicy"]'

umask 077
OUT=$(mktemp -d "$HOME/issue8-s10-retain.XXXXXX")
log() { echo "$1" | tee -a "$OUT/summary.txt"; }
log "OUT_DIR=$OUT"
log "SCRIPT_SHA256=$(sha256sum "$0" | cut -d' ' -f1)"
log "START_KST=$(TZ=Asia/Seoul date '+%Y-%m-%d %H:%M:%S')"
log "START_UTC=$(date -u '+%Y-%m-%dT%H:%M:%SZ')"

# 1. 실행자·계정
aws sts get-caller-identity --output json > "$OUT/01-identity.json" 2> "$OUT/01-identity.stderr"
rc=$?; log "IDENTITY_RC=$rc"
acct=$(jq -r .Account "$OUT/01-identity.json" 2>/dev/null)
log "CALLER_ARN=$(jq -r .Arn "$OUT/01-identity.json" 2>/dev/null)"
if [ $rc -ne 0 ] || [ "$acct" != "$ACCOUNT" ]; then log "STOP=WRONG_ACCOUNT_OR_IDENTITY_FAILED($acct)"; exit 2; fi

# 2. stack 식별·상태
aws cloudformation describe-stacks --region "$REGION" --stack-name "$STACK_ID" --output json \
  > "$OUT/02-describe-stacks.json" 2> "$OUT/02-describe-stacks.stderr"
rc=$?; log "DESCRIBE_STACKS_RC=$rc"
if [ $rc -ne 0 ]; then log "STOP=DESCRIBE_STACKS_FAILED"; exit 3; fi
log "STACK_ID=$(jq -r '.Stacks[0].StackId' "$OUT/02-describe-stacks.json")"
log "STACK_STATUS=$(jq -r '.Stacks[0].StackStatus' "$OUT/02-describe-stacks.json")"
log "TERMINATION_PROTECTION=$(jq -r '.Stacks[0].EnableTerminationProtection' "$OUT/02-describe-stacks.json")"

# 3. 실제 배포 템플릿 원본 (Original stage)
aws cloudformation get-template --region "$REGION" --stack-name "$STACK_ID" --template-stage Original --output json \
  > "$OUT/03-get-template.json" 2> "$OUT/03-get-template.stderr"
rc=$?; log "GET_TEMPLATE_RC=$rc"
if [ $rc -ne 0 ]; then log "STOP=GET_TEMPLATE_FAILED"; exit 4; fi
log "TEMPLATE_BODY_TYPE=$(jq -r '.TemplateBody | type' "$OUT/03-get-template.json")"

# 4. 판정 (저장된 원본 파일에서 계산)
jq '.TemplateBody.Resources | map_values({Type, DeletionPolicy, UpdateReplacePolicy})' \
  "$OUT/03-get-template.json" > "$OUT/04-retain-summary.json"
rc=$?; log "SUMMARY_JQ_RC=$rc"
names=$(jq -c 'keys' "$OUT/04-retain-summary.json")
retain_count=$(jq '[.[] | select(.DeletionPolicy=="Retain" and .UpdateReplacePolicy=="Retain")] | length' "$OUT/04-retain-summary.json")
log "RESOURCES=$names"
log "RETAIN_BOTH_COUNT=$retain_count"
if [ "$names" = "$EXPECTED" ] && [ "$retain_count" = "4" ]; then
  log "S10_RETAIN=PASS (Original template, 4/4 Retain/Retain)"
else
  log "S10_RETAIN=CHECK_REQUIRED"
fi

# 5. 마무리
log "END_KST=$(TZ=Asia/Seoul date '+%Y-%m-%d %H:%M:%S')"
log "AWS_MUTATION=NOT_RUN"
(cd "$OUT" && sha256sum -- 0*.json 0*.stderr summary.txt > SHA256SUMS)
echo "SHA256SUMS_RC=$?"
echo "----- SHA256SUMS -----"; cat "$OUT/SHA256SUMS"
echo "----- 01-identity.json -----"; cat "$OUT/01-identity.json"
echo "----- 03-get-template.json -----"; cat "$OUT/03-get-template.json"
echo "----- 04-retain-summary.json -----"; cat "$OUT/04-retain-summary.json"
echo "PRESERVED_DIR=$OUT"
