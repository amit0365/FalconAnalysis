import ast
from utils import *
from numpy import zeros, int64, cov, linalg, array, save
from numpy import dot, float64, set_printoptions, inf
from scipy import integrate
import os
import math
import pandas as pd
import argparse
set_printoptions(threshold=inf)

sigmas = {2: 144.81253976308423, 4: 146.83798833523608,
          8: 148.83587593064718, 16: 151.78340713845503,
          32: 154.6747794602761, 64: 157.51308555044122,
          128: 160.30114421975344, 256: 163.04153322607107,
          512: 165.7366171829776, 1024: 168.38857144654395}

parser = argparse.ArgumentParser(description = 'analyze')
parser.add_argument('--under', type = int, default = 0)
parser.add_argument('--top', type = int, default = 0)
parser.add_argument('--step', type = int, default = 0)
parser.add_argument('--file', type = int, default = 0)
args = parser.parse_args()

n_files = args.file
min_samples = args.under
max_samples = args.top
step_samples = args.step

n = 512
Q = 12289
msg = b'test'
sigma_square = sigmas[n] ** 2
bound = math.sqrt(n)
norm_th = 1.17*math.sqrt(Q)

def f1(x):
    return (x ** 2) * math.exp(-(x ** 2) / (2 * sigma_square))

def f2(x):
    return math.exp(-(x ** 2) / (2 * sigma_square))

def f3(x):
    return x * math.exp(-(x ** 2) / (2 * sigma_square))

data_path =  r'../data/sig_gen/key_{0}/'.format(n_files)
results_path = r'./results_both_{0}_{1}_{2}_{3}/key_{4}/'.format(n, min_samples, max_samples, step_samples, n_files)

if not os.path.exists(results_path):
    os.makedirs(results_path)

norm_max = 130
norm_min = 120
norm_b0_sqaure = zeros(norm_max**2 - norm_min**2, dtype=float64)
for i in range(norm_max**2 - norm_min**2):
    norm_b0_sqaure[i] = math.sqrt(norm_min**2 + i)

indices = make_indices(n * 2)

# 0 --> 1022, 256 --> 1023, 767 --> 0, 1023 --> 1
rows = [0, 256, 767, 1023]

total_cols = len(range(min_samples, max_samples, step_samples))
csv_data = zeros([1, total_cols])

# transform matrix
P_mtx = zeros((2*n, 2*n), dtype=int)
for ii in range(n>>1):
    P_mtx[ii][ii+(n>>1)] = -1
    P_mtx[ii+(n>>1)][ii] = 1
    P_mtx[ii+n][ii+(n>>1)*3] = -1
    P_mtx[ii+(n>>1)*3][ii+n] = 1

J_mtx = zeros((2*n, 2*n), dtype=int)
for ii in range(J_mtx.shape[0]):
    J_mtx[ii][2*n - 1 - ii] = 1

neg_2_mtx = zeros((2*n, 2*n), dtype=int)
for ii in range(n):
    neg_2_mtx[ii][ii] = 1
    neg_2_mtx[ii+n][ii+n] = -1

neg_3_mtx = zeros((2*n, 2*n), dtype=int)
for ii in range(n):
    neg_3_mtx[ii][ii] = -1
    neg_3_mtx[ii+n][ii+n] = 1

J_mtx_inv = linalg.inv(J_mtx)
neg_2_mtx_inv = linalg.inv(neg_2_mtx)
neg_3_mtx_inv = linalg.inv(neg_3_mtx)

for ii in range(n_files, n_files+1):
    print("ii: ", ii)

    data_sig = data_path + 'sig.txt'
    data_pk = data_path + 'pk.txt'
    data_sk = data_path + 'sk.txt'
    data_z0 = data_path + 'z.txt'

    file_sig = open(data_sig, 'r')
    file_pk = open(data_pk, 'r')
    file_sk = open(data_sk, 'r')
    file_z = open(data_z0, 'r')

    data_in_iters = []

    for iteration in [max_samples]:
        signature = zeros((4*iteration, 2 * n), dtype=int64)
        signature_valid = zeros((4 * iteration, 2 * n), dtype=int64)
        
        basis = file_sk.readline().strip()
        basis = ast.literal_eval(basis)

        assert(type(basis) == list)
        assert(len(basis) == 2*n)

        norm_b0 = linalg.norm(basis)
        # print("norm_b0: ", norm_b0)

        count = 0
        all_count = 0
        for i in range(min_samples):
            all_count = all_count+1
            sig_read = file_sig.readline().strip()
            sig_read = ast.literal_eval(sig_read)

            assert(type(sig_read) == list)
            assert(len(sig_read) == 2*n)

            signature[i] = sig_read
            
            z_read = file_z.readline().strip()
            z_read = ast.literal_eval(z_read)

            assert(type(z_read) == list)
            assert(len(z_read) == 2*n)

            for row in rows:
                index = indices[row]

                # filtered by both leakages and then transform the signatures
                if z_read[index] == 0 or z_read[index] == 1:
                    if z_read[index] == 1:
                        signature_valid[count] = signature[i]
                    if z_read[index] == 0:
                        signature_valid[count] = -signature[i]

                    if row == 256:
                        tmp_back = signature_valid[count]
                        signature_valid[count] = dot(tmp_back, P_mtx)

                    if row == 767:
                        tmp_back = signature_valid[count]
                        tmp_back = dot(tmp_back, P_mtx)
                        tmp_back = dot(tmp_back, neg_2_mtx_inv)
                        signature_valid[count] = dot(tmp_back, J_mtx_inv)
                    
                    if row == 1023:
                        tmp_back = signature_valid[count]
                        tmp_back = dot(tmp_back, neg_3_mtx_inv)
                        signature_valid[count] = dot(tmp_back, J_mtx_inv)

                    count = count + 1

        print("======")
        print("Sampler size: ", all_count)
        print("The number of signatures: ", count)
        print("======")

        for cur_col in range(total_cols):
            sig_extract = signature_valid[:count]

            # Step 1. learn the direction
            cov_result = cov(sig_extract, rowvar=False)
            # spectral decomposition
            egi_result, egi_vector = linalg.eig(cov_result)
            egi_value = egi_result[0]
            egi_vector_T = egi_vector.T
            egi_vector_T_b0 = egi_vector_T[0]

            # Step 2. learn the norm
            min_value = zeros(norm_max**2 - norm_min**2, dtype=float64)
            for i in range(norm_max**2 - norm_min**2):
                values1 = integrate.quad(f1, 0, norm_b0_sqaure[i])
                values2 = integrate.quad(f2, 0, norm_b0_sqaure[i])
                values3 = integrate.quad(f3, 0, norm_b0_sqaure[i])
                result_integrate = ((values1[0]) / (values2[0])) - (values3[0] / (values2[0])) ** 2
                min_value[i] = abs(result_integrate - egi_value)
            min_value_best = min(min_value)
            min_index = min_value.tolist().index(min_value_best)
            # print("norm_b0_best: ", norm_b0_sqaure[min_index])

            result_b0 = zeros(2*n, dtype=float64)
            result_b0_prime = zeros(2*n, dtype=float64)
            recovered_b0 = zeros(2*n, dtype=float64)
            b0_prime = zeros(2*n, dtype=float64)

            distance = zeros(count, dtype=float64)
            # start_normal = math.floor(norm_b0_sqaure[min_index])
            start_normal = 120
            num = (130 - start_normal) * 2
            big_130 = zeros(num, dtype=int64)
            for j in range(num):
                count_inner = 0
                for k in range(2 * n):
                    b0_prime[k] = round(egi_vector_T_b0[k] * (j / 2 + start_normal))
                nnorm = linalg.norm(b0_prime)
                b0_prime = b0_prime / nnorm
                for i in range(count):
                    inner_product = dot(signature_valid[i], b0_prime)
                    distance[i] = abs(inner_product)
                    if nnorm < distance[i]:
                        count_inner = count_inner + 1
                big_130[j] = count_inner

            nor_min_value_best = min(big_130)
            nor_min_index = big_130.tolist().index(nor_min_value_best)
            print("norm_b0: ", norm_b0)
            print("fit_norm: ", (nor_min_index/2 + start_normal))

            # get the approximate key
            norm_b0_sqaure[min_index] = nor_min_index / 2 + start_normal
            for i in range(2 * n):
                result_b0[i] = round(egi_vector_T_b0[i] * norm_b0_sqaure[min_index] - basis[i])
                result_b0_prime[i] = round(egi_vector_T_b0[i] * norm_b0_sqaure[min_index] + basis[i])
                recovered_b0[i] = egi_vector_T_b0[i] * norm_b0_sqaure[min_index]

            result_b0_path = os.path.join(results_path, 'approx_b0_{}'.format(cur_col))

            if linalg.norm(result_b0) ** 2 < linalg.norm(result_b0_prime) ** 2:
                save(result_b0_path, recovered_b0)
            else:
                for i in range(2 * n):
                    recovered_b0[i] = -1 * recovered_b0[i]
                save(result_b0_path, recovered_b0)

            if cur_col == total_cols - 1:
                break

            start_num = min_samples + cur_col * step_samples

            # further add the signatures
            for j in range(start_num, start_num + step_samples):
                all_count = all_count + 1
                sig_read = file_sig.readline().strip()
                sig_read = ast.literal_eval(sig_read)

                assert(type(sig_read) == list)
                assert(len(sig_read) == 2*n)

                signature[j] = sig_read

                z_read = file_z.readline().strip()
                z_read = ast.literal_eval(z_read)

                assert(type(z_read) == list)
                assert(len(z_read) == 2*n)

                for row in rows:
                    index = indices[row]
                    # filtered by both leakages and then transform the signatures
                    if z_read[index] == 0 or z_read[index] == 1:
                        if z_read[index] == 1:
                            signature_valid[count] = signature[j]
                        if z_read[index] == 0:
                            signature_valid[count] = -signature[j]

                        if row == 256:
                            tmp_back = signature_valid[count]
                            signature_valid[count] = dot(tmp_back, P_mtx)

                        if row == 767:
                            tmp_back = signature_valid[count]
                            tmp_back = dot(tmp_back, P_mtx)
                            tmp_back = dot(tmp_back, neg_2_mtx_inv)
                            signature_valid[count] = dot(tmp_back, J_mtx_inv)

                        if row == 1023:
                            tmp_back = signature_valid[count]
                            tmp_back = dot(tmp_back, neg_3_mtx_inv)
                            signature_valid[count] = dot(tmp_back, J_mtx_inv)

                        count = count + 1

            print("======")
            print("Sampler size: ", all_count)
            print("The number of signatures: ", count)
            print("======")

print("The analyze finishes!!!")