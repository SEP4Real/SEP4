#include "server_api.h"
#include "wifi_http.h"
#include <stdio.h>
#include <string.h>
#include <stdlib.h>

static long  session_id = -1;
static char  tcp_rx_buf[1024];

void server_register_device(void)
{
    printf("[DEVICE] Registering device key: %s\r\n", DEVICE_PUBLIC_KEY);
    char body[64];
    snprintf(body, sizeof(body), "{\"publicKey\":\"%s\"}", DEVICE_PUBLIC_KEY);
    http_post("/Device", body, tcp_rx_buf, sizeof(tcp_rx_buf));
}

void server_start_session(void)
{
    printf("[SESSION] Starting...\r\n");
    char body[64];
    snprintf(body, sizeof(body), "{\"deviceId\":\"%s\"}", DEVICE_PUBLIC_KEY);
    http_post("/Session", body, tcp_rx_buf, sizeof(tcp_rx_buf));

    char *p = strstr(tcp_rx_buf, "\"id\":");
    if (p)
    {
        p += 5;
        session_id = atol(p);
        printf("[SESSION] Started — ID: %ld\r\n", session_id);
    }
    else
    {
        printf("[ERROR] Could not parse session ID\r\n");
    }
}

void server_send_pulse(void)
{
    if (session_id < 0) return;
    char endpoint[32];
    snprintf(endpoint, sizeof(endpoint), "/Session/%ld/pulse", session_id);
    printf("[PULSE] Sending keepalive\r\n");
    http_patch(endpoint, "", tcp_rx_buf, sizeof(tcp_rx_buf));
}

void server_send_data(uint8_t temp_int, uint8_t temp_dec)
{
    if (session_id < 0) return;
    char body[96];
    snprintf(body, sizeof(body), "{\"sessionId\":%ld,\"temperature\":%d.%d}", session_id, temp_int, temp_dec);
    printf("[DATA] Sending temp=%d.%d\r\n", temp_int, temp_dec);
    http_post("/Data", body, tcp_rx_buf, sizeof(tcp_rx_buf));
}