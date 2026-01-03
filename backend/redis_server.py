import redis

try:
    r = redis.Redis.from_url("redis://localhost:6379")
    r.ping()
    print("✅ Redis is running and accessible")
except redis.ConnectionError:
    print("❌ Cannot connect to Redis")
    raise