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

static const char *inject_ip = NULL;

static WIFI_ERROR_MESSAGE_t fake_get_ip(char *url, char *ip_address)
{
    (void)url;
    strcpy(ip_address, inject_ip);
    return WIFI_OK;
}

static char captured_tx[512];

static WIFI_ERROR_MESSAGE_t capture_tx(uint8_t *data, uint16_t len)
{
    uint16_t n = (len < sizeof(captured_tx) - 1) ? len : sizeof(captured_tx) - 1;
    memcpy(captured_tx, data, n);
    captured_tx[n] = '\0';
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
    memset(captured_tx, 0, sizeof(captured_tx));
    inject_ip = "192.139";
    wifi_command_get_ip_from_URL_fake.custom_fake = fake_get_ip;
    http_resolve_host();
    RESET_FAKE(wifi_command_get_ip_from_URL);
}

void tearDown(void) {}


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

void http_resolve_host_returns_ok_when_ip_resolves(void)
{
    RESET_FAKE(wifi_command_get_ip_from_URL);
    wifi_command_get_ip_from_URL_fake.custom_fake = fake_get_ip;
    WIFI_ERROR_MESSAGE_t message = http_resolve_host();
    TEST_ASSERT_EQUAL(WIFI_OK, message);
}


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

void test_http_post_request_starts_with_post_method(void)
{
    char rx_buf[128];
    wifi_command_create_TCP_connection_fake.return_val = WIFI_OK;
    wifi_command_TCP_transmit_fake.custom_fake = capture_tx;

    http_post("/test", "{}", rx_buf, sizeof(rx_buf));
    TEST_ASSERT_EQUAL(0, strncmp(captured_tx, "POST /test HTTP/1.0", 19));
}

void test_http_post_request_includes_content_length_header(void)
{
    char rx_buf[128];
    const char *body = "{\"x\":42}";
    wifi_command_create_TCP_connection_fake.return_val = WIFI_OK;
    wifi_command_TCP_transmit_fake.custom_fake = capture_tx;

    http_post("/test", body, rx_buf, sizeof(rx_buf));

    TEST_ASSERT_NOT_NULL(strstr(captured_tx, "Content-Length: 8"));
}

void test_http_post_request_body_appears_after_headers(void)
{
    char rx_buf[128];
    const char *body = "{\"hello\":\"world\"}";
    wifi_command_create_TCP_connection_fake.return_val = WIFI_OK;
    wifi_command_TCP_transmit_fake.custom_fake = capture_tx;

    http_post("/test", body, rx_buf, sizeof(rx_buf));

    char *end_of_headers = strstr(captured_tx, "\r\n\r\n");
    TEST_ASSERT_NOT_NULL(end_of_headers);
    TEST_ASSERT_EQUAL_STRING(body, end_of_headers + 4);
}

// ===== http_patch =====

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

void test_http_patch_request_starts_with_patch_method(void)
{
    char rx_buf[128];
    wifi_command_create_TCP_connection_fake.return_val = WIFI_OK;
    wifi_command_TCP_transmit_fake.custom_fake = capture_tx;

    http_patch("/test", "{}", rx_buf, sizeof(rx_buf));

    TEST_ASSERT_EQUAL(0, strncmp(captured_tx, "PATCH /test HTTP/1.0", 20));
}

int main(void)
{
    UNITY_BEGIN();

    RUN_TEST(http_resolve_host_calls_wifi_command_get_ip_from_URL_once);
    RUN_TEST(http_resolve_host_returns_ok_status_when_ok);
    RUN_TEST(http_resolve_host_returns_error_message_when_error);
    RUN_TEST(http_resolve_host_returns_ok_when_ip_resolves);

    RUN_TEST(test_http_post_calls_tcp_connect);
    RUN_TEST(test_http_post_calls_tcp_transmit);
    RUN_TEST(test_http_post_closes_connection_on_success);
    RUN_TEST(test_http_post_closes_connection_on_connect_fail);
    RUN_TEST(test_http_post_returns_error_on_connect_fail);
    RUN_TEST(test_http_post_does_not_transmit_on_connect_fail);
    RUN_TEST(test_http_post_closes_connection_on_transmit_fail);
    RUN_TEST(test_http_post_returns_error_on_transmit_fail);
    RUN_TEST(test_http_post_request_starts_with_post_method);
    RUN_TEST(test_http_post_request_includes_content_length_header);
    RUN_TEST(test_http_post_request_body_appears_after_headers);

    RUN_TEST(test_http_patch_calls_tcp_connect);
    RUN_TEST(test_http_patch_closes_connection_on_success);
    RUN_TEST(test_http_patch_request_starts_with_patch_method);

    return UNITY_END();
}