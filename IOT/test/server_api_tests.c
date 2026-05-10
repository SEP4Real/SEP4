#include "unity/unity.h"
#include "fakes/fff.h"
#include "../src/server_api.h"
#include "../src/wifi_http.h"
#include <string.h>

DEFINE_FFF_GLOBALS;

FAKE_VALUE_FUNC(WIFI_ERROR_MESSAGE_t, http_post, const char *, const char *, char *, uint16_t);
FAKE_VALUE_FUNC(WIFI_ERROR_MESSAGE_t, http_patch, const char *, const char *, char *, uint16_t);

// Captured argument buffers
static char captured_body[256];
static char captured_endpoint[64];
static char captured_patch_endpoint[64];

// Inject response
static const char *inject_post_response = NULL;
static const char *inject_patch_response = NULL;

// Custom fakes
static WIFI_ERROR_MESSAGE_t capture_and_inject_post(const char *endpoint,
                                                    const char *body,
                                                    char *rx_buf,
                                                    uint16_t rx_buf_size)
{
    strncpy(captured_endpoint, endpoint, sizeof(captured_endpoint) - 1);
    strncpy(captured_body, body, sizeof(captured_body) - 1);
    if (inject_post_response && rx_buf)
        strncpy(rx_buf, inject_post_response, rx_buf_size - 1);
    return WIFI_OK;
}

static WIFI_ERROR_MESSAGE_t capture_and_inject_patch(const char *endpoint,
                                                     const char *body,
                                                     char *rx_buf,
                                                     uint16_t rx_buf_size)
{
    (void)body;
    strncpy(captured_patch_endpoint, endpoint, sizeof(captured_patch_endpoint) - 1);
    if (inject_patch_response && rx_buf)
        strncpy(rx_buf, inject_patch_response, rx_buf_size - 1);
    return WIFI_OK;
}

static int retry_call_count = 0;

static WIFI_ERROR_MESSAGE_t retry_fake(const char *ep, const char *body,
                                       char *rx_buf, uint16_t rx_buf_size)
{
    (void)ep;
    (void)body;
    retry_call_count++;
    if (retry_call_count == 1)
        strncpy(rx_buf, "{\"error\":\"bad\"}", rx_buf_size - 1);
    else
        strncpy(rx_buf, "{\"id\":7}", rx_buf_size - 1);
    return WIFI_OK;
}

void setUp(void)
{
    server_reset();
    RESET_FAKE(http_post);
    RESET_FAKE(http_patch);
    FFF_RESET_HISTORY();
    inject_patch_response = NULL;
    inject_post_response = NULL;
    memset(captured_body, 0, sizeof(captured_body));
    memset(captured_endpoint, 0, sizeof(captured_endpoint));
    memset(captured_patch_endpoint, 0, sizeof(captured_patch_endpoint));
}

void tearDown(void) {}

// Starts a session with a given id
static void start_session_with_id(int id)
{
    static char response[32];
    snprintf(response, sizeof(response), "{\"id\":%d}", id);
    inject_post_response = response;
    http_post_fake.custom_fake = capture_and_inject_post;
    server_start_session();
    RESET_FAKE(http_post);
    RESET_FAKE(http_patch);
    memset(captured_body, 0, sizeof(captured_body));
    memset(captured_endpoint, 0, sizeof(captured_endpoint));
    memset(captured_patch_endpoint, 0, sizeof(captured_patch_endpoint));
    inject_post_response = NULL;
}

// server_register_device

void test_register_calls_http_post_once(void)
{
    http_post_fake.custom_fake = capture_and_inject_post;
    server_register_device();
    TEST_ASSERT_EQUAL(1, http_post_fake.call_count);
}

void test_register_posts_to_device_endpoint(void)
{
    http_post_fake.custom_fake = capture_and_inject_post;
    server_register_device();
    TEST_ASSERT_EQUAL_STRING("/Device", captured_endpoint);
}

void test_register_body_contains_id(void)
{
    http_post_fake.custom_fake = capture_and_inject_post;
    server_register_device();
    TEST_ASSERT_NOT_NULL(strstr(captured_body, DEVICE_ID));
}

void test_register_body_contains_id_field(void)
{
    http_post_fake.custom_fake = capture_and_inject_post;
    server_register_device();
    TEST_ASSERT_NOT_NULL(strstr(captured_body, "id"));
}

// server_start_session

void test_start_session_posts_to_session_endpoint(void)
{
    inject_post_response = "{\"id\":1}";
    http_post_fake.custom_fake = capture_and_inject_post;
    server_start_session();
    TEST_ASSERT_EQUAL_STRING("/Session", captured_endpoint);
}

void test_start_session_body_contains_device_id(void)
{
    inject_post_response = "{\"id\":1}";
    http_post_fake.custom_fake = capture_and_inject_post;
    server_start_session();
    TEST_ASSERT_NOT_NULL(strstr(captured_body, DEVICE_ID));
}

void test_start_session_body_contains_device_id_field(void)
{
    inject_post_response = "{\"id\":1}";
    http_post_fake.custom_fake = capture_and_inject_post;
    server_start_session();
    TEST_ASSERT_NOT_NULL(strstr(captured_body, "deviceId"));
}

void test_start_session_parses_session_id(void)
{
    inject_post_response = "{\"id\":42}";
    http_post_fake.custom_fake = capture_and_inject_post;
    server_start_session();

    RESET_FAKE(http_patch);
    http_patch_fake.custom_fake = capture_and_inject_patch;
    server_send_pulse();

    TEST_ASSERT_EQUAL(1, http_patch_fake.call_count);
    TEST_ASSERT_NOT_NULL(strstr(captured_patch_endpoint, "42"));
}

void test_start_session_retries_on_parse_fail(void)
{
    retry_call_count = 0;
    http_post_fake.custom_fake = retry_fake;
    server_start_session();
    TEST_ASSERT_EQUAL(2, http_post_fake.call_count);
}

// server_send_pulse

void test_send_pulse_is_noop_without_session(void)
{
    server_send_pulse();
    TEST_ASSERT_EQUAL(0, http_patch_fake.call_count);
}

void test_send_pulse_calls_http_patch_with_session(void)
{
    start_session_with_id(5);
    http_patch_fake.custom_fake = capture_and_inject_patch;
    server_send_pulse();
    TEST_ASSERT_EQUAL(1, http_patch_fake.call_count);
}

void test_send_pulse_endpoint_contains_session_id(void)
{
    start_session_with_id(5);
    http_patch_fake.custom_fake = capture_and_inject_patch;
    server_send_pulse();
    TEST_ASSERT_NOT_NULL(strstr(captured_patch_endpoint, "5"));
}

void test_send_pulse_endpoint_contains_pulse(void)
{
    start_session_with_id(5);
    http_patch_fake.custom_fake = capture_and_inject_patch;
    server_send_pulse();
    TEST_ASSERT_NOT_NULL(strstr(captured_patch_endpoint, "pulse"));
}

void test_send_pulse_endpoint_uses_session_path(void)
{
    start_session_with_id(5);
    http_patch_fake.custom_fake = capture_and_inject_patch;
    server_send_pulse();
    TEST_ASSERT_NOT_NULL(strstr(captured_patch_endpoint, "/Session/"));
}

void test_send_pulse_restarts_session_when_alive_false(void)
{
    start_session_with_id(9);

    inject_patch_response = "{\"alive\":false}";
    http_patch_fake.custom_fake = capture_and_inject_patch;

    inject_post_response = "{\"id\":10}";
    http_post_fake.custom_fake = capture_and_inject_post;

    printf("patch calls: %d\n", http_patch_fake.call_count);
    printf("patch endpoint: %s\n", captured_patch_endpoint);
    printf("post calls: %d\n", http_post_fake.call_count);

    server_send_pulse();

    TEST_ASSERT_EQUAL(1, http_post_fake.call_count);
}

// server_send_data

void test_send_data_is_noop_without_session(void)
{
    server_send_data(22, 5, 60, 0, 856);
    TEST_ASSERT_EQUAL(0, http_post_fake.call_count);
}

void test_send_data_calls_http_post_with_session(void)
{
    start_session_with_id(3);
    http_post_fake.custom_fake = capture_and_inject_post;
    server_send_data(22, 5, 60, 0, 856);
    TEST_ASSERT_EQUAL(1, http_post_fake.call_count);
}

void test_send_data_posts_to_data_endpoint(void)
{
    start_session_with_id(3);
    http_post_fake.custom_fake = capture_and_inject_post;
    server_send_data(22, 5, 60, 0, 856);
    TEST_ASSERT_EQUAL_STRING("/Data", captured_endpoint);
}

void test_send_data_body_contains_temperature_field(void)
{
    start_session_with_id(3);
    http_post_fake.custom_fake = capture_and_inject_post;
    server_send_data(22, 5, 60, 0, 856);
    TEST_ASSERT_NOT_NULL(strstr(captured_body, "temperature"));
}

void test_send_data_body_contains_humidity_field(void)
{
    start_session_with_id(3);
    http_post_fake.custom_fake = capture_and_inject_post;
    server_send_data(22, 5, 60, 0, 856);
    TEST_ASSERT_NOT_NULL(strstr(captured_body, "humidity"));
}

void test_send_data_body_contains_session_id_field(void)
{
    start_session_with_id(3);
    http_post_fake.custom_fake = capture_and_inject_post;
    server_send_data(22, 5, 60, 0, 856);
    TEST_ASSERT_NOT_NULL(strstr(captured_body, "sessionId"));
}

void test_send_data_body_contains_temp_values(void)
{
    start_session_with_id(3);
    http_post_fake.custom_fake = capture_and_inject_post;
    server_send_data(22, 5, 60, 0, 856);
    TEST_ASSERT_NOT_NULL(strstr(captured_body, "22"));
    TEST_ASSERT_NOT_NULL(strstr(captured_body, "5"));
}

void test_send_data_body_contains_humidity_values(void)
{
    start_session_with_id(3);
    http_post_fake.custom_fake = capture_and_inject_post;
    server_send_data(22, 5, 60, 3, 856);
    TEST_ASSERT_NOT_NULL(strstr(captured_body, "60"));
    TEST_ASSERT_NOT_NULL(strstr(captured_body, "3"));
}

void test_send_data_body_contains_light_field(void)
{
    start_session_with_id(3);
    http_post_fake.custom_fake = capture_and_inject_post;
    server_send_data(22, 5, 60, 3, 856);
    TEST_ASSERT_NOT_NULL(strstr(captured_body, "lightLevel"));
}

void test_send_data_body_contains_light_values(void)
{
    start_session_with_id(3);
    http_post_fake.custom_fake = capture_and_inject_post;
    server_send_data(22, 5, 60, 3, 856);
    TEST_ASSERT_NOT_NULL(strstr(captured_body, "856"));
}

int main(void)
{
    UNITY_BEGIN();

    RUN_TEST(test_register_calls_http_post_once);
    RUN_TEST(test_register_posts_to_device_endpoint);
    RUN_TEST(test_register_body_contains_id);
    RUN_TEST(test_register_body_contains_id_field);

    RUN_TEST(test_start_session_posts_to_session_endpoint);
    RUN_TEST(test_start_session_body_contains_device_id);
    RUN_TEST(test_start_session_body_contains_device_id_field);
    RUN_TEST(test_start_session_parses_session_id);
    RUN_TEST(test_start_session_retries_on_parse_fail);

    RUN_TEST(test_send_pulse_is_noop_without_session);
    RUN_TEST(test_send_pulse_calls_http_patch_with_session);
    RUN_TEST(test_send_pulse_endpoint_contains_session_id);
    RUN_TEST(test_send_pulse_endpoint_contains_pulse);
    RUN_TEST(test_send_pulse_endpoint_uses_session_path);
    RUN_TEST(test_send_pulse_restarts_session_when_alive_false);

    RUN_TEST(test_send_data_is_noop_without_session);
    RUN_TEST(test_send_data_calls_http_post_with_session);
    RUN_TEST(test_send_data_posts_to_data_endpoint);
    RUN_TEST(test_send_data_body_contains_temperature_field);
    RUN_TEST(test_send_data_body_contains_humidity_field);
    RUN_TEST(test_send_data_body_contains_session_id_field);
    RUN_TEST(test_send_data_body_contains_temp_values);
    RUN_TEST(test_send_data_body_contains_humidity_values);
    RUN_TEST(test_send_data_body_contains_light_field);
    RUN_TEST(test_send_data_body_contains_light_values);

    return UNITY_END();
}