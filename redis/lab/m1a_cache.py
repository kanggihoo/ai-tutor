"""①-a cache-aside: 상품 조회(캐시 우선)와 가격 변경(DB 갱신 → 캐시 무효화).

uv run m1a_cache.py read 1
uv run m1a_cache.py update 1 200
"""

import sys

from common import TTL, connect, hook, rds

r = rds()


def key(pid: int) -> str:
    return f"product:{pid}"


def read(pid: int) -> dict:
    # 1) Redis에서 먼저 찾는다. 있으면 DB는 안 간다
    cached = r.hgetall(key(pid))
    if cached:
        return {"from": "cache", **cached}

    # 2) 캐시 미스 → 원본 DB에서 가격과 버전을 읽는다
    with connect() as conn:
        price, v = conn.execute(
            "SELECT price, version FROM products WHERE id = %s", (pid,)
        ).fetchone()

    hook("after_db_read")  # 실험: 여기서 멈춘 사이에 다른 요청이 끼어든다

    # 3) 읽은 값을 Redis에 채운다  ← 결정 지점 (읽은 지 오래된 값이어도 그냥 쓴다)
    r.hset(key(pid), mapping={"price": price, "v": v})
    r.expire(key(pid), TTL)
    return {"from": "db", "price": price, "v": v}


def update(pid: int, price: int) -> None:
    # 1) 원본 DB를 고치고 버전을 1 올린다. with 블록이 끝날 때 커밋
    with connect() as conn:
        conn.execute(
            "UPDATE products SET price = %s, version = version + 1 WHERE id = %s",
            (price, pid),
        )

    hook("after_commit")  # 실험: 커밋은 됐고 캐시는 아직 안 지움

    # 2) 캐시를 지운다  ← 결정 지점
    r.delete(key(pid))


if __name__ == "__main__":
    cmd, pid, *rest = sys.argv[1:]
    if cmd == "read":
        print(read(int(pid)))
    else:
        update(int(pid), int(rest[0]))
        print("updated")
