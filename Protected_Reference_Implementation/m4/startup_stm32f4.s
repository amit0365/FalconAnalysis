.syntax unified
.cpu cortex-m4
.fpu fpv4-sp-d16
.thumb

/* Vector table with SysTick handler at slot 15 (offset 0x3C) */
.global vectors
.section .isr_vector, "a", %progbits
vectors:
    .word _estack            /* 0:  Initial SP */
    .word Reset_Handler      /* 1:  Reset */
    .word Default_Handler    /* 2:  NMI */
    .word Default_Handler    /* 3:  HardFault */
    .word Default_Handler    /* 4:  MemManage */
    .word Default_Handler    /* 5:  BusFault */
    .word Default_Handler    /* 6:  UsageFault */
    .word 0                  /* 7-10: reserved */
    .word 0
    .word 0
    .word 0
    .word Default_Handler    /* 11: SVC */
    .word Default_Handler    /* 12: DebugMon */
    .word 0                  /* 13: reserved */
    .word Default_Handler    /* 14: PendSV */
    .word SysTick_Handler    /* 15: SysTick */
    .rept 80
    .word Default_Handler    /* 16+: external IRQs */
    .endr

.text
.global Reset_Handler
.thumb_func
Reset_Handler:
    /* enable FPU (CPACR at 0xE000ED88, set CP10/CP11 = full access) */
    ldr r0, =0xE000ED88
    ldr r1, [r0]
    orr r1, r1, #(0xF << 20)
    str r1, [r0]
    dsb
    isb
    /* copy .data from flash to sram */
    ldr r0, =_sdata
    ldr r1, =_edata
    ldr r2, =_sidata
1:  cmp r0, r1
    beq 2f
    ldr r3, [r2], #4
    str r3, [r0], #4
    b 1b
2:  /* zero .bss */
    ldr r0, =_sbss
    ldr r1, =_ebss
    mov r3, #0
3:  cmp r0, r1
    beq 4f
    str r3, [r0], #4
    b 3b
4:  bl main
    /* semihosting exit */
    mov r0, #0x18
    ldr r1, =0x20026
    bkpt 0xAB
5:  b 5b

.global Default_Handler
.thumb_func
Default_Handler:
    b Default_Handler

/* Weak SysTick handler; C code can override. */
.weak SysTick_Handler
.thumb_func
SysTick_Handler:
    bx lr
