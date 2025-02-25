import time 
from tqdm import trange
import os
from utils import *
import sys
sys.path.insert(0, './falcon')
import falcon
import argparse
parser = argparse.ArgumentParser(description = 'Falcon signature generation')
parser.add_argument('--key', type = int, default = 0)
args = parser.parse_args()

# i-the instance
keys = args.key
# dimension
n = 512
# number of signatures to be generated
iteration = 60 * 1000
# modulus
Q = 12289
msg = b'test'

data_path = r'./sig_gen/'
if not os.path.exists(data_path):
    os.makedirs(data_path)

data_path = data_path + "key_{0}/".format(keys)
if not os.path.exists(data_path):
    os.makedirs(data_path)

start_time = time.time()

for i in trange(keys,keys+1):
    # key generation
    sk = falcon.SecretKey(n)
    f, g = sk.f, sk.g
    basis = list(g) + neg(list(f))
    pk = falcon.PublicKey(sk)
    h = pk.h

    file_sk = open(data_path + 'sk.txt', "a")
    file_sk.write(str(basis)+'\n')
    file_sk.close()

    file_pk = open(data_path + 'pk.txt', "a")
    file_pk.write(str(h)+'\n')
    file_pk.close()

    with open(data_path + 'sig.txt', "a") as file_sig, open(data_path + 'z.txt', "a") as file_z:
        for j in range(iteration):
            # signing
            sig, aleas = sk.sign(msg)
            file_sig.write(str(sig[0] + sig[1])+'\n')
            file_z.write(str(aleas)+'\n')
    file_sig.close()
    file_z.close()

end_time = time.time()

run_time = end_time - start_time

print("run time: ", run_time)

