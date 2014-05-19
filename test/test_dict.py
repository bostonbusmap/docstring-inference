def f(x, y):
    """
    :type x: float
    :type y: float
    :rtype: dict[string, int]
    """
    return {"x": x, "y": y}

x = f(3, 4)
print(x.values())

# This should error
x.missing()
