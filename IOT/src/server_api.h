#pragma once
#include <stdint.h>

#define DEVICE_ID "arduino-device-01"

void server_register_device(void);
void server_start_session(void);
void server_send_pulse(void);
void server_send_data(uint8_t temp_int, uint8_t temp_dec, uint8_t hum_int, uint8_t hum_dec, uint16_t light_raw, uint16_t co2_ppm);
void server_reset(void);
void server_send_onetime_measurement(uint8_t temp_int, uint8_t temp_dec, uint8_t hum_int, uint8_t hum_dec, uint16_t light_raw, uint16_t co2_ppm);