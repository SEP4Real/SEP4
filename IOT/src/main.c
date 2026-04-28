#include <avr/io.h>
#include <avr/interrupt.h>
#include <util/delay.h>
#include <stdio.h>

#include "uart.h"
#include "wifi.h"
#include "dht11.h"
#include "timer.h"
#include "server_api.h"

#ifndef SERVER_IP
#error "SERVER_IP not defined — set it in secrets.ini build_flags"
#endif
#ifndef SERVER_PORT
#error "SERVER_PORT not defined — set it in secrets.ini build_flags"
#endif

static int uart0_putchar(char c, FILE *stream)
{
    (void)stream;
    uart_write_byte(UART0_ID, (uint8_t)c);
    return 0;
}
static FILE uart_stdout = FDEV_SETUP_STREAM(uart0_putchar, NULL, _FDEV_SETUP_WRITE);

static void delay_s(uint8_t seconds)
{
    for (uint8_t s = 0; s < seconds; s++)
        for (uint8_t m = 0; m < 100; m++)
            _delay_ms(10);
}

static volatile uint8_t pulse_due = 0;
static volatile uint8_t data_due  = 0;

static void on_pulse_timer(uint8_t id) { (void)id; pulse_due = 1; }
static void on_data_timer(uint8_t id)  { (void)id; data_due  = 1; }

int main(void)
{
    sei();

    uart_init(UART0_ID, 115200, NULL, 0);
    stdout = &uart_stdout;

    printf("\r\n=== Device boot ===\r\n");

    wifi_init();
    printf("[WIFI] Waiting for module...\r\n");
    delay_s(4);

    printf("[WIFI] Sending AT...\r\n");
    while (wifi_command_AT() != WIFI_OK) delay_s(1);
    printf("[WIFI] Module OK\r\n");

    wifi_command_disable_echo();
    wifi_command_set_mode_to_1();

    printf("[WIFI] Connecting to %s...\r\n", WIFI_SSID);
    while (wifi_command_join_AP(WIFI_SSID, WIFI_PASSWORD) != WIFI_OK)
    {
        printf("[WIFI] Retrying...\r\n");
        delay_s(2);
    }
    printf("[WIFI] Connected\r\n");

    wifi_command_set_to_single_Connection();

    server_register_device();
    server_start_session();

    int8_t pulse_timer = timer_create_sw(on_pulse_timer, 5000);
    int8_t data_timer  = timer_create_sw(on_data_timer,  10000);

    if (pulse_timer < 0 || data_timer < 0)
        printf("[ERROR] Timer creation failed\r\n");

    while (1)
    {
        if (pulse_due)
        {
            pulse_due = 0;
            server_send_pulse();
        }

        if (data_due)
        {
            data_due = 0;
            uint8_t t_int = 0, t_dec = 0, h_int = 0, h_dec = 0;
            if (dht11_get(&h_int, &h_dec, &t_int, &t_dec) == DHT11_OK)
                server_send_data(t_int, t_dec);
            else
                printf("[ERROR] DHT11 read failed\r\n");
        }
    }
}