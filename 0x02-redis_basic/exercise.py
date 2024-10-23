#!/usr/bin/env python3
"""File to write string to redis"""
import redis
import uuid
from typing import Union


class Cache:
    """Represents an object for storing data in a Redis data storage"""

    def __init__(self) -> None:
        """Initialize the Redis client and flush the database"""
        self._redis = redis.Redis()
        self._redis.flushdb()

    @call_history
    @count_calls
    def store(self, data: Union[str, int, float, bytes]) -> str:
        """Store the input data in Redis using a randomly generated key"""
        key = str(uuid.uuid4())
        self._redis.set(key, data)
        return key
