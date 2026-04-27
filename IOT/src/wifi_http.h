#pragma once
#include <stdint.h>
#include "wifi.h"

#define SERVER_IP   ""
#define SERVER_PORT 8080

WIFI_ERROR_MESSAGE_t http_post(const char *endpoint, const char *body, char *rx_buf, uint16_t rx_buf_size);
WIFI_ERROR_MESSAGE_t http_patch(const char *endpoint, const char *body, char *rx_buf, uint16_t rx_buf_size);