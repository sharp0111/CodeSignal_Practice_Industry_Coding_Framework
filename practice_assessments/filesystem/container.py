from __future__ import annotations

import heapq
from collections import Counter, defaultdict


class Container:
    """
    A container of integers that should support
    addition, removal, and search for the median integer
    """

    def __init__(self):
        self._low = []
        self._high = []

        self._del_low = defaultdict(int)
        self._del_high = defaultdict(int)

        self._count = Counter()
        self._count_low = Counter()
        self._count_high = Counter()

        self._n_low = 0
        self._n_high = 0

    def add(self, value: int) -> None:
        """
        Adds the specified value to the container

        :param value: int
        """
        # TODO: implement this method
        self._count[value] += 1

        if self._n_low == 0:
            heapq.heappush(self._low, -value)
            self._count_low[value] += 1
            self._n_low += 1
        else:
            self._prune_low()
            median = -self._low[0]
            if value <= median:
                heapq.heappush(self._low, -value)
                self._count_low[value] += 1
                self._n_low += 1
            else:
                heapq.heappush(self._high, value)
                self._count_high[value] += 1
                self._n_high += 1

        self._rebalance()

    def delete(self, value: int) -> bool:
        """
        Attempts to delete one item of the specified value from the container

        :param value: int
        :return: True, if the value has been deleted, or
                 False, otherwise.
        """
        # TODO: implement this method
        if self._count[value] == 0:
            return False

        self._count[value] -= 1
        if self._count[value] == 0:
            del self._count[value]

        self._prune_low()
        self._prune_high()

        if self._count_low.get(value, 0) > 0:
            self._del_low[value] += 1
            self._count_low[value] -= 1
            if self._count_low[value] == 0:
                del self._count_low[value]
            self._n_low -= 1
        else:
            self._del_high[value] += 1
            self._count_high[value] -= 1
            if self._count_high[value] == 0:
                del self._count_high[value]
            self._n_high -= 1

        self._prune_low()
        self._prune_high()
        self._rebalance()
        return True

    def get_median(self) -> int:
        """
        Finds the container's median integer value, which is
        the middle integer when the all integers are sorted in order.
        If the sorted array has an even length,
        the leftmost integer between the two middle
        integers should be considered as the median.

        :return: The median if the array is not empty, or
        :raise:  a runtime exception, otherwise.
        """
        # TODO: implement this method
        if (self._n_low + self._n_high) == 0:
            raise RuntimeError("Container is empty")

        self._prune_low()
        self._prune_high()
        self._rebalance()
        self._prune_low()
        return -self._low[0]

    def _prune_low(self) -> None:
        while self._low:
            v = -self._low[0]
            if self._del_low.get(v, 0) > 0:
                heapq.heappop(self._low)
                self._del_low[v] -= 1
                if self._del_low[v] == 0:
                    del self._del_low[v]
            else:
                break

    def _prune_high(self) -> None:
        while self._high:
            v = self._high[0]
            if self._del_high.get(v, 0) > 0:
                heapq.heappop(self._high)
                self._del_high[v] -= 1
                if self._del_high[v] == 0:
                    del self._del_high[v]
            else:
                break

    def _rebalance(self) -> None:
        self._prune_low()
        self._prune_high()

        if self._n_low > self._n_high + 1:
            self._prune_low()
            x = -heapq.heappop(self._low)

            self._count_low[x] -= 1
            if self._count_low[x] == 0:
                del self._count_low[x]
            self._n_low -= 1

            heapq.heappush(self._high, x)
            self._count_high[x] += 1
            self._n_high += 1

            self._prune_low()
            self._prune_high()

        elif self._n_low < self._n_high:
            self._prune_high()
            x = heapq.heappop(self._high)

            self._count_high[x] -= 1
            if self._count_high[x] == 0:
                del self._count_high[x]
            self._n_high -= 1

            heapq.heappush(self._low, -x)
            self._count_low[x] += 1
            self._n_low += 1

            self._prune_low()
            self._prune_high()
