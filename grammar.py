"""Foo                # Class Foo visible in the current scope
x.y.Bar            # Class Bar from x.y module
Foo | Bar          # Foo or Bar
(Foo, Bar)         # Tuple of Foo and Bar
list[Foo]          # List of Foo elements
dict[Foo, Bar]     # Dict from Foo to Bar
T                  # Generic type (T-Z are reserved for generics)
T <= Foo           # Generic type with upper bound Foo
Foo[T]             # Foo parameterized with T
(Foo, Bar) -> Baz  # Function of Foo and Bar that returns Baz
"""

import parsley
from astroid import nodes

def parse_node(text):
    if text == "None":
        clazz = "NoneType"
    else:
        clazz = text

    return nodes.Class(clazz, 'docstring').instanciate_class()

def as_class(string):
    last_dot_index = string.rfind(".")
    if last_dot_index != -1:
        module_name = string[:last_dot_index]
        class_name = string[last_dot_index + 1:]
    else:
        module_name = ""
        class_name = string
    
    clazz = nodes.Class(class_name, 'docstring')
    module = nodes.Module(module_name, 'docstring')
    clazz.parent = module
    return clazz.instanciate_class()

class Class:
    def __init__(self, name):
        self.name = name

    def __str__(self):
        return self.name

class Function:
    def __init__(self, input, output):
        self.input = input
        self.output = output

    def __str__(self):
        return str(self.input) + " -> " + str(self.output)

class Type:
    def __init__(self, type):
        self.type = type

    def __str__(self):
        return self.type

class List:
    def __init__(self, type):
        self.type = type

    def __str__(self):
        return "list[" + str(self.type) + "]"

class StringType:
    def __init__(self, type):
        self.type = type

    def __str__(self):
        # TODO
        return self.type

class Tuple:
    def __init__(self, items):
        self.items = items

    def __str__(self):
        return "(" + ", ".join(str(s) for s in self.items) + ")"

class Dict:
    def __init__(self, first, second):
        self.first = first
        self.second = second

    def __str__(self):
        return "dict[" + str(self.first) + ", " + str(self.second) + "]"

class Or:
    def __init__(self, items):
        self.items = items

    def __str__(self):
        return " | ".join(str(s) for s in self.items)

class BoundedType:
    def __init__(self, type, bound):
        self.type = type
        self.bound = bound

    def __str__(self):
        return str(self.type) + " <= " + str(self.bound)

class ParameterizedType:
    def __init__(self, type, parameters):
        self.type = type
        self.parameters = parameters

    def __str__(self):
        return str(self.type) + "[" + ", ".join(str(s) for s in self.parameters) + "]"

def make_grammar():
    # TODO: tuple with one value
    # TODO: make sense of the return values
    x = parsley.makeGrammar("""
clazzChar = letterOrDigit | '.'
clazz = <clazzChar+>:x -> Class(x)

# a type or a class
item = (:x ?(x in 'TUVWXYZ') -> Type(x)
 | 'None' -> Type('NoneType')
 | 'unknown' -> Type('unknown')
 | ('string' | 'bytestring' | 'bytes' | 'unicode'):x -> StringType(x)
 | clazz:x -> x)

commaRule = ',' ws rule:rule ws -> rule

orRule = '|' ws rule:rule ws -> rule

rule = ('(' ws rule:firstRule ws commaRule*:ruleList ')' -> Tuple([firstRule] + ruleList)
  | 'list[' ws rule:x ws ']' -> List(x)
  | 'dict[' ws rule:first ws ',' ws rule:second ws ']' -> Dict(first, second)
  | (item:one
     (ws orRule+:two -> Or([one] + two)
      | ws '<=' ws rule:two -> BoundedType(one, two)
      | ws '[' ws rule:two ws commaRule*:ruleList ']' -> ParameterizedType(one, [two] + ruleList)
      | -> one)))

expr = rule:arg (ws '->' ws rule:ret -> Function(arg, ret)
  | -> arg)
    """, {"Class": Class,
          "Type": Type,
          "BoundedType": BoundedType,
          "Tuple" : Tuple,
          "StringType" : StringType,
          "List" : List,
          "Dict" : Dict,
          "Function" : Function,
          "ParameterizedType" : ParameterizedType,
          "Or" : Or})
    return x
    

if __name__ == "__main__":
    x = make_grammar()
    print(x("None").expr())
    print(x("Foo | Bar").expr())
    print(x("Foo").expr())
    print(x("x.y.Bar").expr())
    print(x("(Foo, Bar)").expr())
    print(x("list[Foo]").expr())
    print(x("dict[Foo, Bar]").expr())
    print(x("T").expr())
    print(x("T <= Foo").expr())
    print(x("Foo[T]").expr())
    print(x("(Foo, Bar) -> Baz").expr())
    print(x("Foo | Bar | Baaz").expr())
