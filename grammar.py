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
from astroid import nodes, UseInferenceDefault, MANAGER

def parse_node(node, context, text):
    grammar = make_grammar()(text)

    tree = grammar.expr()
    infer_node = tree.infer(node)
    if type(infer_node) == list:
        return iter(infer_node)
    else:
        return iter([infer_node])

def instantiate_class(node, class_name, count=10):
    if count == 0:
        raise UseInferenceDefault()
    if isinstance(node, nodes.From):
        from_module = node.do_import_module(node.modname)
        scope, items = from_module.scope().scope_lookup(from_module.scope(), class_name)
        if items:
            return instantiate_class(items[0], class_name, count - 1)
        raise UseInferenceDefault()
    else:
        return node.instanciate_class()

class Class:
    def __init__(self, name):
        self.name = name

    def __str__(self):
        return self.name

    def infer(self, node):
        # TODO: I don't really know if module handling is correct here
        # but it also looks like astroid doesn't fully know about imported
        
        string = self.name
        last_dot_index = string.rfind(".")
        if last_dot_index != -1:
            module_name = string[:last_dot_index]
            class_name = string[last_dot_index + 1:]
        else:
            module_name = ""
            class_name = string
        scope, items = node.scope().scope_lookup(node.scope(), string)

        if items:
            return instantiate_class(items[0], class_name)

        # TODO: I probably shouldn't be using the cache this way
        if module_name in MANAGER.astroid_cache:
            module = MANAGER.astroid_cache[module_name]
            return instantiate_class(module, class_name)
        
        raise UseInferenceDefault()


class Function:
    def __init__(self, input, output):
        self.input = input
        self.output = output

    def __str__(self):
        return str(self.input) + " -> " + str(self.output)

    def infer(self, node):
        lam = nodes.Lambda()
        # not sure why lam.args starts out as a list()
        lam.args = nodes.Arguments()
        lam.args.args = []
        lam.args.defaults = []
        lam.args.kwonlyargs = []
        lam.args.kw_defaults = []
        lam.body = self.output.infer(node)

        lam.doc = ""
        if isinstance(self.input, Tuple):
            for item in self.input.items:
                assname = nodes.AssName()
                assname.name = "__unused"
                lam.args.args.append(assname)
                lam.args.defaults.append(item.infer(node))
        else:
            assname = nodes.AssName()
            assname.name = "__unused"
            lam.args.args.append(assname)
            lam.args.defaults.append(self.input.infer(node))

        return lam
class Type:
    def __init__(self, type):
        self.type = type

    def __str__(self):
        return self.type

    def infer(self, node):
        # TODO: need a fancier type inference system
        raise UseInferenceDefault()

class List:
    def __init__(self, type):
        self.type = type

    def __str__(self):
        return "list[" + str(self.type) + "]"

    def infer(self, node):
        
        return nodes.List()

class StringType:
    def __init__(self, type):
        self.type = type

    def __str__(self):
        # TODO: differentiate types based on python 2/3
        return self.type

    def infer(self, node):
        import sys
        if sys.version_info() >= (3,0):
            if self.type == "string" or self.type == "bytestring":
                return Or([Class("str"), Class("unicode")]).infer(node)
            elif self.type == "bytes":
                return Class("str").infer(node)
            elif self.type == "unicode":
                return Class("unicode").infer(node)
            else:
                # Shouldn't happen, all cases should have been handled
                raise Exception("Inference error")
        else:
            if self.type == "string":
                return Class("str").infer(node)
            elif self.type == "bytestring" or self.type == "bytes":
                return Class("bytes").infer(node)
            elif self.type == "unicode":
                return Class("str").infer(node)
            else:
                # Shouldn't happen, all cases should have been handled
                raise Exception("Inference error")

class Tuple:
    def __init__(self, items):
        self.items = items

    def __str__(self):
        return "(" + ", ".join(str(s) for s in self.items) + ")"

    def infer(self, node):
        elts = [item.infer(node) for item in self.items]
        return nodes.Tuple(elts=elts)

class Dict:
    def __init__(self, first, second):
        self.first = first
        self.second = second

    def __str__(self):
        return "dict[" + str(self.first) + ", " + str(self.second) + "]"

    def infer(self, node):
        return nodes.Dict()

class Or:
    def __init__(self, items):
        self.items = items

    def __str__(self):
        return " | ".join(str(s) for s in self.items)

    def infer(self, node):
        # TODO: Currently this is more of an And than an Or
        return [item.infer(node) for item in self.items]

class BoundedType:
    def __init__(self, type, bound):
        self.type = type
        self.bound = bound

    def __str__(self):
        return str(self.type) + " <= " + str(self.bound)

    def infer(self, node):
        # TODO: figure out how to implement this
        return Type(self.type).infer(node)

class ParameterizedType:
    def __init__(self, type, parameters):
        self.type = type
        self.parameters = parameters

    def __str__(self):
        return str(self.type) + "[" + ", ".join(str(s) for s in self.parameters) + "]"

    def infer(self, node):
        # TODO: figure out how to implement this
        return Type(self.type).infer(node)

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
