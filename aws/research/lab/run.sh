#!/usr/bin/env bash
# 사용법:
#   ./run.sh                 cases.txt의 모든 case를 한 번 돌린다
#   ./run.sh t01             이름이 t01로 시작하는 case만
#   ROUND=r2 ./run.sh        로그를 logs/r2/ 아래에 남긴다 (기본 r1)
# 각 case: compose down -v -> 지정 env로 up -> client에서 python 실행 -> 로그 저장 -> down -v -> floci가 띄운 컨테이너 정리
# 종료 코드: 모든 case가 PASS면 0, 아니면 1
set -u
export MSYS_NO_PATHCONV=1
cd "$(dirname "$0")"
ROUND="${ROUND:-r1}"
FILTER="${1:-}"
mkdir -p "logs/$ROUND"
SUMMARY="logs/$ROUND/summary.txt"
: > "$SUMMARY"
overall=0

cleanup_spawned() {
  # floci가 이 lab용으로 띄운 자원만 지운다. compose가 FLOCI_DOCKER_RESOURCE_NAMESPACE=${LAB_NS:-awslab}을 주므로
  # 컨테이너·볼륨 이름은 floci-aws-<ns>-..., VPC 네트워크는 label floci_namespace=<ns>를 갖는다(2026-11-13 확인).
  local ns="${LAB_NS:-awslab}"
  ids=$(docker ps -aq --filter "name=^floci-aws-${ns}-" 2>/dev/null)
  [ -n "$ids" ] && docker rm -f $ids >/dev/null 2>&1
  nets=$(docker network ls -q --filter "label=floci_namespace=${ns}" 2>/dev/null)
  [ -n "$nets" ] && docker network rm $nets >/dev/null 2>&1
  vols=$(docker volume ls -q --filter "name=^floci-aws-${ns}-" 2>/dev/null)
  [ -n "$vols" ] && docker volume rm -f $vols >/dev/null 2>&1
  true
}

down() { docker compose down -v --remove-orphans >/dev/null 2>&1; cleanup_spawned; }

while IFS='|' read -r label script envs; do
  label="$(echo "$label" | xargs)"; script="$(echo "$script" | xargs)"; envs="$(echo "$envs" | xargs)"
  [ -z "$label" ] && continue
  case "$label" in \#*) continue;; esac
  [ -n "$FILTER" ] && [[ "$label" != $FILTER* ]] && continue
  log="logs/$ROUND/$label.log"
  down
  # shellcheck disable=SC2086
  env $envs docker compose up -d floci >/dev/null 2>&1 < /dev/null
  for _ in $(seq 1 60); do curl -sf localhost:4566/_floci/health >/dev/null && break; sleep 1; done
  {
    echo "# case=$label script=$script env=[$envs] round=$ROUND date=$(date -Iseconds)"
    docker logs awslab-floci 2>&1 | grep -E "IAM: |Security group|security-group|SCP" | head -5 | sed 's/^/# floci: /'
  } > "$log"
  eargs=(-e "LAB_MODE=$label"); for kv in $envs; do eargs+=(-e "$kv"); done
  if [[ "$script" == *.sh ]]; then
    # shellcheck disable=SC2086
    env $envs LAB_MODE="$label" bash "./$script" >> "$log" 2>&1 < /dev/null
  else
    # shellcheck disable=SC2086
    env $envs docker compose --profile client run --rm -T "${eargs[@]}" client python "/lab/$script" >> "$log" 2>&1 < /dev/null
  fi
  rc=$?
  docker logs awslab-floci > "logs/$ROUND/$label.floci.log" 2>&1
  if [ $rc -eq 0 ]; then st=PASS; else st=FAIL; overall=1; fi
  echo "$st $label" | tee -a "$SUMMARY"
  down
done < cases.txt

exit $overall
