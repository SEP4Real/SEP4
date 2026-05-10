#pragma once
#include <stdint.h>

// GPIO
static volatile uint8_t DDRL, PORTL, PINL;
static volatile uint8_t DDRB, PORTB, PINB;
static volatile uint8_t DDRC, PORTC, PINC;
static volatile uint8_t DDRD, PORTD, PIND;

// ADC
static volatile uint8_t ADMUX, ADCSRA;
static volatile uint16_t ADC;
#define REFS0 6
#define ADEN 7
#define ADSC 6
#define ADPS0 0
#define ADPS1 1
#define ADPS2 2

// Timer
static volatile uint8_t TCCR0A, TCCR0B, TIMSK0, OCR0A;
static volatile uint8_t TCCR1A, TCCR1B, TIMSK1;
static volatile uint8_t TCCR2A, TCCR2B, TIMSK2;
#define WGM01 1
#define WGM00 0
#define CS00 0
#define CS01 1
#define CS02 2
#define OCIE0A 1
#define OCIE0B 2
#define TOV0 0
#define F_CPU 16000000UL

// SREG
static uint8_t sreg_stub;
#define SREG sreg_stub

// UART — all 4 peripherals
static volatile uint8_t UBRR0H, UBRR0L, UCSR0A, UCSR0B, UCSR0C, UDR0;
static volatile uint8_t UBRR1H, UBRR1L, UCSR1A, UCSR1B, UCSR1C, UDR1;
static volatile uint8_t UBRR2H, UBRR2L, UCSR2A, UCSR2B, UCSR2C, UDR2;
static volatile uint8_t UBRR3H, UBRR3L, UCSR3A, UCSR3B, UCSR3C, UDR3;

#define U2X0 1
#define RXEN0 4
#define TXEN0 3
#define RXCIE0 7
#define UDRE0 5
#define RXC0 7
#define UCSZ00 1
#define UCSZ01 2

#define RXEN1 4
#define TXEN1 3
#define RXCIE1 7
#define UDRE1 5
#define RXC1 7
#define UCSZ10 1
#define UCSZ11 2

#define RXEN2 4
#define TXEN2 3
#define RXCIE2 7
#define UDRE2 5
#define RXC2 7
#define UCSZ20 1
#define UCSZ21 2

#define RXEN3 4
#define TXEN3 3
#define RXCIE3 7
#define UDRE3 5
#define RXC3 7
#define UCSZ30 1
#define UCSZ31 2

// Port bits
#define PL0 0
#define PL1 1
#define PL2 2
#define PL3 3
#define PL4 4
#define PL5 5
#define PL6 6
#define PL7 7

#define PB0 0
#define PB1 1
#define PB2 2
#define PB3 3
#define PB4 4
#define PB5 5
#define PB6 6
#define PB7 7

// fdev stubs
#include <stdio.h>
#define _FDEV_SETUP_RW 3
#define fdev_setup_stream(s, p, g, f) ((void)0)