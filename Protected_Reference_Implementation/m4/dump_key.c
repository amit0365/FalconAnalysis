#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "falcon.h"
int main(void) {
    shake256_context rng;
    shake256_init_prng_from_system(&rng);
    size_t pk_len = FALCON_PRIVKEY_SIZE(9);
    size_t pu_len = FALCON_PUBKEY_SIZE(9);
    size_t tmp_kg = FALCON_TMPSIZE_KEYGEN(9);
    uint8_t *pk = malloc(pk_len), *pu = malloc(pu_len), *t = malloc(tmp_kg);
    falcon_keygen_make(&rng, 9, pk, pk_len, pu, pu_len, t, tmp_kg);
    FILE *f = fopen("/tmp/m4build/key_falcon512.h", "w");
    fprintf(f, "/* Pre-generated Falcon-512 private key for M4 bench */\n");
    fprintf(f, "#define M4_PRIVKEY_LEN %zu\n", pk_len);
    fprintf(f, "static const unsigned char m4_privkey[M4_PRIVKEY_LEN] = {");
    for (size_t i = 0; i < pk_len; i++) fprintf(f, "%s%u,", i%16==0?"\n  ":" ", pk[i]);
    fprintf(f, "\n};\n");
    fclose(f);
    return 0;
}
