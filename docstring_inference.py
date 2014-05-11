from astroid import MANAGER, UseInferenceDefault, inference_tip, YES, InferenceError, nodes
from astroid.builder import AstroidBuilder

def infer_from_docstring(node, context=None):
    
    def infer_first(node):
        try:
            value = node.infer().next()
            if value is YES:
                raise UseInferenceDefault()
            else:
                return value
        except StopIteration:
            raise InferenceError()


MANAGER.register_transform(nodes.CallFunc, inference_tip(infer_from_docstring))

