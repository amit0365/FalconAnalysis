# Bare-metal Cortex-M4 build for Falcon F1 vs F2-radical benchmark.
#
# Builds two ELFs for QEMU mps2-an386:
#   m4_bench_f1.elf   — Lin et al. F1 protected SamplerZ
#   m4_bench_f2.elf   — F2-radical (this work)
#
# Usage:
#   make ARM_TC=/path/to/arm-none-eabi-bin   # if toolchain not on PATH
#   make bench                                # build both
#   make run                                  # build + run on QEMU with SYSTICK
#
# Toolchain: ARM GNU Toolchain 15.2 (gcc-arm-embedded). On macOS without
# admin install, extract from the Homebrew cask pkg:
#   pkgutil --expand-full \
#     ~/Library/Caches/Homebrew/Cask/arm-gnu-toolchain-15.2.rel1-darwin-arm64-arm-none-eabi.pkg--15.2.rel1.pkg \
#     /tmp/gcc-arm-extract
#   export PATH=/tmp/gcc-arm-extract/Payload/bin:$PATH

ARM_TC   ?=
CC        = $(if $(ARM_TC),$(ARM_TC)/)arm-none-eabi-gcc
SIZE      = $(if $(ARM_TC),$(ARM_TC)/)arm-none-eabi-size
QEMU      ?= qemu-system-arm

CFLAGS_M4 = -mcpu=cortex-m4 -mthumb -mfpu=fpv4-sp-d16 -mfloat-abi=hard -O2
LDFLAGS   = --specs=nano.specs -nostartfiles -T mps2_m4.ld

SRC       = startup_stm32f4.s m4_bench.c \
            ../codec.c ../common.c ../falcon.c ../fft.c ../fpr.c \
            ../keygen.c ../rng.c ../shake.c ../sign.c ../vrfy.c

INCLUDES  = -I.. -I.

.PHONY: all bench run clean key

all: bench

bench: m4_bench_f1.elf m4_bench_f2.elf

m4_bench_f1.elf: $(SRC) startup_stm32f4.s mps2_m4.ld key_falcon512.h
	$(CC) $(CFLAGS_M4) $(LDFLAGS) $(INCLUDES) $(SRC) -o $@
	$(SIZE) $@

m4_bench_f2.elf: $(SRC) startup_stm32f4.s mps2_m4.ld key_falcon512.h
	$(CC) $(CFLAGS_M4) -DF2_RADICAL $(LDFLAGS) $(INCLUDES) $(SRC) -o $@
	$(SIZE) $@

run: bench
	@echo "=== F1 (Lin et al.) on QEMU mps2-an386 ==="
	@$(QEMU) -M mps2-an386 -cpu cortex-m4 -nographic -semihosting \
	  -kernel m4_bench_f1.elf &
	@PID=$$!; sleep 20; kill $$PID 2>/dev/null; wait $$PID 2>/dev/null; true
	@echo ""
	@echo "=== F2-radical on QEMU mps2-an386 ==="
	@$(QEMU) -M mps2-an386 -cpu cortex-m4 -nographic -semihosting \
	  -kernel m4_bench_f2.elf &
	@PID=$$!; sleep 20; kill $$PID 2>/dev/null; wait $$PID 2>/dev/null; true

# Regenerate the Falcon-512 key embedded in key_falcon512.h.
# Must be run on the host (not for M4); uses the host's keygen.
key:
	@echo "(Run from parent dir after building host .o files:)"
	@echo "  clang -O2 -I.. -o /tmp/dump_key dump_key.c \\"
	@echo "    ../codec.o ../common.o ../falcon.o ../fft.o ../fpr.o \\"
	@echo "    ../keygen.o ../rng.o ../shake.o ../sign.o ../vrfy.o"
	@echo "  /tmp/dump_key  # writes key_falcon512.h"

clean:
	rm -f *.elf *.o *.hex
