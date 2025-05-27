import redis


def cache():
    return redis.Redis(
        host="localhost",
        port=6379
    )