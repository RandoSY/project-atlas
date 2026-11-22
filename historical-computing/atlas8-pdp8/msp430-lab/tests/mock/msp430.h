/* HOST-ONLY compile stub: syntax-check G2553 C; never flash this file! */
#ifndef MOCK_MSP430_H
#define MOCK_MSP430_H
#include <stdint.h>
#define __interrupt
#define BIT0 1
#define BIT1 2
#define BIT2 4
#define WDTPW 0x5a00
#define WDTHOLD 0x80
#define CALBC1_1MHZ 0x10
#define CALDCO_1MHZ 0x10
#define UCSWRST 1
#define UCSSEL_2 0x80
#define UCBRS_0 0
#define UCA0RXIE 1
#define UCA0TXIFG 2
#define ADC10ON 0x10
#define ADC10SHT_2 0x200
#define INCH_0 0
#define ADC10BUSY 1
#define ENC 2
#define ADC10SC 1
#define TASSEL_2 0x200
#define MC_2 0x20
#define TACLR 4
#define TAIE 2
#define CM_1 0x4000
#define CCIS_0 0
#define SCS 0x800
#define CAP 0x100
#define CCIE 0x10
#define TAIFG 1
#define __enable_interrupt() ((void)0)
#define __disable_interrupt() ((void)0)
extern volatile uint16_t WDTCTL, ADC10CTL0,ADC10CTL1,ADC10MEM,TA1CTL,TA1CCTL1,TA1IV,TA1CCR1;
extern volatile uint8_t P2OUT,P2SEL,P2SEL2,P2DIR,P1SEL,P1SEL2,ADC10AE0,DCOCTL,BCSCTL1,IE2,IFG2,UCA0CTL1,UCA0BR0,UCA0BR1,UCA0MCTL,UCA0TXBUF,UCA0RXBUF;
#endif
