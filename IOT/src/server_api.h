#pragma once
#include <stdint.h>

#define DEVICE_PUBLIC_KEY "arduino-device-01"

void server_register_device(void);
void server_start_session(void);
void server_send_pulse(void);
void server_send_data(uint8_t temp_int, uint8_t temp_dec);