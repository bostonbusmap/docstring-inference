from astroid import MANAGER, UseInferenceDefault, inference_tip, YES, InferenceError, nodes
from astroid.builder import AstroidBuilder

import py2stdlib

def register(linter):
    pass

SKELETONS_DIR = "/home/schneg/Projects/python_skeletons"

MODULES_TO_PATH = {}
TRANSFORMS = {}
def import_a_module(module_name):
    def import_this_module(module):
        path = MODULES_TO_PATH[module.name]
        with open(path) as f:
            fake = AstroidBuilder(MANAGER).string_build(f.read())

            for k, items in fake.locals.items():
                for item in items:
                    if type(item) == nodes.Function:
                        if k in module.locals:
                            if type(module.locals[k]) == nodes.Function:
                                module.locals[k].doc = item.doc
                            # else type(module.locals[k]) == nodes.Function
                        else:
                            module.set_local(k, nodes.Function(k, item.doc))

    return import_this_module



import os
def import_skeletons_module():
    for dirpath, dirnames, filenames in os.walk(SKELETONS_DIR):
        for filename in filenames:
            if filename.endswith(".py"):
                if not dirpath.startswith(SKELETONS_DIR):
                    raise Exception("Expected root to start with python skeletons directory")

                # TODO: make this better
                path = dirpath[len(SKELETONS_DIR) + 1:].replace("/", ".")
                if filename.endswith("__init__.py"):
                    module_name = path
                else:
                    module_name = path + "." + filename[:-len(".py")]
                if module_name.startswith("."):
                    module_name = module_name[1:]
                if module_name != "":
                    MODULES_TO_PATH[module_name] = os.path.join(dirpath, filename)
                    TRANSFORMS[module_name] = import_a_module(module_name)
import_skeletons_module()
def transform(module):
    try:
        tr = TRANSFORMS[module.name]
    except KeyError:
        pass
    else:
        tr(module)
        
MANAGER.register_transform(nodes.Module, transform)


