#!/usr/bin/env bash
# 常驻启动：起 Neo4j → 8 个 Java 服务 → Agent → 前端，然后挂住不退。
# 只给「需要在当前会话里一直跑」的场景用；日常用 启动全部.bat。
set -u

ROOT="$(cd "$(dirname "$0")/.." && pwd -W)"
LOG="$ROOT/logs"
mkdir -p "$LOG"
JAVA="/d/tools/jdk17/bin/java.exe"
NEO="/d/tools/neo4j/neo4j-community-5.26.0"
PY="/d/tools/venvs/herbmind/Scripts/python.exe"

port_up() { netstat -ano 2>/dev/null | grep LISTENING | grep -q ":$1 "; }
wait_port() { for i in $(seq 1 "$2"); do port_up "$1" && return 0; sleep 1; done; return 1; }

# PostgreSQL：本机直装版（数据在 D:\pgdata）
if ! port_up 5432; then
  echo "[start] postgres"
  rm -f /d/pgdata/postmaster.pid 2>/dev/null
  ( /d/tools/pg17/bin/postgres.exe -D /d/pgdata >> "$LOG/pg.log" 2>&1 ) &
fi

if ! port_up 7474; then
  echo "[start] neo4j"
  ( cd "$NEO" && "$JAVA" -cp "lib/*" -Dbasedir="$NEO" org.neo4j.server.CommunityEntryPoint \
      --home-dir="$NEO" --config-dir="$NEO/conf" >> "$LOG/neo4j.log" 2>&1 ) &
fi

wait_port 5432 40 && echo "[ok] postgres" || echo "[warn] postgres 未就绪"

start_svc() {
  local name="$1" port="$2"
  if port_up "$port"; then echo "[skip] $name :$port"; return; fi
  echo "[start] $name :$port"
  ( cd "$ROOT" && unset SERVER_PORT SERVER__PORT && \
    "$JAVA" -jar "$ROOT/backend/$name/target/$name-2.0.0-SNAPSHOT.jar" --server.port="$port" \
    >> "$LOG/$name.log" 2>&1 ) &
  sleep 3
}

for pair in svc-identity:8081 svc-catalog:8082 svc-search:8083 svc-training:8084 \
            svc-graph:8085 svc-insight:8086 herbmind-bff:8090 herbmind-gateway:8080; do
  start_svc "${pair%%:*}" "${pair##*:}"
done

wait_port 8080 90 && echo "[ok] gateway" || echo "[warn] gateway 未就绪"

if ! port_up 8091; then
  echo "[start] agent"
  ( cd "$ROOT/agent" && "$PY" run.py --host 0.0.0.0 --port 8091 >> "$LOG/agent.log" 2>&1 ) &
fi

if ! port_up 5173; then
  echo "[start] frontend"
  ( cd "$ROOT/frontend" && npm_config_cache='D:/npm-cache' npm run dev >> "$LOG/frontend.log" 2>&1 ) &
fi

wait_port 5173 60 && echo "[ok] frontend" || echo "[warn] frontend 未就绪"
echo "[ready] 全部启动完成，进程挂住中…"

# 挂住，避免脚本退出导致子进程被回收
while true; do sleep 60; done
