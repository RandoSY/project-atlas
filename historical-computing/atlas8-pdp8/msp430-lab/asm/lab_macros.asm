; ATLAS-8 MSP430 symbolic vocabulary (TI assembler syntax, illustrative)
; These macros are device-side operations, NOT PDP-8 IOT instruction words.
; Include correct MSP430G2553 device definitions in the assembler project.
;
ADC_START  .macro
    BIS.W   #ADC10SC, &ADC10CTL0
    .endm
;
LAB_READY_ON .macro
    BIS.B   #BIT0, &P2OUT
    .endm
;
LAB_READY_OFF .macro
    BIC.B   #BIT0, &P2OUT
    .endm
