/***********************************************
 * co2.h
 *  CO2 sensor interface for the sensor model MH-Z19B, 
 *  which communicates over UART3. The sensor sends CO2 concentration
 *  in ppm as a 16-bit value (2 bytes).
 * 
 *  Author:  Erland Larsen
 *  Date:    2026-03-27
 *  Project: SPE4_API
 **********************************************/
#pragma once
#include <stdint.h>

typedef enum {
    CO2_OK = 0,
    CO2_ERROR,
    CO2_NO_DATA
} co2_status_t;

co2_status_t co2_init(void);
co2_status_t co2_request_measurement(void);
co2_status_t co2_start_measure(void);
co2_status_t co2_read_ppm(uint16_t *co2_ppm);
uint8_t co2_has_data(void);
