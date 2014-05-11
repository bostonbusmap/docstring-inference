from astroid import MANAGER, UseInferenceDefault, inference_tip, YES, InferenceError, nodes
from astroid.builder import AstroidBuilder

import xml.etree.ElementTree as etree
from docutils.core import publish_doctree

def register(linter):
    pass

def infer_from_docstring(node, context=None):
    
    docstring = node.getattr('__doc__')[0].value
    if docstring is None:
        return
    
    doctree = etree.fromstring(publish_doctree(docstring).asdom().toxml())
    field_lists = doctree.findall(".//field_list")
    fields = [f for field_list in field_lists
              for f in field_list.findall('field')]
    if fields:
        for field in fields:
            raise Exception(publish_doctree(docstring).asdom().toxml())
            field_name = field.findall("field_name")[0].text
            field_body = field.findall("field_body")[0].findall("paragraph")[0].text
            print "XXX: %s, YYY: %s" % (field_name, field_body)
    # TODO: parse each field in fields to types, then
    # return iter([node]) where node is like the input but
    # altered somehow to provide inference information

MANAGER.register_transform(nodes.Function, infer_from_docstring)

