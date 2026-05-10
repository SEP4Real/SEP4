#include "server_api.h"
#include "wifi_http.h"
#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#include <avr/wdt.h>
#include <util/delay.h>

#define SESSION_START_RETRIES 5
#define SESSION_RETRY_DELAY_MS 2000

static long session_id = -1;
static char tcp_rx_buf[1024];

static void delay_ms_wdt(uint16_t ms)
{
    for (uint16_t i = 0; i < ms / 10; i++)
    {
        wdt_reset();
        _delay_ms(10);
    }
}

void server_register_device(void)
{
    printf("[DEVICE] Registering device key: %s\n", DEVICE_PUBLIC_KEY);
    char body[64];
    snprintf(body, sizeof(body), "{\"publicKey\":\"%s\"}", DEVICE_PUBLIC_KEY);
    http_post("/Device", body, tcp_rx_buf, sizeof(tcp_rx_buf));
}

void server_start_session(void)
{
    char body[64];
    snprintf(body, sizeof(body), "{\"deviceId\":\"%s\"}", DEVICE_PUBLIC_KEY);

    for (uint8_t attempt = 1; attempt <= SESSION_START_RETRIES; attempt++)
    {
        printf("[SESSION] Starting (attempt %d/%d)...\n", attempt, SESSION_START_RETRIES);

        http_post("/Session", body, tcp_rx_buf, sizeof(tcp_rx_buf));

        char *p = strstr(tcp_rx_buf, "\"id\":");
        if (p)
        {
            p += 5;
            session_id = atol(p);
            if (session_id > 0)
            {
                printf("[SESSION] Started — ID: %ld\n", session_id);
                return;
            }
        }

        printf("[SESSION] Parse failed — response: %s\n", tcp_rx_buf);

        if (attempt < SESSION_START_RETRIES)
            delay_ms_wdt(SESSION_RETRY_DELAY_MS);
    }

    printf("[ERROR] Could not start session after %d attempts — rebooting\n", SESSION_START_RETRIES);
    wdt_enable(WDTO_30MS);
    while (1)
    {
    }
}

void server_send_pulse(void)
{
    if (session_id < 0)
        return;

    char endpoint[32];
    snprintf(endpoint, sizeof(endpoint), "/Session/%ld/pulse", session_id);
    printf("[PULSE] Sending keepalive\n");

    http_patch(endpoint, "{}", tcp_rx_buf, sizeof(tcp_rx_buf));

    if (strstr(tcp_rx_buf, "\"alive\":false") != NULL || strstr(tcp_rx_buf, "\"alive\": false") != NULL)
    {
        printf("[SESSION] Server reports session %ld is dead — restarting\n", session_id);
        session_id = -1;
        server_start_session();
    }
}

void server_send_data(uint8_t temp_int, uint8_t temp_dec, uint8_t hum_int, uint8_t hum_dec, uint16_t light_raw)
{
    if (session_id < 0){
        return;
    }
    char body[128];
    snprintf(body, sizeof(body), "{\"sessionId\":%ld,\"temperature\":%d.%d,\"humidity\":%d.%d,\"lightLevel\":%u}", session_id, temp_int, temp_dec, hum_int, hum_dec, light_raw);
    printf("[DATA] Sending temp=%d.%d, hum=%d.%d, light=%u\n", temp_int, temp_dec, hum_int, hum_dec, light_raw);
    http_post("/Data", body, tcp_rx_buf, sizeof(tcp_rx_buf));
}

void server_reset(void)
{
    session_id = -1;
}