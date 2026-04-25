#include <avr/io.h>
#include <util/delay.h>
#include <stdio.h>
#include "drivers/sound_detector.h"

static int uart_putchar(char c, FILE *stream) {
    while (!(UCSR0A & (1 << UDRE0)));
    UDR0 = c;
    return 0;
}

static FILE uart_stdout = FDEV_SETUP_STREAM(uart_putchar, NULL, _FDEV_SETUP_WRITE);

int main(void) {
    UBRR0 = 103;
    UCSR0B = (1 << TXEN0);
    UCSR0C = (1 << UCSZ01) | (1 << UCSZ00);
    stdout = &uart_stdout;

    sound_detector_init(0);
    sound_detector_set_calibration_offset(0.0f);

    while (1) {
        float db = sound_detector_read_db();
        printf("%d dB\n", (int)db);
        _delay_ms(500);
    }

    return 0;
}