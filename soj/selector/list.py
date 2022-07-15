#
#    Copyright 2022 - Carlos A. <https://github.com/dealfonso>
#
#    Licensed under the Apache License, Version 2.0 (the "License");
#    you may not use this file except in compliance with the License.
#    You may obtain a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS,
#    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#    See the License for the specific language governing permissions and
#    limitations under the License.
#
from .selector import Selector
from .. import Result
from ..utils import debug_function

class ListElement(Selector):
    def __init__(self, index: int, next: "Selector" = None):
        """Creates the list selector

        Args:
            index (int): the index of the element in the list
            next ("Selector", optional): the next selector to apply in the chain. Defaults to None.
        """
        super().__init__(next)
        self._index = index

    def _to_str(self) -> str:
        return f"[{self._field}]"

    def select(self, obj) -> "Result":
        if not isinstance(obj, list):
            return Result()
        if self._index >= len(obj):
            return Result()
        obj = obj[self._index]
        if self._next is None:
            return Result(obj)
        else:
            return self._next.select(obj)

    def get(self, obj: list):
        if not isinstance(obj, list):
            return None
        if self._index >= len(obj):
            return None
        if self._next is None:
            return obj[self._index]
        else:
            return self._next.get(obj[self._index])

class List(Selector):
    def __init__(self, start:int = None, end:int = 1, next: "Selector" = None):
        """Creates the list selector

        Args:
            start (int, optional): the initial limit of the slice. Defaults to None.
            end (int, optional): the end limit of the slice. Defaults to 1.
            next ("Selector", optional): the next selector to apply in the chain. Defaults to None.
        """
        super().__init__(next)
        self._list = []
        self._start = start
        self._end = end
    def _to_str(self) -> str:
        """A string representation of the selector

        Returns:
            str: The string representation of the selector
        """
        if self._start is None:
            if self._end is None:
                return f"[]"
            else:
                return f"[:{self._end}]"
        else:
            if self._end is None:
                return f"[{self._start}:]"
            else:
                return f"[{self._start}:{self._end}]"

    def select(self, obj) -> "Result":
        if not isinstance(obj, list):
            return Result()
        if self._next is None:
            return Result(*obj[self._start:self._end])
        else:
            result = Result()
            for item in obj[self._start:self._end]:
                result.append(self._next.select(item))
            return result

    def get(self, obj: list):
        if not isinstance(obj, list):
            return None
        if self._next is None:
            return obj[self._start:self._end]
        else:
            return list(filter(lambda x: x is not None, [ self._next.get(item) for item in obj[self._start:self._end] ]))

    def alt_get(self, obj: list):
        if not isinstance(obj, list):
            return None
        if self._next is None:
            return obj[self._start:self._end]
        else:
            return list(filter(lambda x: x is not None, [ self._next.get(item) for item in obj[self._start:self._end] ]))
