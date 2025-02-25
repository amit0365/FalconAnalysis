

def make_indices(n):
    indices = [i for i in range(n-1, -1, -1)]
    indices = permute(indices)
    indices = indices[n//2:] + indices[:n//2]
    f0, f1 = split(indices)
    return f0+f1


def back_first_row(a, nb):
    assert nb >= 0
    a_len = len(a)

    for idx in range(nb):
        a = a[1:len(a)] + ([-a[0]])

    assert len(a) == a_len

    return a


def permute(f):
    n = len(f)
    f0 = [f[2 * i + 0] for i in range(n // 2)]
    f1 = [f[2 * i + 1] for i in range(n // 2)]
    if n == 4:
        return(f0+f1)
    else:
        f0 = permute(f0)
        f1 = permute(f1)
        return f0+f1

def split(f):
    n = len(f)
    f0 = [f[2 * i + 0] for i in range(n // 2)]
    f1 = [f[2 * i + 1] for i in range(n // 2)]
    return(f0,f1)