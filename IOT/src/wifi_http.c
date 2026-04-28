#include "wifi_http.h"
#include <stdio.h>
#include <string.h>
#include <util/delay.h>
#include <avr/wdt.h>

static volatile uint8_t data_received = 0;
static char server_ip[16] = {0};

static void on_receive(void)
{
    data_received = 1;
}

WIFI_ERROR_MESSAGE_t http_resolve_host(void)
{
    printf("[DNS] Resolving %s...\n", SERVER_HOST);
    WIFI_ERROR_MESSAGE_t err = wifi_command_get_ip_from_URL((char *)SERVER_HOST, server_ip);

    if (err != WIFI_OK || server_ip[0] == '\0')
    {
        printf("[DNS] Resolution failed (%d)\n", err);
        return err;
    }

    printf("[DNS] %s -> %s\n", SERVER_HOST, server_ip);
    return WIFI_OK;
}

static WIFI_ERROR_MESSAGE_t http_request(const char *method, const char *endpoint, const char *body, char *rx_buf, uint16_t rx_buf_size)
{
    printf("[HTTP] %s %s\n", method, endpoint);

    char req[384];
    snprintf(req, sizeof(req),
        "%s %s HTTP/1.0\r\n"
        "Host: %s:%d\r\n"
        "Content-Type: application/json\r\n"
        "Content-Length: %u\r\n"
        "Connection: close\r\n"
        "\r\n%s",
        method, endpoint, SERVER_HOST, SERVER_PORT, (uint16_t)strlen(body), body);

    data_received = 0;
    memset(rx_buf, 0, rx_buf_size);

    WIFI_ERROR_MESSAGE_t err = wifi_command_create_TCP_connection((char *)SERVER_HOST, SERVER_PORT, on_receive, rx_buf);

    if (err != WIFI_OK)
    {
        printf("[ERROR] TCP connect failed (%d)\n", err);
        return err;
    }

    err = wifi_command_TCP_transmit((uint8_t *)req, (uint16_t)strlen(req));
    if (err != WIFI_OK)
    {
        printf("[ERROR] TCP transmit failed (%d)\n", err);
        wifi_command_close_TCP_connection();
        return err;
    }

    uint16_t waited = 0;
    while (!data_received && waited < 3000)
    {
        wdt_reset();
        _delay_ms(10);
        waited += 10;
    }

    wifi_command_close_TCP_connection();
    return err;
}

WIFI_ERROR_MESSAGE_t http_post(const char *endpoint, const char *body, char *rx_buf, uint16_t rx_buf_size)
{
    return http_request("POST", endpoint, body, rx_buf, rx_buf_size);
}

WIFI_ERROR_MESSAGE_t http_patch(const char *endpoint, const char *body, char *rx_buf, uint16_t rx_buf_size)
{
    return http_request("PATCH", endpoint, body, rx_buf, rx_buf_size);
}