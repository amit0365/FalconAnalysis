/* Minimal bench: 200 falcon_sign_dyn calls on Falcon-512, per-sig wall time. */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>
#include "falcon.h"

#define N_SIGS 200
#define LOGN 9

static uint64_t now_ns(void) {
    struct timespec ts;
#ifdef __APPLE__
    clock_gettime(CLOCK_UPTIME_RAW, &ts);
#else
    clock_gettime(CLOCK_MONOTONIC, &ts);
#endif
    return (uint64_t)ts.tv_sec * 1000000000ULL + (uint64_t)ts.tv_nsec;
}

int main(void) {
    shake256_context rng;
    shake256_init_prng_from_system(&rng);

    size_t privkey_len = FALCON_PRIVKEY_SIZE(LOGN);
    size_t pubkey_len = FALCON_PUBKEY_SIZE(LOGN);
    size_t sig_len = FALCON_SIG_COMPRESSED_MAXSIZE(LOGN);
    size_t tmp_kg = FALCON_TMPSIZE_KEYGEN(LOGN);
    size_t tmp_sign = FALCON_TMPSIZE_SIGNDYN(LOGN);

    uint8_t *privkey = malloc(privkey_len);
    uint8_t *pubkey = malloc(pubkey_len);
    uint8_t *sig = malloc(sig_len);
    uint8_t *tmp_k = malloc(tmp_kg);
    uint8_t *tmp_s = malloc(tmp_sign);

    falcon_keygen_make(&rng, LOGN, privkey, privkey_len, pubkey, pubkey_len, tmp_k, tmp_kg);

    const char *msg = "bench";
    size_t msg_len = strlen(msg);

    for (int i = 0; i < 5; i++) {
        size_t sl = sig_len;
        falcon_sign_dyn(&rng, sig, &sl, FALCON_SIG_COMPRESSED,
                         privkey, privkey_len, msg, msg_len, tmp_s, tmp_sign);
    }

    uint64_t t0 = now_ns();
    for (int i = 0; i < N_SIGS; i++) {
        size_t sl = sig_len;
        int rc = falcon_sign_dyn(&rng, sig, &sl, FALCON_SIG_COMPRESSED,
                                  privkey, privkey_len, msg, msg_len, tmp_s, tmp_sign);
        if (rc != 0) { fprintf(stderr, "sign failed\n"); return 1; }
    }
    uint64_t t1 = now_ns();

    double total_ms = (double)(t1 - t0) / 1e6;
    double per_sig_us = total_ms * 1000.0 / N_SIGS;
    printf("logn=%d N=%d total=%.2f ms per_sig=%.2f us throughput=%.0f sigs/sec\n",
           LOGN, N_SIGS, total_ms, per_sig_us, 1e6 / per_sig_us);

    free(privkey); free(pubkey); free(sig); free(tmp_k); free(tmp_s);
    return 0;
}
