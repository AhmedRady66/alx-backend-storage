#!/usr/bin/env python3
"""File to write string to redis"""
from functools import wraps
import redis
import uuid
from typing import Union, Callable, Optional


def count_calls(method: Callable) -> Callable:
    """Count how many times methods of the Cache class are called"""
    @wraps(method)
    def wrapper(self, *args, **kwargs):
        """Return the given method after incrementing its call counter"""
        if isinstance(self._redis, redis.Redis):
            self._redis.incr(method.__qualname__)
        return method(self, *args, **kwargs)

    return wrapper


def call_history(method: Callable) -> Callable:
    """store the history of inputs and outputs for a particular function"""
    @wraps(method)
    def wrapper(self, *args, **kwargs):
        """Add its input parameters to one list in redis,
        and store its output into another list."""
        in_key = f"{method.__qualname__}:inputs"
        out_key = f"{method.__qualname__}:outputs"
        if isinstance(self._redis, redis.Redis):
            self._redis.rpush(in_key, str(args))
        output = method(self, *args, **kwargs)
        if isinstance(self._redis, redis.Redis):
            self._redis.rpush(out_key, output)
        return output
    return wrapper


class Cache:
    """Represents an object for storing data in a Redis data storage"""

    def __init__(self) -> None:
        """Initialize the Redis client and flush the database"""
        self._redis = redis.Redis()
        self._redis.flushdb()

    @count_calls
    @call_history
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
