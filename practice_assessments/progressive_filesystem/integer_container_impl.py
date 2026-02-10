# MAKE CHANGE ONLY IN THIS FILE
from integer_container import IntegerContainer

from collections import defaultdict
from bisect import bisect_left, insort


class IntegerContainerImpl(IntegerContainer):

    def __init__(self):
        # TODO: implement
        self._counts = defaultdict(int)
        self._size = 0
        self._keys: list[int] = []

    # TODO: implement interface methods here
    def add(self, value: int) -> int:
        # self._counts[value] += 1
        # self._size += 1
        # return self._size
        if self._counts[value] == 0:
            insort(self._keys, value)
        self._counts[value] += 1
        self._size += 1
        return self._size

    def delete(self, value: int) -> bool:
        # if self._counts.get(value, 0) <= 0:
        #     return False
        # self._counts[value] -= 1
        # self._size -= 1
        # if self._counts[value] == 0:
        #     del self._counts[value]
        # return True
        if self._counts.get(value, 0) == 0:
            return False
        self._counts[value] -= 1
        self._size -= 1
        if self._counts[value] == 0:
            del self._counts[value]
            i = bisect_left(self._keys, value)
            self._keys.pop(i)
        return True

    def get_median(self) -> int | None:
        if self._size == 0:
            return None
        target = (self._size - 1) // 2
        running = 0
        for val in self._keys:
            running += self._counts[val]
            if running > target:
                return val
        return None