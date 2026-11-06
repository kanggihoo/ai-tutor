"""①-a 개선 버전: 묘비와 Lua 버전 비교. 기존 m1a_cache.py와 비교용.

uv run m1a_versioned.py read 1
uv run m1a_versioned.py update 1 200

한계: commit 후 묘비 기록 전 사망, 버전 기록 만료·eviction은 막지 못한다.
"""

import sys

from common import TTL, connect, hook, rds
from m1a_cache import key

r = rds()
TOMB_TTL = 60  # 실험용. 오래 멈춘 요청까지 막는 시간 상한을 보장하지 않는다.

# Redis 안에서 버전 검사 + 가격 저장 + TTL 설정을 한 번에 수행한다.
FILL = """
local current = tonumber(redis.call('HGET', KEYS[1], 'v') or '0')
if tonumber(ARGV[2]) < current then
    return 0
end
redis.call('HSET', KEYS[1], 'price', ARGV[1], 'v', ARGV[2])
redis.call('HDEL', KEYS[1], 'tomb')
redis.call('EXPIRE', KEYS[1], ARGV[3])
return 1
"""

# 늦게 도착한 변경 요청이 더 최신 버전의 기준을 낮추지 못하게 한다.
INVALIDATE = """
local current = tonumber(redis.call('HGET', KEYS[1], 'v') or '0')
if tonumber(ARGV[1]) < current then
    return 0
end
redis.call('HSET', KEYS[1], 'v', ARGV[1], 'tomb', '1')
redis.call('HDEL', KEYS[1], 'price')
redis.call('EXPIRE', KEYS[1], ARGV[2])
return 1
"""


def read(pid: int) -> dict:
    cached = r.hgetall(key(pid))
    # 묘비는 가격이 없으므로 cache 미스로 처리한다.
    if cached and "tomb" not in cached:
        return {"from": "cache", **cached}

    with connect() as conn:
        price, v = conn.execute(
            "SELECT price, version FROM products WHERE id = %s", (pid,)
        ).fetchone()

    hook("after_db_read")

    # 저장 거절은 후속 요청의 cache 오염을 막는다. 이번 응답을 재조회하지는 않는다.
    stored = r.eval(FILL, 1, key(pid), price, v, TTL)
    return {"from": "db", "price": price, "v": v, "cache_stored": bool(stored)}


def update(pid: int, price: int) -> None:
    with connect() as conn:
        (v,) = conn.execute(
            "UPDATE products SET price = %s, version = version + 1 "
            "WHERE id = %s RETURNING version",
            (price, pid),
        ).fetchone()

    hook("after_commit")  # DB는 commit됐지만 Redis 묘비는 아직 없다.
    r.eval(INVALIDATE, 1, key(pid), v, TOMB_TTL)


if __name__ == "__main__":
    cmd, pid, *rest = sys.argv[1:]
    if cmd == "read":
        print(read(int(pid)))
    else:
        update(int(pid), int(rest[0]))
        print("updated")
