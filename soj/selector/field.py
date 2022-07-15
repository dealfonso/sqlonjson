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
from . import Selector
from ..result import Result
from ..utils import debug_function

class Field(Selector):
    def __init__(self, field: str, next: "Selector" = None):
        """Creates the list selector

        Args:
            field (str): name of the field
            next ("Selector", optional): the next selector to apply in the chain. Defaults to None.
        """
        super().__init__(next)
        self._field = field

    def _to_str(self) -> str:
        return f".{self._field}"

    def select(self, obj) -> "Result":
        if not isinstance(obj, dict):
            return Result()
        if self._field not in obj:
            return Result()
        if self._next is None:
            return Result(obj[self._field])
        else:
            results = self._next.select(obj[self._field])
            return results

    def get(self, obj):
        if not isinstance(obj, dict):
            return None
        if self._field not in obj:
            return None

        # This is the current implementation
        if self._next is None:
           return obj[self._field]
        else:
           return self._next.get(obj[self._field])


        # ----- ALTERNATIVES -----
        # TODO: not sure how to handle this; if using the first part, 
        #       in case of select x.a.b will remain as x.a.b, while probably expecting x.b but if using the second part,
        #       we have a problem when using x.a[].b because now b is a list of b elements and cannot be added to x as is
        #       because if x has other field (e.g. x.c), a list cannot be merged to x
        #if self._next is None:
        #    return {self._field: obj[self._field]}
        #else:
        #    return {self._field: self._next.get(obj[self._field])}
        # if self._next is None:
        #     return {self._field: obj[self._field]}
        # else:
        #     return self._next.get(obj[self._field])

        # TODO: not sure how to handle this; if using this third approach seems to provide the most consistent results:
        #   if the field is a leaf returns the key and the value, but if it is not, it is expected to return only a value,
        #   but if it is a list, it will return the object {key: list} because it cannot be flattened
        if self._next is None:
            return {self._field: obj[self._field]}
        else:
            result = self._next.get(obj[self._field])
            if isinstance(result, list):
                return {self._field: result}
            else:
                return result