"""Command line"""

import sys

from interpreter import Interpreter as parser

def execute():
    """Execute the interpreter"""
    args = sys.argv

    if not args[1:]:
        raise ValueError("Missing file name.")

    interpreter = parser(file=args[1]) # Execute the file

    return interpreter.compile()

if __name__ == "__main__":
    print(execute())
