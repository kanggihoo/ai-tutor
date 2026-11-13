#!/usr/bin/env bash
# 깨끗한 상태에서 case들을 두 번 연속 돌리고 CHECK/RESULT 줄이 같은지 비교한다.
# 사용법: ./verify.sh <이름> [case 접두어]   예) ./verify.sh sl sl   -> logs/sl-1, logs/sl-2
# 이미 있는 로그 디렉터리는 지우지 않는다(baseline 보존). 같은 이름이 있으면 중단한다.
# 종료 코드: 두 round 모두 전부 PASS이고 판정 줄이 같으면 0
set -u
cd "$(dirname "$0")"
NAME="${1:?verify 이름을 주세요 (예: sl)}"
FILTER="${2:-}"
for r in "$NAME-1" "$NAME-2"; do
  [ -e "logs/$r" ] && { echo "logs/$r 이 이미 있다. 다른 이름을 쓰거나 직접 옮기세요."; exit 2; }
done
ROUND="$NAME-1" ./run.sh $FILTER; rc1=$?
ROUND="$NAME-2" ./run.sh $FILTER; rc2=$?
norm() { for f in $(ls "logs/$1"/*.log | grep -v '\.floci\.log$' | sort); do grep -h -E '^(CHECK|RESULT) ' "$f"; done; }
norm "$NAME-1" > "logs/$NAME-1/checks.txt"
norm "$NAME-2" > "logs/$NAME-2/checks.txt"
if diff -u "logs/$NAME-1/checks.txt" "logs/$NAME-2/checks.txt" > "logs/$NAME-1-vs-2.diff"; then same=0; echo "$NAME-1 == $NAME-2 ($(wc -l < "logs/$NAME-1/checks.txt") lines)"; else same=1; echo "$NAME-1 != $NAME-2, see logs/$NAME-1-vs-2.diff"; fi
echo "rc1=$rc1 rc2=$rc2"
[ $rc1 -eq 0 ] && [ $rc2 -eq 0 ] && [ $same -eq 0 ]
