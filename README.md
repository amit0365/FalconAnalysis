# Exploitable Codes for Paper "Thorough Power Analysis on Falcon Gaussian Samplers and Practical Countermeasure"

This paper mainly focuses on the side channel security of [[Falcon]](https://falcon-sign.info/), which is one of the post-quantum signatures selected by NIST for standardization. In this repository, we provide the following exploitable codes:
* Refined attack on the key recovery of [[ZLYW23]](https://eprint.iacr.org/2023/224.pdf)
* Countermeasures against half Gaussian leakage [[GMRR22]](https://eprint.iacr.org/2022/057.pdf) and sign leakage [[ZLYW23]](https://eprint.iacr.org/2023/224.pdf)

Next, we give the related descriptions and show how to use it. 

## Refined Attack

In folder "Refined_attack/", we first use the symplecticity of NTRU to improve the key recovery [[ZLYW23]](https://eprint.iacr.org/2023/224.pdf). By combing some advanced decoding technique, the required traces for a full key recovery can be reduced by at least <mark> 85% </mark>. 

Then, we provide the exploitable codes to validate the effectiveness of our refined attacks. The procedure can be divided into the following three steps:

1. generate the signatures as a database
2. improve the key recovery by exploiting NTRU symplecticity
3. correct the errors of approximate key with decoding technique

Next, we give some examples to show how to run the codes given in the folder "Refined_attack/". We first enter this directory
```
$ cd Refined_attack/
```

### 1. How to generate signatures
First, we collect enough signatures to perform the following full key recovery against Falcon. In this setting, 60,000 signatures (configured by the parameter "iteration" in the gen_sig.py) are sufficient for our all experiments in our paper. 
* *parameter description*
    * --key, i-th instance to be generated
```
$ cd data/
$ python3 gen_sig.py --key 0
```

### 2. Refining the key recovery by using the symplecticity of NTRU
Next, we make use of the above generated signatures to approximate the signing key respectively by using the half Gaussian leakage, sign leakage and both leakages. We further adapt the symplecticity of NTRU basis to dramatically reduce the required traces.
* *parameter description*
    * --under, minimum number signatures
    * --top, maximum number signatures
    * --step, the signature increment
    * --file, i-th instance

The case of only using half Gaussian leakage:
```
$ cd analyze/
$ python3 half_gau.py --under *** --top *** --step *** --file *** 
```
The case of only using sign leakage:
```
$ cd analyze/
$ python3 sign.py --under *** --top *** --step *** --file ***
```
The case of using both leakages:
```
$ cd analyze/
$ python3 both.py --under *** --top *** --step *** --file ***
```
### 3. Correct errors with decoding technique

Furthermore, by adapting some decoding technique, we mount a full key recovery from the approximation of key. Moreover, we provide the complete 40 instances evaluated in our paper and store these data in the respective subfolder "decoding/../results_process/", especially for the approximate key recovered by Step 2 ("recovered_keys.npy"). 

Correct errors when using half Gaussian leakage:
```
$ cd decoding/half_gau/
$ python3 improved_decoding.py > your_file.txt
```

Correct errors when using sign leakage:
```
$ cd decoding/sign/
$ python3 improved_decoding.py > your_file.txt
```

Correct errors when using both leakages:
```
$ cd decoding/both/
$ python3 improved_decoding.py > your_file.txt
```

## Countermeasures
In this part, we first give a practical countermeasure against both half Gaussian leakage [[GMRR22]](https://eprint.iacr.org/2022/057.pdf) and sign leakage[[ZLYW23]](https://eprint.iacr.org/2023/224.pdf).

### Protected implementation
We provide the full protected reference implementation, based on the original [one](https://csrc.nist.gov/CSRC/media/Projects/post-quantum-cryptography/documents/round-3/submissions/Falcon-Round3.zip). 

For the protected reference implementation:
```
$ cd Protected_Reference_Implementation/
$ make
$ ./test_falcon
```





