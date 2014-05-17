from astroid import MANAGER, UseInferenceDefault, inference_tip, YES, InferenceError, nodes
from astroid.builder import AstroidBuilder

import xml.etree.ElementTree as etree
from docutils.core import publish_doctree

def register(linter):
    pass

def parse_node(text):
    if text == "None":
        clazz = "NoneType"
    else:
        clazz = text

    return nodes.Class(clazz, 'docstring').instanciate_class()

def infer_from_docstring(node, context=None):
    for infer in node.func.infer(context):
        
        docstring = infer.doc
        if docstring is None:
            return
        
    
        doctree = etree.fromstring(publish_doctree(docstring).asdom().toxml())
        field_lists = doctree.findall(".//field_list")
        fields = [f for field_list in field_lists
                  for f in field_list.findall('field')]

        if fields:
            for field in fields:
                field_name = field.findall("field_name")[0].text
                field_body = field.findall("field_body")[0].findall("paragraph")[0].text
            
                if field_name.startswith("rtype"):
                    name = nodes.Name()
                    name.name = field_body
                    ret_node = parse_node(field_body)
                    return iter([ret_node])
        # found nothing
        
def infer_enum(node, context=None):
    class_node = nodes.Class("ABC", 'docstring')
    return iter([class_node.instanciate_class()])


def wrap_exception(node, context=None):
    try:
        return infer_from_docstring(node, context)
    except (InferenceError, UseInferenceDefault):
        return None

MANAGER.register_transform(nodes.CallFunc, inference_tip(infer_from_docstring))

