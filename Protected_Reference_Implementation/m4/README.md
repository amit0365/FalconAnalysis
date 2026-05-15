# Cortex-M4 Bare-Metal Build for Falcon F1 vs F2-radical

Reproduces the M4 cycle-count measurements in `easycrypt_f2/M4_QEMU_EMPIRICAL.txt`.

## What this does

Builds the Falcon-512 SamplerZ + F2-radical countermeasure for bare-metal Cortex-M4 (ARMv7-M) and runs on QEMU `mps2-an386`. Uses ARM SYSTICK (with IRQ-driven wrap counter) to measure true M4 cycle counts. Outputs results via ARM semihosting.

## Quick start (assumes ARM toolchain on PATH)

```sh
make bench       # builds m4_bench_f1.elf and m4_bench_f2.elf
make run         # builds + runs both on QEMU with semihosting output
```

## Toolchain setup

You need:
1. `arm-none-eabi-gcc` (ARM GNU Toolchain 15.2+) with newlib
2. `qemu-system-arm` (11.0+)

### macOS without admin install

The Homebrew `gcc-arm-embedded` cask requires sudo for its installer pkg. If you don't want the global install, extract the toolchain payload manually:

```sh
brew fetch --cask gcc-arm-embedded   # cache the .pkg without installing
pkgutil --expand-full \
  ~/Library/Caches/Homebrew/Cask/arm-gnu-toolchain-15.2.rel1-darwin-arm64-arm-none-eabi.pkg--15.2.rel1.pkg \
  /tmp/gcc-arm-extract
export PATH=/tmp/gcc-arm-extract/Payload/bin:$PATH
```

For QEMU:
```sh
brew install qemu
```

Then `make bench && make run`.

## Files

| File | Purpose |
|---|---|
| `Makefile` | Build + run rules |
| `startup_stm32f4.s` | Vector table (with SysTick at slot 15), Reset_Handler, FPU enable, .data/.bss init |
| `mps2_m4.ld` | Linker script for QEMU `mps2-an386` (flash @ 0x00000000, SRAM @ 0x20000000) |
| `m4_bench.c` | Bare-metal bench: SYSTICK init, runs N_SIGS Falcon-512 signatures, reports cycles via semihosting |
| `dump_key.c` | Host-only — generates Falcon-512 key and writes it as a C array |
| `key_falcon512.h` | Pre-generated Falcon-512 private key (embedded as static const array) |

## How the cycle counting works

SYSTICK is a 24-bit downcounter in the M4 System Control Space. We:
1. Set reload value to `0xFFFFFF` (max)
2. Enable with `CLKSOURCE=processor`, `TICKINT=1` (interrupt on wrap)
3. `SysTick_Handler` in C increments a global wrap counter
4. Read total cycles via race-free snapshot (`cpsid i` / re-check `COUNTFLAG`)

This extends the 24-bit hardware counter to effectively 64-bit. Sufficient for measuring full Falcon-512 signatures (which take ~10⁶ cycles).

## Expected output

```
=== M4 Falcon-512 variant=F1-Lin (SYSTICK cycles) ===
SYSTICK enabled, reload=0xFFFFFF (24-bit, wrap counter via IRQ)
Running 3 signatures...
  sig 0: 1309125 cycles, sig_len=651
  sig 1: 1213600 cycles, sig_len=655
  sig 2: 1213225 cycles, sig_len=657
=== avg: 1245316 cycles/sig
    at 168 MHz: 7 ms/sig
```

For F2-radical (`-DF2_RADICAL`):
```
  sig 0: 737500 cycles, sig_len=650
  sig 1: 543025 cycles, sig_len=658
  sig 2: 489925 cycles, sig_len=657
=== avg: 590150 cycles/sig
    at 168 MHz: 3 ms/sig
```

**F2/F1 ratio (steady state): 2.35× fewer M4 cycles.**

## Caveats

QEMU's `mps2-an386` SYSTICK counts emulated instructions cleanly but does NOT model:
- Cache miss latency
- Flash wait states (~3 cycles per access above 30 MHz on real STM32F4)
- Pipeline stalls / branch misprediction
- Memory bus contention

Real STM32F4 cycles are typically 1.5-3× higher than QEMU's count for cache-heavy workloads. The **F2/F1 ratio is preserved** since it depends on instruction count, not memory hierarchy.

For paper-grade numbers, use a real STM32F4 board (Chipwhisperer-Lite or similar) — Phase 3 work in the `easycrypt_f2/KILL_PLAN.md`.

## Regenerating the key

If you want a different Falcon-512 key embedded:

```sh
cd ..    # back to Protected_Reference_Implementation/
make     # builds host .o files
clang -O2 -I . -o /tmp/dump_key m4/dump_key.c \
  codec.o common.o falcon.o fft.o fpr.o keygen.o rng.o shake.o sign.o vrfy.o
/tmp/dump_key   # writes m4/key_falcon512.h
```

## See also

- `../sign.c` (lines after `#ifdef F2_RADICAL`) — F2-radical implementation
- `../../easycrypt_f2/M4_QEMU_EMPIRICAL.txt` — measurement results
- `../../easycrypt_f2/M4_ESTIMATE.md` — analytical projection vs measurement
- `../../easycrypt_f2/PHASE1_MAIN_THEOREM.md` — F2-radical security proof
