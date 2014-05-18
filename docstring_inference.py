from astroid import MANAGER, UseInferenceDefault, inference_tip, YES, InferenceError, nodes
from astroid.builder import AstroidBuilder

import xml.etree.ElementTree as etree
from docutils.core import publish_doctree
from grammar import parse_node

def register(linter):
    pass

def infer_rtype(node, context=None):
    for infer in node.func.infer(context.clone()):
        docstring = infer.doc
        if docstring is None:
            break
        
    
        doctree = etree.fromstring(publish_doctree(docstring).asdom().toxml())
        field_lists = doctree.findall(".//field_list")
        fields = [f for field_list in field_lists
                  for f in field_list.findall('field')]
        if fields:
            for field in fields:
                field_names = field.findall("field_name")
                field_bodies = field.findall("field_body")
                if not field_names:
                    break
                if not field_bodies:
                    break
                field_name = field_names[0].text
                paragraphs = field_bodies[0].findall("paragraph")
                if not paragraphs:
                    break
                field_body = paragraphs[0].text
            
                if field_name.startswith("rtype"):
                    ret_node = parse_node(node, context, field_body)
                    return iter([ret_node])
    # found nothing
    raise UseInferenceDefault()

def infer_arg(node, context=None):
    if not isinstance(node.parent, nodes.Arguments):
        raise UseInferenceDefault()
    if not isinstance(node.parent.parent, nodes.Function):
        raise UseInferenceDefault()

    func = node.parent.parent
    docstring = func.doc
    if docstring is None:
        raise UseInferenceDefault()

    
    doctree = etree.fromstring(publish_doctree(docstring).asdom().toxml())
    field_lists = doctree.findall(".//field_list")
    fields = [f for field_list in field_lists
              for f in field_list.findall('field')]

    if fields:
        for field in fields:
            field_name = field.findall("field_name")[0].text
            field_body = field.findall("field_body")[0].findall("paragraph")[0].text
            
            if field_name == "type %s" % node.name:
                ret_node = parse_node(node, context, field_body)
                return iter([ret_node])
            
    raise UseInferenceDefault()
        
        
MANAGER.register_transform(nodes.CallFunc, inference_tip(infer_rtype))
MANAGER.register_transform(nodes.AssName, inference_tip(infer_arg))

