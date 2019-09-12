"""Interpret a file"""

import re

class Interpreter:
    """Main interpreter"""
    def __init__(self, file):
        self.content = self.read(file)

        self.in_if = False
        self._last_condition = None

        self.variables = {}

    def read(self, file):
        """Read a file"""
        with open(file, "r") as to_read:
            return to_read.read()

    def is_variable(self, item):
        """See if an item is a variable"""
        if item.startswith("'") and item.endswith("'") or item.startswith('"') \
                                and item.endswith('"') or item.isdigit() \
                                or item in ["True", "False"] or item.startswith("'") \
                                or item.startswith('"') or item.endswith("'") \
                                or item.endswith('"'):
            return False

        if item in self.variables.keys():
            return True

        raise RuntimeError("%s is not defined" % item)

    def get_indent(self, line):
        """Get the indent of a line"""
        comp = re.compile(r"^ *")

        return len(comp.findall(line)[0])

    def output(self, line):
        """Output function"""
        to_send = []

        for word in ' '.join(line.split("OUTPUT")[1:]).split(" "):
            if word != "" and self.is_variable(word):
                var = list(self.variables[word])

                if var[0] in ('"', "'"):
                    var[0] = ""
                if var[-1] in ('"', "'"):
                    var[-1] = ""

                to_send += f"{''.join(var).strip()} "
            else:
                split = list(word)

                if split:
                    if split[0] in ('"', "'"):
                        split[0] = ""
                    if split[-1] in ('"', "'"):
                        split[-1] = ""

                    to_send += f"{''.join(split).strip()} "
                else:
                    to_send += f"{word} "

        print(''.join(to_send).strip())

    def set_variable(self, line):
        """Set a variable"""
        if list(line.split("<-")[1].strip())[0].isdigit():
            self.variables[line.split("<-")[0].strip()] = str(eval(line.split("<-")[1].strip()))
        else:
            self.variables[line.split("<-")[0].strip()] = line.split("<-")[1].strip()

    def conditional(self, line):
        """IF statements"""
        condition = line.split(" ")[2] if len(line.split(" ")) > 2 else None
        condition_one = line.split(" ")[1]
        condition_two = ' '.join(line.split(" ")[3:]) if len(line.split(" ")) > 2 else None

        if self.is_variable(condition_one):
            condition_one = self.variables[condition_one]
            
        if condition_two:
            if self.is_variable(condition_two):
                condition_two = self.variables[condition_two]

        self._last_condition = eval(f"{condition_one}{condition if condition else '=='}{condition_two if condition_two else 'True'}")

        if self._last_condition:
            self.in_if = True

    def is_else(self, line):
        """ELSE statements"""
        if line.strip() in self.variables.keys():
            raise SyntaxError("Invalid Syntax, < '%s' >" % (line))

        if not self._last_condition:
            self.determine(line.strip())

    def determine(self, line):
        """Determine a line type"""
        if line.split(" ")[1] == "<-":
            self.set_variable(line)

        if line.startswith("OUTPUT"):
            self.output(line)

        if line.startswith("IF"):
            self.conditional(line)

    def compile(self):
        """Interpreter"""
        if not self.content:
            return "No content"

        for i, line in enumerate(self.content.splitlines()):
            if len(line.split(" ")) == 1 and line == "" or line.startswith("//"):
                continue

            try:
                if self.content.splitlines()[i+1].strip() in self.variables.keys():
                    raise SyntaxError("Invalid Syntax, <line %s>" % i)
            except IndexError:
                pass

            if self.in_if and self.get_indent(line) == 4:
                self.in_if = False

                lines = []
                for item in self.content.splitlines()[i:]:
                    if self.get_indent(item) == 4:
                        lines.append(item.strip())
                    else:
                        break
                
                for item in lines:
                    self.determine(item)

                continue

            if not line.startswith("ELSE") and line.split(" ")[1] == "<-":
                self.set_variable(line)

            if line.startswith("OUTPUT"):
                self.output(line)

            if line.startswith("IF"):
                self.conditional(line)

            if line.startswith("ELSE"):
                lines = [line.strip() for line in self.content.splitlines()[i:] \
                        if self.get_indent(line) == 4]

                for item in lines:
                    self.is_else(item)

        return 0
