#include <avr/io.h>
#include <avr/interrupt.h>
#include <util/delay.h>
#include <stdio.h>

#include "uart.h"
#include "uart_stdio.h"
#include "wifi.h"
#include "wifi_http.h"
#include "dht11.h"
#include "light.h"
#include "co2.h"
#include "timer.h"
#include "server_api.h"
#include "button.h"

static void delay_s(uint8_t seconds)
{
    for (uint8_t s = 0; s < seconds; s++)
    {
        for (uint8_t m = 0; m < 100; m++)
        {
            _delay_ms(10);
        }
    }
}

static volatile uint8_t pulse_due = 0;
static volatile uint8_t data_due = 0;
static volatile uint8_t session_button_cooldown_active = 0;
static uint8_t request_in_progress = 0;

static void on_pulse_timer(uint8_t id)
{
    (void)id;
    pulse_due = 1;
}
static void on_data_timer(uint8_t id)
{
    (void)id;
    data_due = 1;
}

static void on_session_button_cooldown_timer(uint8_t id)
{
    session_button_cooldown_active = 0;
    timer_pause(id);
}

int main(void)
{
    sei();
    button_init();
    uart_stdio_init(115200);

    printf("\n=== Device boot ===\n");
    light_init();
    uint16_t latest_co2_ppm = 0;
    if (co2_init() == CO2_OK)
    {
        printf("[CO2] Sensor UART initialized\n");
        co2_request_measurement();
    }
    else
    {
        printf("[CO2] Sensor UART init failed\n");
    }

    wifi_init();
    printf("[WIFI] Waiting for module...\n");
    delay_s(4);

    printf("[WIFI] Sending AT...\n");
    while (wifi_command_AT() != WIFI_OK)
    {
        delay_s(1);
    }
    printf("[WIFI] Module OK\n");

    wifi_command_disable_echo();
    wifi_command_set_mode_to_1();

    printf("[WIFI] Connecting to %s...\n", WIFI_SSID);
    while (wifi_command_join_AP(WIFI_SSID, WIFI_PASSWORD) != WIFI_OK)
    {
        printf("[WIFI] Retrying...\n");
        delay_s(2);
    }
    printf("[WIFI] Connected\n");

    wifi_command_set_to_single_Connection();

    while (http_resolve_host() != WIFI_OK)
    {
        printf("[DNS] Retrying in 2s...\n");
        delay_s(2);
    }

    server_register_device();
    delay_s(1);
    printf("[SESSION] Waiting for Button 1 to start session\n");

    int8_t pulse_timer = timer_create_sw(on_pulse_timer, 5000);
    int8_t data_timer = timer_create_sw(on_data_timer, 30000);
    int8_t session_button_cooldown_timer = timer_create_sw(on_session_button_cooldown_timer, 20000);

    if (pulse_timer < 0 || data_timer < 0 || session_button_cooldown_timer < 0)
    {
        printf("[ERROR] Timer creation failed\n");
    }
    else
    {
        timer_pause(session_button_cooldown_timer);
    }

    static uint8_t session_active = 0;
    static uint8_t button1_last_state = 0;
    static uint8_t button2_last_state = 0;

    while (1)
    {
        uint8_t button1_current_state = button_get(1);
        uint8_t button2_current_state = button_get(2);

        if (button1_last_state == 0 && button1_current_state == 1 && !request_in_progress)
        {
            _delay_ms(50);

            if (button_get(1))
            {
                if (session_button_cooldown_active)
                {
                    printf("[SESSION] Ignored - wait 20s between start/stop actions\n");
                    button1_last_state = button1_current_state;
                    continue;
                }

                session_button_cooldown_active = 1;
                if (session_button_cooldown_timer > 0)
                {
                    timer_resume(session_button_cooldown_timer);
                }

                request_in_progress = 1;

                if (session_active)
                {
                    printf("[SESSION] Button 1 pressed - ending session\n");
                    session_active = 0;
                    server_reset();
                    pulse_due = 0;
                    data_due = 0;
                    printf("[SESSION] Session ended - pulse/data stopped\n");
                }
                else
                {
                    printf("[SESSION] Button 1 pressed - starting session\n");
                    server_start_session();
                    session_active = 1;
                    pulse_due = 0;
                    data_due = 0;
                    printf("[SESSION] Session started by button\n");
                }

                request_in_progress = 0;
            }
        }

        if (button2_last_state == 0 && button2_current_state == 1 && !request_in_progress)
        {
            _delay_ms(50);

            if (button_get(2))
            {
                request_in_progress = 1;
                printf("[ONETIME] Button 2 pressed — taking instant measurement\n");

                uint8_t t_int = 0, t_dec = 0, h_int = 0, h_dec = 0;
                uint16_t light = light_measure_raw();
                uint16_t co2   = latest_co2_ppm;

                co2_read_ppm(&co2);

                if (dht11_get(&h_int, &h_dec, &t_int, &t_dec) == DHT11_OK)
                {
                    server_send_onetime_measurement(t_int, t_dec, h_int, h_dec, light, co2);
                }
                else
                {
                    printf("[ERROR] DHT11 failed during instant measurement\n");
                }

                request_in_progress = 0;
            }
        }

        button1_last_state = button1_current_state;
        button2_last_state = button2_current_state;

        if (session_active && !request_in_progress && pulse_due)
        {
            pulse_due = 0;
            request_in_progress = 1;
            server_send_pulse();
            request_in_progress = 0;
        }

        if (session_active && !request_in_progress && data_due)
        {
            data_due = 0;
            request_in_progress = 1;
            uint8_t t_int = 0, t_dec = 0, h_int = 0, h_dec = 0;
            uint16_t current_light = light_measure_raw();
            uint16_t current_co2 = latest_co2_ppm;

            if (co2_read_ppm(&current_co2) == CO2_OK)
            {
                latest_co2_ppm = current_co2;
                printf("[CO2] ppm=%u\n", current_co2);
            }
            else
            {
                printf("[CO2] No fresh reading, using ppm=%u\n", current_co2);
            }

            co2_request_measurement();

            if (dht11_get(&h_int, &h_dec, &t_int, &t_dec) == DHT11_OK)
            {
                server_send_data(t_int, t_dec, h_int, h_dec, current_light, current_co2);
            }
            else
            {
                printf("[ERROR] DHT11 read failed\n");
            }
            request_in_progress = 0;
        }
    }
}
