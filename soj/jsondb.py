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
import argparse
import os
import sys
import json
import logging
from .parser.parser import Parser
from .result import Result
from .utils import debug_function
from .selector import Selector
from .version import VERSION

class JSONDB:
    def __init__(self, jsondoc: str) -> None:
        try:
            self._jsondoc = json.loads(jsondoc)
        except Exception as e:
            logging.error(f"Error parsing JSON: {e}")
            raise e
    def FROM(self, query: str) -> "Result":
        if isinstance(query, Selector):
            selector = query
        else:
            selector = Parser().parse_selection(query)

        try:
            pass
        except Exception as e:
            logging.error(f"Error parsing selector: {e}")
            return Result()
        return selector.select(self._jsondoc)
    def query(self, query_str: str):
        query_params = Parser().parse(query_str)
        r_from = self.FROM(query_params["from"])
        r_filtered = r_from.filter(query_params["where"])
        r_select = r_filtered.select(query_params["select"])
        return r_select

def main():
    """This is a demo application to test the JSONDB class. It accepts a JSON document as input and enables to query it using a SQL-like query language.

    e.g.
        $ sqlonjson.py -f myjson.json -q "SELECT * FROM myjson WHERE ..id==1"
    """
    logging.basicConfig(level=logging.DEBUG)
    parser = argparse.ArgumentParser(allow_abbrev=False, description=main.__doc__, formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument(help="The json document to query", dest="jsonfile")
    parser.add_argument("-f", "--from", help="The from clause where execute the query", dest="q_from", default="$")
    parser.add_argument("-w", "--where", help="The where clause where execute the query", dest="q_where", default="$")
    parser.add_argument("-s", "--select", help="The select clause where execute the query", dest="q_select", default="$")
    parser.add_argument("-v", "--version", help="Show the version of the program", action="version", version=VERSION)
    parser.add_argument("-q", "--query", help="The query to execute", dest="query", default=None)

    args = parser.parse_args()
    if args.jsonfile == "-":
        jsonfile = sys.stdin
    else:
        if not os.path.exists(args.jsonfile):
            print("File not found: %s" % args.jsonfile)
            return 1
        jsonfile = open(args.jsonfile)

    jsondb = JSONDB(jsonfile.read())
    if args.query is not None:
        r = jsondb.query(args.query)
    else:
        r = jsondb.query(f"select {args.q_select} from {args.q_from} where {args.q_where}")
    print(json.dumps(list(r), indent=4))

if __name__ == "__main__":
    main()