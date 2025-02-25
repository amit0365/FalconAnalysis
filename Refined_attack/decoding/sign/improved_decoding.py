import numpy as np
from numpy import linalg, float64
from utils import *
from scipy.stats import rankdata

import sys
sys.path.insert(0, '../falcon')
import falcon
from ntrugen import ntru_solve

nb_keys = 40
steps = 15

max_samples = 50000
min_samples = 12500
step_samples = 2500

nb_sigs = [i for i in range(min_samples, max_samples, step_samples)]

pro_array = np.zeros((nb_keys, len(nb_sigs)), dtype=float64)

success_array = np.zeros((nb_keys, len(nb_sigs)), dtype=np.int64)

success_sum = np.zeros(len(nb_sigs), dtype=np.int64)

real_keys = np.load("results_process/real_keys.npy")
print(real_keys.shape)
print(type(real_keys[0][0]))
pks = np.load("results_process/pks.npy")
print(pks.shape)
print(type(pks[0][0]))
recovered_keys = np.load("results_process/recovered_keys.npy")
print(recovered_keys.shape)
print(type(recovered_keys[0][0][0]))

exhaustive_list = []

for nb_key in range(nb_keys):
    print("\n\n\n\n")
    print("nb_key: ", nb_key)
    basis = real_keys[nb_key]
    f = neg((basis[N:]).tolist())
    print("f: ", f)
    g = (basis[:N]).tolist()
    print("g: ", g)
    F, G = ntru_solve(f, g)
    print("F: ", F)
    print("G: ", G)
    h = pks[nb_key]
    print("h: ", h)
    ZZ_q = IntegerModRing(12289)
    A, B = MakeMatrix(f, g, F, G, h)
    H = anti_cir(h)
    Ht_q = matrix(ZZ_q, H.transpose())
    for idx, item in enumerate(nb_sigs):
        counter_success = 0

        print("Sample size: ", item)

        b = recovered_keys[nb_key][idx]
        g_prime = vector(ZZ_q, [round(b[i]) for i in range(N)])
        f_prime = vector(ZZ_q, [round(-b[i]) for i in range(N, 2 * N)])

        rounded_b = [int(round(b[i])) for i in range(2 * N)]
        n_incorrect = 1024
        n_inc = 0
        for i in range(2*N):
            if basis[i] != rounded_b[i]:
                n_inc += 1
        n_incorrect = min([n_incorrect, n_inc])

        print("The number of used signatures: ", item)
        print("The number of incorrect coefficients in recovered key: ", n_incorrect)

        # ========================================

        print("\nRunning the improved decoding technique...\n")

        # Estimate std using curve fitting
        sigma = 41.44998235 / sqrt(item)

        # x = b' - rounded b'
        x = [(b[i] - round(b[i])) for i in range(N*2)]

        # coefficients of probability of being correctly rounded
        p = [(prob(sigma, x[i])) for i in range(N*2)]

        rank = rankdata(p)
        rank = [int(rank[i])-1 for i in range(len(rank))]

        g0_index = []
        ge_index = []
        f0_index = []
        fe_index = []

        for i in range(N):
            if rank[i] >= N:
                g0_index.append(i)
            else:
                ge_index.append(i)
        for i in range(N, 2*N):
            if rank[i] >= N:
                f0_index.append(i-N)
            else:
                fe_index.append(i-N)
        print("g0: ", len(g0_index), "  ge: ", len(ge_index), "  f0: ", len(f0_index), "  fe: ", len(fe_index))

        sorted_prob = np.sort(p)
        prod = 1
        for i in range(N, N*2):
            prod = prod * sorted_prob[i]

        pro_array[nb_key][idx] = prod

        print("\nEstimated success probability: ", prod)
        print("\nEstimated number of correctly rounded coefficients: ", sum(sorted_prob))

        diff = np.zeros(2*N, dtype=float64)

        for i in range(2*N):
            diff[i] = round(b[i]) - basis[i]

        diff_norm = linalg.norm(diff) ** 2
        print("The l2-norm of diff between recovered and real one: ", diff_norm)

        if linalg.norm(diff) ** 2 < 7:
            counter_success += 1
            exhaustive_list.append(item)
            print("keys: ", nb_key, "sample size: ", item)
            print("Exhaustive search can be used to do key recovery attack.")
            success_array[nb_key][idx] = counter_success
            print("counter_success: ", counter_success)
            continue

        if len(g0_index) + len(f0_index) < len(ge_index) + len(fe_index):
            print("The rearrange matrix is not a square matrix. ")
            success_array[nb_key][idx] = counter_success
            print("counter_success: ", counter_success)
            continue

        tmp = matrix(ZZ, len(fe_index), N)
        for i in range(len(fe_index)):
            for j in range(N):
                tmp[i, j] = H[fe_index[i], j]

        # print(tmp,"last")

        tmp = tmp.transpose()
        M = []

        for i in range(len(g0_index)):
            M.append(tmp[g0_index[i]])

        M = matrix(ZZ_q, M[0:len(fe_index)][0:len(fe_index)])

        v = vector(ZZ_q, g_prime - Ht_q * f_prime)

        tmp = []
        for i in range(len(g0_index)):
            tmp.append(int(v[g0_index[i]]))

        v = vector(ZZ_q, tmp[0:len(fe_index)])

        if not M.is_invertible():
            print("Input matrix must be non-singular")
            success_array[nb_key][idx] = counter_success
            print("counter_success: ", counter_success)
            continue

        tmp = M.inverse() * v

        e_f = zero_vector(ZZ_q, N)

        for i in range(len(fe_index)):
            e_f[fe_index[i]] = int(tmp[i])

        recovered_f = f_prime + e_f

        e_g = (g_prime - Ht_q * f_prime) - Ht_q * e_f

        recovered_g = - g_prime + e_g

        # Check
        error = []
        basis_q = vector(ZZ_q, [basis[i] for i in range(2 * N)])
        print(basis_q)

        incorrect_f = 0
        incorrect_g = 0
        for i in range(N):
            if recovered_g[i] != basis_q[i]:
                incorrect_g += 1
            if recovered_f[i] != basis_q[i + N]:
                incorrect_f += 1
        error.append(incorrect_g + incorrect_f)

        basis_q_minus = vector(ZZ_q, [-basis[i] for i in range(2*N)])
        print(basis_q_minus)
        incorrect_f = 0
        incorrect_g = 0
        for i in range(N):
            if recovered_g[i] != basis_q_minus[i]:
                incorrect_g += 1
            if recovered_f[i] != basis_q_minus[i+N]:
                incorrect_f += 1
        error.append(incorrect_g+incorrect_f)
        # print(error)
        print("============Result============")
        print("min number of incorrect:  ", min(error))
        if min(error) != 0:
            print("Fail")
        else:
            counter_success += 1
            print("Success")
        print("===============================")

        success_array[nb_key][idx] = counter_success
        print("counter_success: ", counter_success)
    print(nb_key, "-th row of success: ", success_array[nb_key])
for nb_key in range(nb_keys):
    print(success_array[nb_key].tolist())
for idx in range(len(nb_sigs)):
    sum_col = 0
    for nb_key in range(nb_keys):
        sum_col += success_array[nb_key][idx]
    success_sum[idx] = sum_col

print("Sum for success array: ", success_sum)

print("Min value of signatures used to perform simple exhaustive search: ", min(exhaustive_list))

np.save("results_process/pro_array.npy", pro_array)
np.save("results_process/success_array", success_array)
