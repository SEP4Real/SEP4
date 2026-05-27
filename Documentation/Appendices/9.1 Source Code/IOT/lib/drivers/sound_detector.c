#include "sound_detector.h"
#include <avr/io.h>
#include <math.h>
#include <util/delay.h>

static uint8_t sound_adc_channel = 0;
static float calibration_offset = 0.0f;

void sound_detector_init(uint8_t adc_channel)
{
    sound_adc_channel = adc_channel;
    ADMUX = (1 << REFS0);
    ADCSRA = (1 << ADEN) | (1 << ADPS2) | (1 << ADPS1) | (1 << ADPS0);
}

uint16_t adc_read(void)
{
    ADMUX = (ADMUX & 0xF0) | (sound_adc_channel & 0x07);
    ADCSRA |= (1 << ADSC);
    while (ADCSRA & (1 << ADSC));
    return ADC;
}

float sound_detector_read_db(void)
{
    uint32_t sum_squares = 0;
    for (uint8_t i = 0; i < 128; i++) {
        int16_t sample = (int16_t)adc_read() - 512;
        sum_squares += (uint32_t)(sample * sample);
        _delay_us(200);
    }
    float rms = sqrtf((float)sum_squares / 128.0f);
    if (rms < 1.0f) rms = 1.0f;
    return 20.0f * log10f(rms) + calibration_offset;
} 


void sound_detector_set_calibration_offset(float offset)
{
    calibration_offset = offset;
}