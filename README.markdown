# About

docstring-inference is a pylint-brain plugin to use type information stored
in docstrings for type inference. It aims to support type information within [python-skeletons](https://github.com/JetBrains/python-skeletons).

# Install

Currently this is just a few files which you can drop in astroid/brain/. There
are instructions at [pylint-brain](https://bitbucket.org/logilab/pylint-brain) to set up your own development environment.

# Goals
 * Use declared types for inference
 * Warn if declared types confict with inferred types
 * Integrate python-skeletons (maybe another plugin)