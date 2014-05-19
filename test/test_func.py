def make_adder(g):
    """
    :type g: int 
    :rtype: int -> int
    """
    def adder(x):
        return g+x
    return adder

m = make_adder(5)

# should print 11
print(m(6))

# should error saying there is no 'g' method on the int
m(6).g()

# should error because of too many arguments
m(7,9)
