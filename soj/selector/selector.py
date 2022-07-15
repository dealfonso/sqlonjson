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
from ..result import Result 

class Selector:
    """Selector is the abstraction of a selector of parts of a JSON object
    """

    def __init__(self, next: "Selector" = None) -> None:
        """Creates the selector

        Args:
            next (Selector, optional): Is the next selector that has to be applied to the results of this one. Defaults to None.
        """
        self._next = next

    def select(self, obj) -> "Result":
        """Obtains the list of objects that match the selector (and the chain of next selectors)

        Args:
            obj (dict): the object from which to apply the selector

        Returns:
            The objects that match the selector, from object <obj>
        """
        raise NotImplementedError()

    @property
    def next(self, next: "Selector") -> "Selector":
        """Sets the next selector

        Args:
            next (Selector): The selector that has to be applied to the results of this one.

        Returns:
            Selector: the selector (to enable chaining)
        """
        self._next = next
        return self._next

    def __add__(self, next : "Selector") -> "Selector":
        """Appends a selector to the end of the chain of selectors that are to be applied after this one

        Args:
            next (Selector): the selector to be appended to the end of the chain

        Returns:
            Selector: this object (to enable chaining)
        """
        if isinstance(next, Empty):
            next = next._next

        if self._next is None:
            self._next = next
        else:
            self._next += next
        return self
    def _to_str(self):
        """A string representation of the selector
        """
        raise NotImplementedError()
    def __str__(self) -> str:
        """The generic string representation of the selector, that appends the string representation of the chain of next selectors

        Returns:
            str: The string representation of the selector
        """
        result = self._to_str()
        if self._next is not None:
            result = f"{result}{self._next}"
        return result
    def get(self, obj):
        """Gets the objects that matches the selector (and the chain of next selectors)

        Args:
            obj (list): the list from which to apply the selector

        Returns:
            list | dict: the resulting objects
        """
        raise NotImplementedError()

class Empty(Selector):
    def _to_str(self):
        return f"$"
    def get(self, obj: dict):
        return obj
    def select(self, obj) -> "Result":
        return Result(obj)

class Constant(Selector):
    def __init__(self, value) -> None:
        super().__init__(None)
        self._value = value
    def _to_str(self):
        return f"{self._value}"
    def get(self, obj):
        return self._value
    def select(self, obj) -> "Result":
        return Result(self._value)