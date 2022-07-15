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
from ..result import Result, merge_objects

class Explorer(Selector):
    def select(self, obj) -> "Result":
        # First we get the results of directly applying the next selector to this object
        results_self = Result()
        if self._next is not None:
            results_self = self._next.select(obj)

        # Then we get the results of applying the next selector to each element of the list
        result_k = Result()
        if isinstance(obj, dict):
            for k, v in obj.items():
                result_k += self.select(v)
        elif isinstance(obj, list):
            for v in obj:
                result_k += self.select(v)
        return results_self + result_k
    def get(self, obj):
        results_self = []
        results_k = []
        if self._next is not None:
            v = self._next.get(obj)
            if v is not None:
                if isinstance(v, list):
                    results_self.extend(v)
                else:
                    results_self.append(v)
        if isinstance(obj, dict):
            for k, v in obj.items():
                v = self.get(v)
                if v is not None:
                    if isinstance(v, list):
                        results_self.extend(v)
                    else:
                        results_self.append(v)
        elif isinstance(obj, list):
            for v in obj:
                v = self.get(v)
                if v is not None:
                    if isinstance(v, list):
                        results_self.extend(v)
                    else:
                        results_self.append(v)
        result = results_self + results_k
        if len(result) == 0:
            return None
        return result
    def alt_get(self, obj):
        results_self = []
        results_k = []
        if self._next is not None:
            v = self._next.get(obj)
            if v is not None:
                results_self.append(v)
        if isinstance(obj, dict):
            for k, v in obj.items():
                v = self.get(v)
                if v is not None:
                    results_k.append({k:v})
        elif isinstance(obj, list):
            for v in obj:
                v = self.get(v)
                if v is not None:
                    results_k.append(v)
        result = results_self + results_k
        if len(result) == 0:
            return None
        if len(result) == 1:
            return result[0]
        return result
    def _to_str(self):
        return "."