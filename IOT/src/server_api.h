#pragma once
#include <stdint.h>

#ifndef DEVICE_PUBLIC_KEY
#error "DEVICE_PUBLIC_KEY not defined — set it in secrets.ini build_flags"
#endif
void server_register_device(void);
void server_start_session(void);
void server_send_pulse(void);
void server_send_data(uint8_t temp_int, uint8_t temp_dec);