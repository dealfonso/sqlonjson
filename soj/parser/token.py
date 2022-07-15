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
class Token:
    T_NOTOKEN = "No token"
    T_IDENTIFIER = "Identifier"
    T_IDENTIFIER_SPECIAL = "Special identifier"
    T_DOT = "."
    T_DOT_DOT = ".."
    T_ROOT = "$"
    T_INTEGER = "Integer"
    T_FLOAT = "Float"
    T_STRING = "String"
    T_SQ_OPEN = "["
    T_SQ_CLOSE = "]"
    T_RANGE_SEPARATOR = ":"
    T_SEPARATOR = "Separator"
    T_EOF = "EOF"
    T_OPERATOR = "Operator"
    T_COMMA = ","

    def __init__(self, token: str = T_NOTOKEN, data = None):
        """Creates the object

        Args:
            token (str, optional): The token. It should be any of Token.T_* (it is not controlled at this point). Defaults to T_NOTOKEN.
            data (Any, optional): Additional data, related to the token type. Defaults to None.
        """
        self._token = token
        self._data = data
        # This is a placeholder for the start position of the token
        self.position = None
    @property
    def token(self) -> str:
        """Obtains the token type

        Returns:
            str: the token type (one of Token.T_*)
        """
        return self._token
    @property
    def data(self):
        """Obtains the data related to the token type

        Returns:
            Any: the data
        """
        return self._data
    def __str__(self) -> str:
        """Obtain a string representation of the object.

        Returns:
            str: The string representation
        """
        if isinstance(self._data, str):
            retval = f"{self._token} ({self._data[:32]})"
        else:
            retval = f"{self._token} ({self._data})"
        if self.position is not None:
            retval += f" at {self.position}"
        return retval
    def __ne__(self, other):
        """Returns true if the objects are not equal.

        Args:
            other (Token | str): The other object

        Returns:
            bool: True if the objects are not equal
        """
        return not self.__eq__(other)
    def __eq__(self, other):
        """Returns true if the objects are equal.
            (*) If the other object is a string, it is compared to the token type.
            (*) If the other object is a Token, it is compared to the token type and the data.

        Args:
            other (Token, str): the other object

        Returns:
            bool: True if the objects are equal
        """
        if isinstance(other, Token):
            return self._token == other.token and self._data == other.data
        return self._token == other
