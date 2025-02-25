from sage.all import *

N = 512
q = 12289

# rho/rho
def rho_x_z(sigma,x):
    sum = 0.0
    for k in range(-50,50):
        sum += exp(-(x+k)**2 / (2 * sigma ** 2))
    return sum

def rho(sigma,x):
    return exp(-(x)**2 / (2 * sigma ** 2))

def prob(sigma,x):
    return rho(sigma,x) / rho_x_z(sigma,x)

# KeyGen
def MakeMatrix(f,g,F,G,h):
    A = matrix(ZZ,2*N)
    B = matrix(ZZ,2*N)
    for i in range(N*2):
        if i < N :
            for j in range(i,N):
                B[i,j] = g[j-i]
                B[i,j+N] = -f[j-i]
                A[i,j+N] = h[j-i]
            for j in range(i):
                k = (j-i+N)
                B[i,j] = -g[k]
                B[i,j+N] = f[k]
                A[i,j+N] = -h[k]
            A[i,i] = 1
        else:
            i_n = i-N
            for j in range(i_n,N):
                B[i,j] = G[j-i_n]
                B[i,j+N] = -F[j-i_n]
            for j in range(i_n):
                k = (j-i+2*N)
                B[i,j] = -G[k]
                B[i,j+N] = F[k]
            A[i,i] = 12289
    return A,B

def CovMatrix(Cov):
    mtx = matrix(RR,2*N)
    for i in range(N):
        for j in range(N):
            mtx[i,j] = Cov[0][(i-j)%N]
            mtx[i,j+N] = Cov[1][(i-j)%N]
            mtx[i+N,j] = Cov[2][(i-j)%N]
            mtx[i+N,j+N] = Cov[3][(i-j)%N]
    return mtx


def anti_cir(poly):
    mtx = matrix(ZZ,len(poly))

    for j in range(len(poly)):
        mtx[0,j] = poly[j]

    for i in range(1,len(poly)) :
        for j in range(len(poly)):
            if j - 1 >= 0:
                mtx[i,j] = mtx[i-1,j-1]
            else:
                mtx[i,j] = - mtx[i-1,len(poly)-1]

    return mtx

import h5py


def shift(f, i):
    if i == 0:
        return f
    elif i < 0:
        new = f[-i:] + [-e for e in f[:-i]]
    else:
        new = [-e for e in f[-i:]] + f[:-i]
    return new


def F_Matrix(f):
    n = len(f)
    if n == 2:
        F = [[f[0], f[1]], [-f[1], f[0]]]
        return F
    else:
        f0 = [f[2 * i + 0] for i in range(n // 2)]
        f1 = [f[2 * i + 1] for i in range(n // 2)]
        F00 = F_Matrix(f0)
        F01 = F_Matrix(f1)
        F10 = F_Matrix(shift(f1, 1))
        F11 = F_Matrix(f0)

        F = [[c for c in F00[i]] + [c for c in F01[i]] for i in range(n//2)] + [[c for c in F10[i]] + [c for c in F11[i]] for i in range(n//2)]
        return F


def conjugate(f):
    return [f[0]] + [-f[i] for i in range(len(f) - 1, 0, -1)]


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


def neg(f):
    """Negation of a polynomials (any representation)."""
    deg = len(f)
    return [- f[i] for i in range(deg)]


def print_info(data_file):
    file = h5py.File(data_file, 'r')
    test_sets = [elem for elem in file]
    # print(len(test_sets))
    sigs = list(file[test_sets[0]].keys())
    # print("sigs: ", sigs)
    # print(len(sigs))
    print("Number of sets in file:", len(test_sets))
    print("Number of signatures in each set:", [len(file[elem]) for elem in test_sets])
    print("Dimension:", [file[elem].attrs["n"] for elem in test_sets])
    print("Data type:", type(file[test_sets[0]][sigs[0]][:, ]), type(file[test_sets[0]][sigs[0]][:, ][0]))

    file.close()