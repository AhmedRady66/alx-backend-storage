#!/usr/bin/env python3
"""File to write string to redis"""
from functools import wraps
import redis
import uuid
from typing import Union, Callable, Optional


def count_calls(method: Callable) -> Callable:
    """Count how many times methods of the Cache class are called"""
    def wrapper(self, *args, **kwargs):
        """Return the given method after incrementing its call counter"""
        if isinstance(self._redis, redis.Redis):
            self._redis.incr(method.__qualname__)
        return method(self, *args, **kwargs)

    return wrapper


class Cache:
    """Represents an object for storing data in a Redis data storage"""

    def __init__(self) -> None:
        """Initialize the Redis client and flush the database"""
        self._redis = redis.Redis()
        self._redis.flushdb()

    @count_calls
    def store(self, data: Union[str, int, float, bytes]) -> str:
        """Store the input data in Redis using a randomly generated key"""
        key = str(uuid.uuid4())
        self._redis.set(key, data)
        return key

    def get(
            self,
            key: str,
            fn: Callable = None,
            ) -> Union[str, bytes, int, float]:
        """Convert the data back to the desired format"""
        data = self._redis.get(key)
        if data is None:
            return data
        if fn:
            callable_fn = fn(data)
            return callable_fn
        else:
            return data

    def get_str(self, key: str) -> str:
        """Retrieve a string value from a Redis data storage"""
        return self.get(key, lambda k: k.decode('utf-8'))

    def get_int(self, key: str) -> int:
        """Retrieve an int value from a Redis data storage"""
        return self.get(key, lambda k: int(k))
