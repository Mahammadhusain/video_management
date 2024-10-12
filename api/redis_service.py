import redis

# Connect to the Redis server
redis_client = redis.Redis(host='localhost', port=6379, db=0)

# Helper function to set block status in cache
def cache_block_status(video_id: int, is_blocked: bool):
    redis_key = f"video_block_status:{video_id}"
    redis_client.set(redis_key, int(is_blocked))

# Helper function to check block status from cache
def is_video_blocked(video_id: int) -> bool:
    redis_key = f"video_block_status:{video_id}"
    cached_value = redis_client.get(redis_key)
    # If no cache is found, default to not blocked
    return cached_value is not None and int(cached_value) == 1
