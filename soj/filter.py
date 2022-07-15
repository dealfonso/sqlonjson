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
import re
from . import Result 
from .selector import Selector

class Filter:
    def _evaluate(self, obj) -> bool:
        return True

    def filter(self, obj: "Result"):
        for o in obj:
            if self._evaluate(o):
                yield o

class FilterCompare(Filter):
    def __init__(self, lhs: "Selector", operator: str, rhs: "Selector") -> None:
        if operator not in [ "==", "!=", "<", "<=", ">", ">=", "in", "like" ]:
            raise ValueError(f"Invalid operator: {operator}")
        self._lhs = lhs
        self._operator = operator
        self._rhs = rhs

    def __str__(self):
        return f"{self._lhs} {self._operator} {self._rhs}"

    @staticmethod
    def sql_like_fragment_to_regex_string(fragment):
        # taken from https://codereview.stackexchange.com/a/248421
        _char_regex_map = {
            ch : '\\'+ch
            for ch in '.^$*+?{}[]|()\\'
        }
        _char_regex_map['%'] = '.*?'
        _char_regex_map['_'] = '.'
        return '^' + ''.join([
            _char_regex_map.get(ch, ch)
            for ch in fragment
        ]) + '$'

    def _evaluate(self, obj) -> bool:
        """Evaluates the comparison using the given object, the idea is to 

        Args:
            obj (list | dict): The object to be evaluated

        Returns:
            bool: The result of the comparison
        """

        # Get the value of the left hand side, using the selector

        # En si, el selector puede tener multiples elementos individuales que pueden producir valores singulares, asi
        #   que esto hay que tenerlo en cuenta: hay que hacer un "select" sobre el _lhs y luego sobre el _rhs; si uno
        #   produce un resultado individual, se compara con los resultados individuales del otro selector... pero en
        #   el caso de que ambos produzcan resultados plurales, no sabremos como comparar.
        #
        #   por ejemplo: security_groups[].name producira varias entradas "security_group[i].name" que se pueden comparar
        #       con un selector de tipo "==" con una constante, pero no con otra lista
        #   Si produjésemos un selector de tipo "IN", podriamos comparar con una lista de valores, pero no con una
        selector_lhs = self._lhs.select(obj)
        selector_rhs = self._rhs.select(obj)

        if self._operator == "in":
            return __class__.compare(list(selector_lhs), list(selector_rhs), self._operator)

        if len(selector_lhs) >= 0 and len(selector_rhs) == 1:
            value_rhs = list(self._rhs.select(obj))[0]
            for value_lhs in selector_lhs:
                if __class__.compare(value_lhs, value_rhs, self._operator):
                    return True
            return False
        elif len(selector_lhs) == 1 and len(selector_rhs) >= 0:
            value_lhs = list(self._lhs.select(obj))[0]
            for value_rhs in selector_rhs:
                if __class__.compare(value_lhs, value_rhs, self._operator):
                    return True
            return False
        else:
            return __class__.compare(list(selector_lhs), list(selector_rhs), self._operator)

    @staticmethod
    def compare(v0, v1, op: str):
        """Compares two arbitrary values using a specific operator

        Args:
            v0 (Any): the first value
            v1 (Any): the second value
            op (str): the operator to use to compare the values (==, !=, <, >, <=, >=)

        Returns:
            bool: True if the values match using the operator, False otherwise
        """

        # Not checking for complex types, as we are confindent that the comparisons will be implemented in the correct way
        #   e.g. if a = [1, 2, 3] and b = [1, 2, 3], a==b will return True (python3.9)
        #   e.g. if a = {"b":1,"c":2} and b = {"b":1,"c":2}, a==b will return True (python3.9)
        if op == "like":
            if not isinstance(v0, str):
                return False
            if not isinstance(v1, str):
                return False
            v1 = __class__.sql_like_fragment_to_regex_string(v1)
            return re.match(v1, str(v0)) is not None
        elif op == "in":
            if not isinstance(v1, list):
                return False
            if isinstance(v0, list):
                for v in v0:
                    if v not in v1:
                        return False
                return True
            else:
                return v0 in v1
        elif op == "==":
            if v0 is None:
                return v1 is None
            if v1 is None:
                return v0 is None
            return v0 == v1
        elif op == ">":
            return v0 > v1
        elif op == "<":
            return v0 < v1
        elif op == ">=":
            return v0 >= v1
        elif op == "<=":
            return v0 <= v1
        elif op == "!=":
            return v0 != v1
        else:
            raise ValueError(f"Invalid operator: {op}")     

class FilterKeyExists(FilterCompare):
    def __init__(self, lhs) -> None:
        super().__init__(lhs, "==", None)
        
    def _evaluate(self, obj) -> bool:
        """Evaluates the comparison using the given object, the idea is to 

        Args:
            obj (list | dict): The object to be evaluated

        Returns:
            bool: The result of the comparison
        """

        # Get the value of the left hand side, using the selector
        value_lhs = self._lhs.select(obj)
        return len(value_lhs) > 0