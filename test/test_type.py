class A:
    def x(self):
        pass

def f(x):
    """
    :type x: list[T]
    :rtype: T
    """
    return x[0]

# this should fail since A doesn't have 'y'
f([A()]).y()
