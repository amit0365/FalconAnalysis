/* Bare-metal M4 Falcon-512 sign benchmark using SYSTICK for true M4 cycles.
 * SYSTICK is the M4's 24-bit downcounter. We extend to 64-bit via interrupt
 * handler counting wraps. QEMU's mps2-an386 implements SYSTICK correctly. */
#include <string.h>
#include <stdint.h>
#include "falcon.h"
#include "key_falcon512.h"

#define LOGN 9
#define N_SIGS 3

/* SYSTICK registers in System Control Space */
#define SYST_CSR  (*(volatile uint32_t*)0xE000E010)
#define SYST_RVR  (*(volatile uint32_t*)0xE000E014)
#define SYST_CVR  (*(volatile uint32_t*)0xE000E018)
#define SYSTICK_ENABLE   (1U << 0)
#define SYSTICK_TICKINT  (1U << 1)
#define SYSTICK_CLKSRC   (1U << 2)
#define SYSTICK_COUNTFLAG (1U << 16)
#define SYSTICK_RELOAD   0x00FFFFFF   /* max 24-bit */

static volatile uint64_t systick_wraps = 0;

/* C-side SysTick handler (overrides the weak default in startup.s) */
void SysTick_Handler(void) {
    systick_wraps++;
}

static void systick_init(void) {
    SYST_RVR = SYSTICK_RELOAD;
    SYST_CVR = 0;  /* writing CVR clears it AND COUNTFLAG */
    systick_wraps = 0;
    SYST_CSR = SYSTICK_CLKSRC | SYSTICK_TICKINT | SYSTICK_ENABLE;
}

/* Returns total M4 cycles since systick_init.
 * Race-free: temporarily disable interrupts, snapshot wraps + cvr together,
 * re-check COUNTFLAG to handle a wrap during the snapshot. */
static uint64_t systick_cycles(void) {
    uint32_t wraps, cvr, csr;
    __asm volatile ("cpsid i" ::: "memory");
    wraps = (uint32_t)systick_wraps;
    csr = SYST_CSR;            /* reading clears COUNTFLAG */
    cvr = SYST_CVR;
    if (csr & SYSTICK_COUNTFLAG) {
        /* Wrap happened just before our read; reload happened too. */
        wraps += 1;
        cvr = SYST_CVR;
    }
    __asm volatile ("cpsie i" ::: "memory");
    return ((uint64_t)wraps << 24) + (SYSTICK_RELOAD - cvr);
}

/* Semihosting */
static inline int sh_call(int op, void *arg) {
    register int r0 asm("r0") = op;
    register void *r1 asm("r1") = arg;
    asm volatile ("bkpt 0xAB" : "+r"(r0) : "r"(r1) : "memory");
    return r0;
}
#define SYS_WRITE0  0x04
#define SYS_EXIT    0x18
static void sh_puts(const char *s) { sh_call(SYS_WRITE0, (void*)s); }
static void sh_exit(int code) {
    uint32_t arg[2] = {0x20026, (uint32_t)code};
    sh_call(SYS_EXIT, arg);
    for(;;){}
}

static char *u64_to_str(uint64_t v, char *buf) {
    char *p = buf + 23; *p = 0;
    if (v == 0) { *--p = '0'; return p; }
    while (v) { *--p = '0' + (v % 10); v /= 10; }
    return p;
}
static void sh_putu(uint64_t v) {
    char buf[24]; sh_puts(u64_to_str(v, buf));
}

static uint8_t sig_buf[FALCON_SIG_COMPRESSED_MAXSIZE(LOGN)];
static uint8_t tmp_buf[FALCON_TMPSIZE_SIGNDYN(LOGN)];
static const char *msg = "m4 bench";

int main(void) {
    shake256_context rng;
    uint8_t seed[32] = {0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,
                       16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31};
    shake256_init_prng_from_seed(&rng, seed, sizeof seed);

#ifdef F2_RADICAL
    sh_puts("=== M4 Falcon-512 variant=F2-radical (SYSTICK cycles) ===\n");
#else
    sh_puts("=== M4 Falcon-512 variant=F1-Lin (SYSTICK cycles) ===\n");
#endif

    systick_init();
    sh_puts("SYSTICK enabled, reload=0xFFFFFF (24-bit, wrap counter via IRQ)\n");
    sh_puts("Running ");
    sh_putu(N_SIGS);
    sh_puts(" signatures...\n");

    uint64_t total = 0;
    int succ = 0;
    for (int i = 0; i < N_SIGS; i++) {
        size_t sl = sizeof(sig_buf);
        uint64_t c0 = systick_cycles();
        int rc = falcon_sign_dyn(&rng, sig_buf, &sl, FALCON_SIG_COMPRESSED,
                                  m4_privkey, M4_PRIVKEY_LEN,
                                  msg, strlen(msg), tmp_buf, sizeof(tmp_buf));
        uint64_t c1 = systick_cycles();
        if (rc == 0) {
            uint64_t d = c1 - c0;
            total += d;
            succ++;
            sh_puts("  sig "); sh_putu(i); sh_puts(": "); sh_putu(d);
            sh_puts(" cycles, sig_len="); sh_putu(sl); sh_puts("\n");
        } else {
            sh_puts("  sig FAILED rc=");
            sh_putu((uint32_t)rc); sh_puts("\n");
        }
    }
    if (succ > 0) {
        uint64_t avg = total / (uint64_t)succ;
        sh_puts("=== avg: "); sh_putu(avg); sh_puts(" cycles/sig\n");
        sh_puts("    at 168 MHz: "); sh_putu(avg / 168000); sh_puts(" ms/sig\n");
    }
    sh_exit(0);
    return 0;
}
