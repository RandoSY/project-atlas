/* ATLAS-8 G2553 Laboratory Controller v0.7 (reference firmware)
 * Built for TI MSP430G2553, CCS or msp430-elf-gcc with TI device headers.
 * P1.1 = UCA0 RX (from Pico GP0), P1.2 = UCA0 TX (to Pico GP1).
 * P2.0 = READY -> Pico GP2; P1.0 = A0; P2.1 = Timer1_A CCI1A.
 * 3.3V logic only; reference ADC10 is AVCC, NOT precision voltage.
 */
#include <msp430.h>
#include <stdint.h>
#include "lab_protocol.h"
#define RX_SIZE 32
static volatile uint8_t rx_buf[RX_SIZE], rx_read=0, rx_write=0, rx_overrun=0;
static volatile uint8_t adc_active=0, timer_active=0, measure_ready=0, measure_error=0;
static volatile uint16_t adc_value=0, timer_wraps=0;
static volatile uint32_t timer_first=0, timer_delta=0;
static volatile uint8_t timer_edges=0;
static struct lab_parser parser;
static struct lab_request request;
static uint8_t response[LAB_FRAME_MAX], answer[LAB_MAX_PAYLOAD];
static void ready_update(void) {
    if(measure_ready) P2OUT |= BIT0;
    else P2OUT &= (uint8_t)~BIT0;
}
static void tx_byte(uint8_t b) { while (!(IFG2 & UCA0TXIFG)) {} UCA0TXBUF=b; }
static void send_reply(uint8_t seq,uint8_t op,uint8_t status,const uint8_t *data,uint8_t count) {
    uint8_t n,i;
    answer[0]=status;
    for (i=0;i<count && i<7;i++) answer[i+1]=data[i];
    n=lab_pack(seq,(uint8_t)(op|0x80),answer,(uint8_t)(count+1),response);
    for(i=0;i<n;i++) tx_byte(response[i]);
}
static void clear_measurement(void) {
    ADC10CTL0 &= (uint16_t)~ENC;
    TA1CCTL1 &= (uint16_t)~CCIE;
    TA1CTL &= (uint16_t)~(MC_2 | TAIE);
    adc_active=0;timer_active=0;measure_ready=0;measure_error=0;
    timer_edges=0;timer_wraps=0;timer_delta=0;
    ready_update();
}
static void begin_adc(uint8_t channel) {
    clear_measurement();
    /* Channels A1/A2 unavailable: reserved for UART. */
    ADC10CTL0 &= (uint16_t)~ENC;
    ADC10CTL1 = ((uint16_t)channel<<12);  /* INCH_x at bits 12..15 */
    ADC10AE0 |= (uint8_t)(1u<<channel);
    adc_active=1;
    ADC10CTL0 |= ENC|ADC10SC;
}
static void begin_timer(void) {
    clear_measurement();
    TA1CTL=TASSEL_2 | MC_2 | TACLR | TAIE;
    P2DIR &= (uint8_t)~BIT1;
    P2SEL |= BIT1;
    P2SEL2 &= (uint8_t)~BIT1;
    TA1CCTL1=CM_1|CCIS_0|SCS|CAP|CCIE;
    timer_active=1;
}
static void service_adc(void) {
    if (adc_active && !(ADC10CTL1&ADC10BUSY)) {
        adc_value=ADC10MEM;
        adc_active=0;measure_ready=1;ready_update();
    }
}
static uint8_t is_busy(void) {return (uint8_t)(adc_active||timer_active);}
static void command(const struct lab_request *r) {
    uint8_t data[4];
    switch(r->op) {
        case LAB_IDENTIFY:
            if(r->len)break;
            data[0]=1;data[1]=0;data[2]=3; /* protocol 1.0, ADC + timer */
            send_reply(r->seq,r->op,LAB_OK,data,3);return;
        case LAB_STATUS:
            if(r->len)break;
            data[0]=(uint8_t)(measure_ready | (is_busy()<<1) | (measure_error<<2));
            send_reply(r->seq,r->op,LAB_OK,data,1);return;
        case LAB_CLEAR:
            if(r->len)break;
            clear_measurement();send_reply(r->seq,r->op,LAB_OK,data,0);return;
        case LAB_ADC_START:
            if(r->len!=1||r->data[0]>7||r->data[0]==1||r->data[0]==2)break;
            if(is_busy()) {send_reply(r->seq,r->op,LAB_BUSY,data,0);return;}
            begin_adc(r->data[0]);send_reply(r->seq,r->op,LAB_OK,data,0);return;
        case LAB_ADC_READ:
            if(r->len)break;
            if(!measure_ready || timer_edges) {send_reply(r->seq,r->op,LAB_NOT_READY,data,0);return;}
            data[0]=(uint8_t)adc_value;data[1]=(uint8_t)(adc_value>>8);
            measure_ready=0;ready_update();
            send_reply(r->seq,r->op,LAB_OK,data,2);return;
        case LAB_TIMER_START:
            if(r->len)break;
            if(is_busy()) {send_reply(r->seq,r->op,LAB_BUSY,data,0);return;}
            begin_timer();send_reply(r->seq,r->op,LAB_OK,data,0);return;
        case LAB_TIMER_READ:
            if(r->len)break;
            if(!measure_ready || !timer_edges) {send_reply(r->seq,r->op,LAB_NOT_READY,data,0);return;}
            data[0]=(uint8_t)timer_delta;data[1]=(uint8_t)(timer_delta>>8);
            data[2]=(uint8_t)(timer_delta>>16);data[3]=(uint8_t)(timer_delta>>24);
            measure_ready=0;ready_update();
            send_reply(r->seq,r->op,LAB_OK,data,4);return;
    }
    send_reply(r->seq,r->op,LAB_BAD_ARGUMENT,data,0);
}
#pragma vector=USCIAB0RX_VECTOR
__interrupt void lab_uart_rx_isr(void) {
    uint8_t next=(uint8_t)((rx_write+1)&(RX_SIZE-1));
    uint8_t byte=UCA0RXBUF;
    if(next!=rx_read) {rx_buf[rx_write]=byte;rx_write=next;}
    else rx_overrun=1;
}
#pragma vector=TIMER1_A1_VECTOR
__interrupt void lab_timer_isr(void) {
    switch(TA1IV) {
        case 2: /* CCR1 captures rising edge, Timer1_A @ 1 MHz */
            if(timer_active) {
                uint32_t stamp=((uint32_t)timer_wraps<<16)|TA1CCR1;
                /* Overflow may be pending but lower-priority than capture. */
                if((TA1CTL&TAIFG) && TA1CCR1<0x8000)stamp+=65536UL;
                if(timer_edges==0) {timer_first=stamp;timer_edges=1;}
                else {
                    timer_delta=stamp-timer_first;
                    timer_active=0;measure_ready=1;
                    TA1CCTL1 &= (uint16_t)~CCIE;
                    TA1CTL &= (uint16_t)~(MC_2 | TAIE);
                    ready_update();
                }
            }
            break;
        case 10: ++timer_wraps;break;
        default: break;
    }
}
static void setup(void) {
    WDTCTL=WDTPW|WDTHOLD;
    if(CALBC1_1MHZ==0xFF)while(1){} /* missing calibration constants */
    DCOCTL=0;BCSCTL1=CALBC1_1MHZ;DCOCTL=CALDCO_1MHZ;
    P2SEL &= (uint8_t)~BIT0;P2DIR |= BIT0;P2OUT &= (uint8_t)~BIT0;
    P1SEL |= BIT1|BIT2;P1SEL2 |= BIT1|BIT2;
    UCA0CTL1=UCSWRST|UCSSEL_2;
    UCA0BR0=26;UCA0BR1=0;UCA0MCTL=UCBRS_0; /* 1MHz/38400 */
    UCA0CTL1 &= (uint8_t)~UCSWRST;
    IE2 |= UCA0RXIE;
    ADC10CTL0=ADC10SHT_2|ADC10ON;
    ADC10CTL1=INCH_0;
    ADC10AE0=BIT0;
    __enable_interrupt();
}
int main(void) {
    uint8_t byte;
    setup();
    for(;;) {
        service_adc();
        if(rx_overrun) {
            __disable_interrupt();rx_read=rx_write;rx_overrun=0;__enable_interrupt();
            parser.used=0;parser.errors++;
        }
        if(rx_read!=rx_write) {
            byte=rx_buf[rx_read];rx_read=(uint8_t)((rx_read+1)&(RX_SIZE-1));
            if(lab_feed(&parser,byte,&request))command(&request);
        }
    }
}
