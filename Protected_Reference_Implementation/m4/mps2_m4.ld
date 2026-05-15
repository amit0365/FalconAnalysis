ENTRY(Reset_Handler)
MEMORY {
    FLASH (rx) : ORIGIN = 0x00000000, LENGTH = 4M
    SRAM  (rwx): ORIGIN = 0x20000000, LENGTH = 256K
}
_estack = ORIGIN(SRAM) + LENGTH(SRAM);
SECTIONS {
    .isr_vector : { KEEP(*(.isr_vector)) } > FLASH
    .text : { *(.text*) *(.rodata*) *(.glue_7*) *(.eh_frame)
              KEEP(*(.init)) KEEP(*(.fini)) . = ALIGN(4); _etext = .; } > FLASH
    .ARM.exidx : { *(.ARM.exidx*) } > FLASH
    .preinit_array : { PROVIDE_HIDDEN(__preinit_array_start = .);
                       KEEP(*(.preinit_array*)) PROVIDE_HIDDEN(__preinit_array_end = .); } > FLASH
    .init_array : { PROVIDE_HIDDEN(__init_array_start = .);
                    KEEP(*(SORT(.init_array.*))) KEEP(*(.init_array*))
                    PROVIDE_HIDDEN(__init_array_end = .); } > FLASH
    .fini_array : { PROVIDE_HIDDEN(__fini_array_start = .);
                    KEEP(*(SORT(.fini_array.*))) KEEP(*(.fini_array*))
                    PROVIDE_HIDDEN(__fini_array_end = .); } > FLASH
    _sidata = LOADADDR(.data);
    .data : { _sdata = .; *(.data*) . = ALIGN(4); _edata = .; } > SRAM AT > FLASH
    .bss : { _sbss = .; *(.bss*) *(COMMON) . = ALIGN(4); _ebss = .; } > SRAM
    .heap (NOLOAD) : { end = .; _end = .; . = . + 32K; _heap_end = .; } > SRAM
}
