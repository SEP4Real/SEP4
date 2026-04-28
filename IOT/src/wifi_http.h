#pragma once
#include <stdint.h>
#include "wifi.h"

#ifndef SERVER_IP
#error "SERVER_IP not defined — set it in secrets.ini build_flags"
#endif
#ifndef SERVER_PORT
#error "SERVER_PORT not defined — set it in secrets.ini build_flags"
#endif

WIFI_ERROR_MESSAGE_t http_post(const char *endpoint, const char *body, char *rx_buf, uint16_t rx_buf_size);
WIFI_ERROR_MESSAGE_t http_patch(const char *endpoint, const char *body, char *rx_buf, uint16_t rx_buf_size);