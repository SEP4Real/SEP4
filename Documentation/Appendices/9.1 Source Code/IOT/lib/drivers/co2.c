/***********************************************
 * co2.c
 *  CO2 sensor implementation for the sensor model MH-Z19B, 
 *  which communicates over UART3. The sensor sends CO2 concentration
 *  in ppm as a 16-bit value (2 bytes).
 * 
 *  Author:  Erland Larsen
 *  Date:    2026-03-27
 *  Project: SPE4_API
 **********************************************/
#include "co2.h"
#include "uart.h"
#include <stddef.h>
#include <avr/io.h>
#include <avr/interrupt.h>

#define CO2_FRAME_SIZE 9
#define CO2_MAX_PPM 5000

static volatile uint16_t latest_co2_ppm = 0;
static volatile uint8_t co2_data_ready = 0;

static uint8_t co2_checksum(const uint8_t *frame)
{
    uint8_t checksum = 0;

    for (uint8_t i = 1; i < 8; i++)
    {
        checksum += frame[i];
    }

    return (uint8_t)(0xFF - checksum + 1);
}

void co2_uart_rx_callback(uint8_t byte)
{
    static uint8_t byte_count = 0;
    static uint8_t response[CO2_FRAME_SIZE];

    if (byte_count == 0)
    {
        if (byte != 0xFF)
        {
            return;
        }
    }
    else if (byte_count == 1 && byte != 0x86)
    {
        byte_count = (byte == 0xFF) ? 1 : 0;
        response[0] = 0xFF;
        return;
    }

    response[byte_count++] = byte;

    if (byte_count == CO2_FRAME_SIZE)
    {
        if (co2_checksum(response) == response[8])
        {
            uint16_t co2_ppm = ((uint16_t)response[2] << 8) | response[3];

            if (co2_ppm <= CO2_MAX_PPM)
            {
                latest_co2_ppm = co2_ppm;
                co2_data_ready = 1;
            }
        }

        byte_count = 0;
    }
}

co2_status_t co2_init(void)
{
    latest_co2_ppm = 0;
    co2_data_ready = 0;

    if (UART_OK == uart_init(UART3_ID, 9600, co2_uart_rx_callback, 0))
    {
        return CO2_OK;
    }

    return CO2_ERROR;
}

co2_status_t co2_request_measurement(void)
{
    uart_t status = UART_OK;
    static const uint8_t read_command[CO2_FRAME_SIZE] = {0xFF, 0x01, 0x86, 0x00, 0x00, 0x00, 0x00, 0x00, 0x79};

    for (uint8_t i = 0; i < CO2_FRAME_SIZE; i++)
    {
        if (UART_OK != uart_write_byte(UART3_ID, read_command[i]))
        {
            status = UART_ERROR_INVALID_ID;
        }
    }

    return (UART_OK == status) ? CO2_OK : CO2_ERROR;
}

co2_status_t co2_start_measure(void)
{
    return co2_request_measurement();
}

co2_status_t co2_read_ppm(uint16_t *co2_ppm)
{
    if (NULL == co2_ppm)
    {
        return CO2_ERROR;
    }

    uint8_t sreg = SREG;
    cli();

    if (!co2_data_ready)
    {
        SREG = sreg;
        return CO2_NO_DATA;
    }

    *co2_ppm = latest_co2_ppm;
    co2_data_ready = 0;

    SREG = sreg;
    return CO2_OK;
}

uint8_t co2_has_data(void)
{
    return co2_data_ready;
}
