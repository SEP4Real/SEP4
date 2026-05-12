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

// Custom fakes
static const char *inject_ip = NULL;

static WIFI_ERROR_MESSAGE_t fake_get_ip(char *url, char *ip_address)
{
    (void)url;
    strcpy(ip_address, inject_ip);
    return WIFI_OK;
}

void setUp(void)
{
    inject_ip = NULL;
    RESET_FAKE(wifi_command_create_TCP_connection);
    RESET_FAKE(wifi_command_close_TCP_connection);
    RESET_FAKE(wifi_command_TCP_transmit);
    RESET_FAKE(wifi_command_get_ip_from_URL);
    FFF_RESET_HISTORY();

    inject_ip = "192.139";
    wifi_command_get_ip_from_URL_fake.custom_fake = fake_get_ip;
    http_resolve_host();
    RESET_FAKE(wifi_command_get_ip_from_URL);
}

void tearDown(void) {}

// http_resolve_host

void http_resolve_host_calls_wifi_command_get_ip_from_URL_once(void)
{
    RESET_FAKE(wifi_command_get_ip_from_URL);
    wifi_command_get_ip_from_URL_fake.return_val = WIFI_OK;
    http_resolve_host();
    TEST_ASSERT_EQUAL(1, wifi_command_get_ip_from_URL_fake.call_count);
}

void http_resolve_host_returns_ok_status_when_ok(void)
{
    RESET_FAKE(wifi_command_get_ip_from_URL);
    wifi_command_get_ip_from_URL_fake.return_val = WIFI_OK;
    WIFI_ERROR_MESSAGE_t message = http_resolve_host();
    TEST_ASSERT_EQUAL(WIFI_OK, message);
}

void http_resolve_host_returns_error_message_when_error(void)
{
    RESET_FAKE(wifi_command_get_ip_from_URL);
    wifi_command_get_ip_from_URL_fake.return_val = WIFI_FAIL;
    WIFI_ERROR_MESSAGE_t message = http_resolve_host();
    TEST_ASSERT_EQUAL(WIFI_FAIL, message);
}

void http_resolve_host_returns_response_status_when_ip_empty(void)
{
    RESET_FAKE(wifi_command_get_ip_from_URL);
    wifi_command_get_ip_from_URL_fake.custom_fake = fake_get_ip;
    WIFI_ERROR_MESSAGE_t message = http_resolve_host();
    TEST_ASSERT_EQUAL(WIFI_OK, message);
}

// http_post

void test_http_post_calls_tcp_connect(void)
{
    char rx_buf[128];
    wifi_command_create_TCP_connection_fake.return_val = WIFI_OK;
    wifi_command_TCP_transmit_fake.return_val = WIFI_OK;

    http_post("/test", "{}", rx_buf, sizeof(rx_buf));

    TEST_ASSERT_EQUAL(1, wifi_command_create_TCP_connection_fake.call_count);
}

void test_http_post_calls_tcp_transmit(void)
{
    char rx_buf[128];
    wifi_command_create_TCP_connection_fake.return_val = WIFI_OK;
    wifi_command_TCP_transmit_fake.return_val = WIFI_OK;

    http_post("/test", "{}", rx_buf, sizeof(rx_buf));

    TEST_ASSERT_EQUAL(1, wifi_command_TCP_transmit_fake.call_count);
}

void test_http_post_closes_connection_on_success(void)
{
    char rx_buf[128];
    wifi_command_create_TCP_connection_fake.return_val = WIFI_OK;
    wifi_command_TCP_transmit_fake.return_val = WIFI_OK;

    http_post("/test", "{}", rx_buf, sizeof(rx_buf));

    TEST_ASSERT_EQUAL(1, wifi_command_close_TCP_connection_fake.call_count);
}

void test_http_post_closes_connection_on_connect_fail(void)
{
    char rx_buf[128];
    wifi_command_create_TCP_connection_fake.return_val = WIFI_ERROR_NOT_RECEIVING;

    http_post("/test", "{}", rx_buf, sizeof(rx_buf));

    TEST_ASSERT_EQUAL(1, wifi_command_close_TCP_connection_fake.call_count);
}

void test_http_post_returns_error_on_connect_fail(void)
{
    char rx_buf[128];
    wifi_command_create_TCP_connection_fake.return_val = WIFI_ERROR_NOT_RECEIVING;

    WIFI_ERROR_MESSAGE_t result = http_post("/test", "{}", rx_buf, sizeof(rx_buf));

    TEST_ASSERT_EQUAL(WIFI_ERROR_NOT_RECEIVING, result);
}

void test_http_post_does_not_transmit_on_connect_fail(void)
{
    char rx_buf[128];
    wifi_command_create_TCP_connection_fake.return_val = WIFI_ERROR_NOT_RECEIVING;

    http_post("/test", "{}", rx_buf, sizeof(rx_buf));

    TEST_ASSERT_EQUAL(0, wifi_command_TCP_transmit_fake.call_count);
}

void test_http_post_closes_connection_on_transmit_fail(void)
{
    char rx_buf[128];
    wifi_command_create_TCP_connection_fake.return_val = WIFI_OK;
    wifi_command_TCP_transmit_fake.return_val = WIFI_ERROR_NOT_RECEIVING;

    http_post("/test", "{}", rx_buf, sizeof(rx_buf));

    TEST_ASSERT_EQUAL(1, wifi_command_close_TCP_connection_fake.call_count);
}

void test_http_post_returns_error_on_transmit_fail(void)
{
    char rx_buf[128];
    wifi_command_create_TCP_connection_fake.return_val = WIFI_OK;
    wifi_command_TCP_transmit_fake.return_val = WIFI_ERROR_NOT_RECEIVING;

    WIFI_ERROR_MESSAGE_t result = http_post("/test", "{}", rx_buf, sizeof(rx_buf));

    TEST_ASSERT_EQUAL(WIFI_ERROR_NOT_RECEIVING, result);
}

// http_patch

void test_http_patch_calls_tcp_connect(void)
{
    char rx_buf[128];
    wifi_command_create_TCP_connection_fake.return_val = WIFI_OK;
    wifi_command_TCP_transmit_fake.return_val = WIFI_OK;

    http_patch("/test", "{}", rx_buf, sizeof(rx_buf));

    TEST_ASSERT_EQUAL(1, wifi_command_create_TCP_connection_fake.call_count);
}

void test_http_patch_closes_connection_on_success(void)
{
    char rx_buf[128];
    wifi_command_create_TCP_connection_fake.return_val = WIFI_OK;
    wifi_command_TCP_transmit_fake.return_val = WIFI_OK;

    http_patch("/test", "{}", rx_buf, sizeof(rx_buf));

    TEST_ASSERT_EQUAL(1, wifi_command_close_TCP_connection_fake.call_count);
}

int main(void)
{
    UNITY_BEGIN();

    RUN_TEST(http_resolve_host_calls_wifi_command_get_ip_from_URL_once);
    RUN_TEST(http_resolve_host_returns_ok_status_when_ok);
    RUN_TEST(http_resolve_host_returns_error_message_when_error);
    RUN_TEST(http_resolve_host_returns_response_status_when_ip_empty);
    RUN_TEST(test_http_post_calls_tcp_connect);
    RUN_TEST(test_http_post_calls_tcp_transmit);
    RUN_TEST(test_http_post_closes_connection_on_success);
    RUN_TEST(test_http_post_closes_connection_on_connect_fail);
    RUN_TEST(test_http_post_returns_error_on_connect_fail);
    RUN_TEST(test_http_post_does_not_transmit_on_connect_fail);
    RUN_TEST(test_http_post_closes_connection_on_transmit_fail);
    RUN_TEST(test_http_post_returns_error_on_transmit_fail);
    RUN_TEST(test_http_patch_calls_tcp_connect);
    RUN_TEST(test_http_patch_closes_connection_on_success);

    return UNITY_END();
}