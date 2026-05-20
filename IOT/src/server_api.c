#include "server_api.h"
#include "wifi_http.h"
#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#include <avr/wdt.h>
#include <util/delay.h>
#include "buzzer.h"

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
    printf("[DEVICE] Registering device id: %s\n", DEVICE_ID);
    char body[64];
    snprintf(body, sizeof(body), "{\"id\":\"%s\"}", DEVICE_ID);
    http_post("/device", body, tcp_rx_buf, sizeof(tcp_rx_buf));
}

void server_start_session(void)
{
    char body[64];
    snprintf(body, sizeof(body), "{\"deviceId\":\"%s\"}", DEVICE_ID);

    for (uint8_t attempt = 1; attempt <= SESSION_START_RETRIES; attempt++)
    {
        printf("[SESSION] Starting (attempt %d/%d)...\n", attempt, SESSION_START_RETRIES);

        http_post("/session", body, tcp_rx_buf, sizeof(tcp_rx_buf));

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
    snprintf(endpoint, sizeof(endpoint), "/session/%ld/pulse", session_id);
    printf("[PULSE] Sending keepalive\n");

    http_patch(endpoint, "{}", tcp_rx_buf, sizeof(tcp_rx_buf));

    if (strstr(tcp_rx_buf, "\"alive\":false") != NULL || strstr(tcp_rx_buf, "\"alive\": false") != NULL)
    {
        printf("[SESSION] Server reports session %ld is dead — restarting\n", session_id);
        session_id = -1;
        server_start_session();
    }
}

void server_send_data(uint8_t temp_int, uint8_t temp_dec, uint8_t hum_int, uint8_t hum_dec, uint16_t light_raw, uint16_t co2_ppm)
{
    if (session_id < 0)
    {
        return;
    }
    char body[160];
    snprintf(body, sizeof(body), "{\"sessionId\":%ld,\"temperature\":%d.%d,\"humidity\":%d.%d,\"lightLevel\":%u,\"co2Level\":%u}", session_id, temp_int, temp_dec, hum_int, hum_dec, light_raw, co2_ppm);
    printf("[DATA] Sending temp=%d.%d, hum=%d.%d, light=%u, co2=%u\n", temp_int, temp_dec, hum_int, hum_dec, light_raw, co2_ppm);
    http_post("/data", body, tcp_rx_buf, sizeof(tcp_rx_buf));

    char *quality_ptr = strstr(tcp_rx_buf, "\"study_quality\"");
    if (quality_ptr != NULL){

        char *colon_ptr = strchr(quality_ptr, ':');
        if (colon_ptr != NULL)
        {
            int quality_val = atoi(colon_ptr + 1);
            printf("[DATA] Server returned study quality: %d\n", quality_val);
            if (quality_val == 1)
            {
                printf("[ALERT] Quality is 1 - sounding buzzer...\n");
                for (int i = 0; i < 120; i++)
                {
                    wdt_reset();
                    buzzer_beep(); 
                }
            }
            
        }
        
    }
    
}

void server_send_onetime_measurement(uint8_t temp_int, uint8_t temp_dec, uint8_t hum_int, uint8_t hum_dec, uint16_t light_raw, uint16_t co2_ppm){
    char body[150];
    snprintf(body, sizeof(body), "{\"sessionId\":1,\"temperature\":%d.%d,\"humidity\":%d.%d,\"lightLevel\":%u,\"co2Level\":%u}", temp_int, temp_dec, hum_int, hum_dec, light_raw, co2_ppm);
    printf("[ONETIME] Sending data to alternate the endpoint...\n");
    http_post("/predict", body, tcp_rx_buf, sizeof(tcp_rx_buf));
    char *quality_ptr = strstr(tcp_rx_buf, "\"study_quality\"");

    if (quality_ptr != NULL)
    {
        char *colon_ptr = strchr(quality_ptr, ':');
        if (colon_ptr != NULL)
        {
            int quality_val = atoi(colon_ptr + 1);
            printf("[ONETIME] ML returned study quality: %d\n", quality_val);

            if (quality_val == 1) 
            {
                printf("[ALERT] Bad conditions detected!\n");
                for (int i = 0; i < 120; i++) {
                    wdt_reset();
                    buzzer_beep();
                }
            }
            else 
            {
                printf("[ALERT] Good conditions.\n");
                for (int i = 0; i < 40; i++) {
                    wdt_reset();
                    buzzer_beep();
                }
            }
        }
    }
}

void server_reset(void)
{
    session_id = -1;
}
