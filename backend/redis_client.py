import redis
from config import REDIS_HOST, REDIS_PORT, REDIS_DB

redis_client = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=REDIS_DB)

def cache_position(position):
    redis_client.hset(
        f"position:{position['mac']}",
        mapping={
            "x": str(position["x"]),
            "y": str(position["y"]),
            "timestamp": position["timestamp"]
        }
    )
    redis_client.expire(f"position:{position['mac']}", 3600)  # Hết hạn sau 1 giờ

def get_position(mac):
    position = redis_client.hgetall(f"position:{mac}")
    if position:
        return {
            "mac": mac,
            "x": float(position[b"x"]),
            "y": float(position[b"y"]),
            "timestamp": position[b"timestamp"].decode()
        }
    return None

def cache_references(references):
    for ref in references:
        redis_client.hset(
            f"reference:{ref['reference_id']}",
            mapping={
                "type": ref["type"],
                "name": ref["name"],
                "x": str(ref["x"]),
                "y": str(ref["y"]),
                "radius": str(ref["radius"] or "")
            }
        )

def get_references():
    keys = redis_client.keys("reference:*")
    references = []
    for key in keys:
        ref = redis_client.hgetall(key)
        references.append({
            "reference_id": key.decode().split(":")[1],
            "type": ref[b"type"].decode(),
            "name": ref[b"name"].decode(),
            "x": float(ref[b"x"]),
            "y": float(ref[b"y"]),
            "radius": float(ref[b"radius"]) if ref[b"radius"] else None
        })
    return references