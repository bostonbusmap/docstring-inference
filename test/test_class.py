from b import A
import c.f

def f(x, y):
    """
    :type x: int
    :type y: int
    :rtype: c.f.D
"""
    # TODO: A should collide with c.f.D()
    return c.f.D()

# TODO: the string arguments here should collide with the 'int' in the docstring
# and produce an error.
x = f("", "")

# should work fine
x.b()

# should report an error
x.c()
