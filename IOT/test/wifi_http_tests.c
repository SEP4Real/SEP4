#include "fakes/Arduino.h"
#include "fakes/fff.h"
#include "unity/unity.h"
#include "../src/wifi_http.h"
#include "../drivers/wifi.h"

DEFINE_FFF_GLOBALS;

FAKE_VALUE_FUNC(WIFI_ERROR_MESSAGE_t, wifi_command_get_ip_from_URL, char *, char *);
FAKE_VALUE_FUNC(WIFI_ERROR_MESSAGE_t, wifi_command_create_TCP_connection, char *, uint16_t, WIFI_TCP_Callback_t, char *);
FAKE_VALUE_FUNC(WIFI_ERROR_MESSAGE_t, wifi_command_close_TCP_connection);
FAKE_VALUE_FUNC(WIFI_ERROR_MESSAGE_t, wifi_command_TCP_transmit, uint8_t *, uint16_t);

void setUp(void)
{
    RESET_FAKE(wifi_command_get_ip_from_URL);
    FFF_RESET_HISTORY();
}

void tearDown(void) {}

// http_resolve_host

void http_resolve_host_calls_wifi_command_get_ip_from_URL_once(void)
{
    wifi_command_get_ip_from_URL_fake.return_val = WIFI_OK;
    http_resolve_host();
    TEST_ASSERT_EQUAL(1, wifi_command_get_ip_from_URL_fake.call_count);
}

int main(void)
{
    UNITY_BEGIN();
    RUN_TEST(http_resolve_host_calls_wifi_command_get_ip_from_URL_once);
    return UNITY_END();
}