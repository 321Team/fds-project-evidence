#!/usr/bin/env bash
# U1-I1 / U1-I4(safe subset) — 하영 본인 MFA -> FDS-IaC-Operator 역할 시험
# 실행 위치: AWS CloudShell (서울), 321team-hayeoung 콘솔 로그인 상태
# 비용: 없음 (STS·Describe·dry-run·HeadObject만. 자원 생성/수정/삭제 0)
# 금지: MFA 코드·임시 자격증명을 파일/로그/채팅에 남기지 않는다. state 실제 삭제 시험 없음.
set -u
ACCOUNT=774055931866
REGION=ap-northeast-2
ME=321team-hayeoung
ROLE_ARN="arn:aws:iam::${ACCOUNT}:role/FDS-IaC-Operator"
BUCKET="fds-tfstate-${ACCOUNT}-${REGION}"
OUT="$HOME/u1-hayeoung-$(date +%Y%m%d-%H%M%S)"
mkdir "$OUT" && chmod 700 "$OUT" || exit 1
SUMMARY="$OUT/summary.tsv"
printf 'case\texpect\tactual\tresult\n' > "$SUMMARY"
kst() { TZ=Asia/Seoul date '+%Y-%m-%dT%H:%M:%S%z'; }
echo "start_kst=$(kst) host=$(hostname)" > "$OUT/meta.txt"
sha256sum "$0" >> "$OUT/meta.txt"

# run CASE EXPECT CMD... : stdout/stderr/rc 보존, 결과 문구로 판정. MFA 코드는 기록하지 않는다
run() {
  local c=$1 exp=$2; shift 2
  local shown=() mask=0 a
  for a in "$@"; do
    if [ $mask -eq 1 ]; then shown+=(REDACTED); mask=0; else shown+=("$a"); fi
    [ "$a" = "--token-code" ] && mask=1
  done
  { echo "kst=$(kst)"; printf 'argv:'; printf ' %q' "${shown[@]}"; echo; } > "$OUT/$c.cmd"
  "$@" > "$OUT/$c.stdout" 2> "$OUT/$c.stderr"
  local rc=$?
  echo "rc=$rc" >> "$OUT/$c.cmd"
  local act
  if [ $rc -eq 0 ]; then act=OK
  elif grep -q 'DryRunOperation' "$OUT/$c.stderr"; then act=DRYRUN_ALLOWED
  elif grep -qE 'UnauthorizedOperation|AccessDenied|explicit deny|Forbidden|\(403\)' "$OUT/$c.stderr"; then act=DENIED
  elif grep -qE 'Not Found|\(404\)' "$OUT/$c.stderr"; then act=NOT_FOUND
  else act="OTHER_RC$rc"; fi
  local res=FAIL
  case "$exp" in
    *"$act"*) res=PASS ;;
  esac
  printf '%s\t%s\t%s\t%s\n' "$c" "$exp" "$act" "$res" >> "$SUMMARY"
  echo "[$res] $c expect=$exp actual=$act"
}

# 0. 가드: 본인 사용자·계정 확인
aws sts get-caller-identity --output json --no-cli-pager > "$OUT/00-guard.stdout" 2> "$OUT/00-guard.stderr"
CALLER=$(jq -r .Arn "$OUT/00-guard.stdout" 2>/dev/null)
if [ "$CALLER" != "arn:aws:iam::${ACCOUNT}:user/${ME}" ]; then
  echo "STOP: 현재 identity=$CALLER (기대 user/${ME}). root/다른 사용자로 실행하지 마세요."; exit 2
fi
echo "guard OK: $CALLER"

# MFA 장치 ARN
SERIAL=$(aws iam list-mfa-devices --user-name "$ME" --query 'MFADevices[0].SerialNumber' --output text --no-cli-pager 2>/dev/null)
if [ -z "$SERIAL" ] || [ "$SERIAL" = "None" ]; then
  read -r -p "MFA 장치 ARN 입력 (IAM > 보안 자격 증명에서 확인): " SERIAL
fi
echo "mfa_serial=$SERIAL" >> "$OUT/meta.txt"

ask_code() { local c; read -r -s -p "$1 MFA 6자리 (화면에 안 보임): " c; echo >&2; printf '%s' "$c"; }

# 1. 거부: 잘못된 session 이름 (MFA는 정상 제공)
CODE=$(ask_code "[1/3] 첫 번째")
run N1-wrong-session-name DENIED \
  aws sts assume-role --role-arn "$ROLE_ARN" --role-session-name 321team-gwonuk \
  --serial-number "$SERIAL" --token-code "$CODE" --region "$REGION" --output json --no-cli-pager
sed -i 's/"SecretAccessKey": "[^"]*"/"SecretAccessKey": "REDACTED"/; s/"SessionToken": "[^"]*"/"SessionToken": "REDACTED"/' "$OUT/N1-wrong-session-name.stdout"

# 2. 거부: MFA 없이 정확한 session 이름
#    CloudShell이 콘솔 MFA 문맥을 넘겨 주면 성공할 수 있음 -> INFO로만 기록
run N2-no-mfa-token DENIED \
  aws sts assume-role --role-arn "$ROLE_ARN" --role-session-name "$ME" --region "$REGION" --output json --no-cli-pager
sed -i 's/"SecretAccessKey": "[^"]*"/"SecretAccessKey": "REDACTED"/; s/"SessionToken": "[^"]*"/"SessionToken": "REDACTED"/' "$OUT/N2-no-mfa-token.stdout"
if grep -q $'^N2-no-mfa-token\t.*\tOK\t' "$SUMMARY"; then
  sed -i $'s/^\\(N2-no-mfa-token\t[^\t]*\tOK\t\\)FAIL$/\\1INFO_CLOUDSHELL_MFA_CONTEXT/' "$SUMMARY"
  echo "  -> N2 성공은 CloudShell 콘솔 MFA 문맥 때문일 수 있음. 판정은 리뷰에서."
fi

# 3. 성공: MFA + 정확한 session 이름 (새 코드 필요)
echo "30초 정도 기다려 새 코드가 나오면 입력하세요."
CODE=$(ask_code "[2/3] 새")
echo "kst=$(kst)" > "$OUT/P1-assume.cmd"
CREDS=$(aws sts assume-role --role-arn "$ROLE_ARN" --role-session-name "$ME" \
  --serial-number "$SERIAL" --token-code "$CODE" --duration-seconds 900 \
  --region "$REGION" --output json --no-cli-pager 2> "$OUT/P1-assume.stderr")
RC=$?; unset CODE
echo "rc=$RC" >> "$OUT/P1-assume.cmd"
if [ $RC -ne 0 ]; then
  printf 'P1-assume\tOK\tRC%s\tFAIL\n' "$RC" >> "$SUMMARY"
  echo "STOP: 본인 AssumeRole 실패. $OUT/P1-assume.stderr 확인"; exit 3
fi
echo "$CREDS" | jq '{AssumedRoleUser, Expiration: .Credentials.Expiration}' > "$OUT/P1-assume.stdout"
printf 'P1-assume\tOK\tOK\tPASS\n' >> "$SUMMARY"; echo "[PASS] P1-assume"
export AWS_ACCESS_KEY_ID=$(echo "$CREDS" | jq -r .Credentials.AccessKeyId)
export AWS_SECRET_ACCESS_KEY=$(echo "$CREDS" | jq -r .Credentials.SecretAccessKey)
export AWS_SESSION_TOKEN=$(echo "$CREDS" | jq -r .Credentials.SessionToken)
unset CREDS

# 4. 역할 세션 확인
run P2-role-identity OK aws sts get-caller-identity --output json --no-cli-pager
if ! jq -e --arg a "arn:aws:sts::${ACCOUNT}:assumed-role/FDS-IaC-Operator/${ME}" '.Arn==$a' "$OUT/P2-role-identity.stdout" >/dev/null; then
  sed -i $'s/^\\(P2-role-identity\t.*\t\\)PASS$/\\1FAIL_ARN_MISMATCH/' "$SUMMARY"; echo "  -> ARN 불일치"
fi

# 5. 역할 권한 경계 (생성 0: dry-run / 읽기 / HeadObject)
TAGS='ResourceType=vpc,Tags=[{Key=Project,Value=fds-hybrid},{Key=ManagedBy,Value=terraform},{Key=Name,Value=u1-dryrun}]'
run P3-describe-vpcs-seoul OK aws ec2 describe-vpcs --region "$REGION" --output json --no-cli-pager
run P4-createvpc-dryrun-owned-tags DRYRUN_ALLOWED \
  aws ec2 create-vpc --dry-run --cidr-block 10.250.0.0/16 --tag-specifications "$TAGS" --region "$REGION" --no-cli-pager
run N3-createvpc-dryrun-no-tags DENIED \
  aws ec2 create-vpc --dry-run --cidr-block 10.250.0.0/16 --region "$REGION" --no-cli-pager
run N4-describe-vpcs-us-east-1 DENIED aws ec2 describe-vpcs --region us-east-1 --output json --no-cli-pager
run P5-state-key-head "OK|NOT_FOUND" \
  aws s3api head-object --bucket "$BUCKET" --key phase2/network/terraform.tfstate --expected-bucket-owner "$ACCOUNT" --region "$REGION" --no-cli-pager
run N5-other-state-key-head DENIED \
  aws s3api head-object --bucket "$BUCKET" --key phase2/u1-other/terraform.tfstate --expected-bucket-owner "$ACCOUNT" --region "$REGION" --no-cli-pager
run N6-iam-list-users DENIED aws iam list-users --max-items 1 --output json --no-cli-pager

unset AWS_ACCESS_KEY_ID AWS_SECRET_ACCESS_KEY AWS_SESSION_TOKEN
echo "end_kst=$(kst)" >> "$OUT/meta.txt"
( cd "$OUT" && sha256sum -- * > SHA256SUMS )
echo; column -t -s $'\t' "$SUMMARY"
echo; echo "결과 폴더: $OUT  (이 폴더를 압축해 다운로드하세요)"
grep -q $'\tFAIL' "$SUMMARY" && exit 1 || exit 0
