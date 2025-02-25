
def neg(f):
    """Negation of a polynomials (any representation)."""
    deg = len(f)
    return [- f[i] for i in range(deg)]
