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
import logging

def merge_objects(obj1 = None, *objs):
    """Merges multiple dictionaries or lists into one, recursively

    Args:
        obj1 (list | dict, optional): the object to merge in. Defaults to None.
        *objs (list | dict): the objects to merge to obj1

    Returns:
        list | dict: the merged object
    """
    for obj2 in objs:
        if obj2 is None:
            # No object to merge
            continue
        if obj1 is None:
            if isinstance(obj2, (list, dict)):
                obj1 = obj2.copy()
            else:
                obj1 = obj2
            continue
        else:
            if (type(obj1) != type(obj2)):
                raise TypeError("Cannot merge objects of different types")
        if isinstance(obj2, list):
            obj1 = obj1 + [ merge_objects(None, x) for x in obj2 ]
        elif isinstance(obj2, dict):
            for k, v in obj2.items():
                if k not in obj1:
                    if isinstance(v, dict):
                        obj1[k] = {}
                    elif isinstance(v, list):
                        obj1[k] = []
                if isinstance(v, dict):
                    obj1[k] = merge_objects(obj1[k], v)
                elif isinstance(v, list):
                    obj1[k] = merge_objects(obj1[k], v)
                else:
                    obj1[k] = v
        else:
            raise TypeError("Cannot merge simple objects")
    return obj1

class Result:
    def __init__(self, *values) -> None:
        self._elements = []
        for value in values:
            self.append(value)
    def __str__(self) -> str:
        return f"{len(self)} results"
    def append(self, *element) -> "Result":
        """Appends one or more elements to the result

        Returns:
            Result: this element (to enable chaining)
        """
        for e in element:
            self._elements.append(e)
        return self
    def __iter__(self):
        """Generates an iterator that yields the elements of the result

        Yields:
            Any: the next element in the result (if an element is a result, it will yield the elements of that result)
        """
        pos = 0
        while pos < len(self._elements):
            if isinstance(self._elements[pos], ( list, dict, str )):
                yield self._elements[pos]
            else:
                try:
                    for j in self._elements[pos]:
                        # print(f"yield from {self}")
                        yield j
                except TypeError:
                    yield self._elements[pos]
            pos += 1
    def __len__(self) -> int:
        """Calculates the amount of elements in the result (taking into account that if an element is a result, it will add the amount of elements in that result)

        Returns:
            int: the amount of elements that contains this result
        """
        return sum([ len(x) if isinstance(x, Result) else 1 for x in self._elements ])
    def __add__(self, other: "Result") -> "Result":
        """Generates a new result with the elements of both results

        Args:
            other (Result): the other result to add

        Returns:
            Result: The result with the elements of both results
        """
        retval = Result()
        for i in self._elements:
            retval.append(i)
        for i in other._elements:
            retval.append(i)
        return retval
    def filter(self, filter: str) -> "Result":
        """Filters the result with the given filter
        
        Args:
            filter (str): the filter to apply to the result
        
        Returns:
            Result: the result with the filtered elements
            
        """
        from .parser.parser import get_parser
        from .filter import Filter
        parser = get_parser()
        if not issubclass(type(filter), Filter):
            try:
                filter = parser.parse_comparison(filter)
            except Exception as e:
                logging.error(f"Error parsing filter: {e}")
                return Result()
        return Result(filter.filter(self))

    def select(self, selector: str) -> "Result":
        """Selects the result with the given selector
        
        Args:
            selector (str): the selector to apply to the result
        
        Returns:
            Result: the result with the selected elements
            
        """
        from .parser.parser import get_parser
        parser = get_parser()
        if isinstance(selector, str):
            try:
                selectors = parser.parse_selectors(selector)
            except Exception as e:
                logging.error(f"Error parsing filter: {e}")
                return Result()
        else:
            if not isinstance(selector, list):
                selector = [selector]
            selectors = selector
        result = Result()

        for element in self:
            obj = None
            for selector in selectors:
                # TODO: initially it was using selector.get, but using .select seems to obtain the expected resuls
                obj = merge_objects(obj, selector.select(element))
            if obj is not None:
                result.append(obj)
        return result
