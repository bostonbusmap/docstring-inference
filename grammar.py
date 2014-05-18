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

def as_type(x):
    return x

def as_tuple(one, two):
    return (one, two)

def as_string_type(x):
    # TODO: make sense of this
    return x

def make_grammar():
    # TODO: tuple with one value
    # TODO: make sense of the return values
    x = parsley.makeGrammar("""
clazzChar = letterOrDigit | '.'
clazz = <clazzChar+>:x -> x

item = (:x ?(x in 'TUVWXYZ') -> as_type(x)
 | 'None' -> as_type('NoneType')
 | 'unknown' -> as_type('unknown')
 | ('string' | 'bytestring' | 'bytes' | 'unicode'):x -> as_string_type(x)
 | clazz:x -> x)

commaRule = ',' ws rule:rule ws -> rule

rule = ('(' ws rule:firstRule ws commaRule*:ruleList ')' -> [firstRule] + ruleList
  | 'list[' ws item:x ws ']' -> x
  | 'dict[' ws item:first ws ',' ws item:second ws ']' -> (first, second)
  | (item:one
     (ws '|' ws rule:two -> as_tuple(as_class(one), two)
      | ws '<=' ws item:two -> as_tuple(as_class(one), two)
      | ws '[' ws item:two ws ']' -> as_tuple(as_class(one), two)
      | -> as_class(one))))

expr = rule:arg (ws '->' ws rule:ret -> (arg, ret)
  | -> arg)
    """, {"as_class": as_class,
          "as_tuple": as_tuple,
          "as_type": as_type})
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
