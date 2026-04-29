#ifndef SOUND_DETECTOR_H
#define SOUND_DETECTOR_H

#include <stdint.h>

void sound_detector_init(uint8_t adc_channel);
float sound_detector_read_db(void);
void sound_detector_set_calibration_offset(float offset);
uint16_t adc_read(void);

#endif