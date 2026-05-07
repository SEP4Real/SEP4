#include "unity/unity.h"
#include "wifi_http.h"
#include "wifi.h"
#include "fakes/fff.h"

DEFINE_FFF_GLOBALS;

FAKE_VALUE_FUNC(WIFI_ERROR_MESSAGE_t, http_post, const char *, const char *, char *, uint16_t);
FAKE_VALUE_FUNC(WIFI_ERROR_MESSAGE_t, http_patch, const char *, const char *, char *, uint16_t)

#include "server_api.h"

static const char *inject_response = NULL;

static WIFI_ERROR_MESSAGE_t http_post_inject(const char *endpoint,
                                             const char *body,
                                             char *out_buf,
                                             uint16_t out_len)
{
    (void)endpoint;
    (void)body;
    if (inject_response && out_buf)
        strncpy(out_buf, inject_response, out_len - 1);
    return WIFI_OK;
}

void setUp(void)
{
    RESET_FAKE(http_post);
    RESET_FAKE(http_patch);
    FFF_RESET_HISTORY();
    inject_response = NULL;

    http_post_fake.custom_fake = http_post_inject;
    server_start_session();
    RESET_FAKE(http_post);
}

void tearDown(void) {}

/*  server_register_device                                               */

void test_register_calls_http_post_once(void)
{
    server_register_device();
    TEST_ASSERT_EQUAL(1, http_post_fake.call_count);
}

void test_register_posts_to_device_endpoint(void)
{
    server_register_device();
    TEST_ASSERT_EQUAL_STRING("/Device", http_post_fake.arg0_val);
}

void test_register_body_contains_public_key(void)
{
    server_register_device();
    TEST_ASSERT_NOT_NULL(strstr(http_post_fake.arg1_val, DEVICE_PUBLIC_KEY));
}

void test_register_body_is_valid_json_shape(void)
{
    server_register_device();
    const char *body = http_post_fake.arg1_val;
    TEST_ASSERT_NOT_NULL(strchr(body, '{'));
    TEST_ASSERT_NOT_NULL(strchr(body, '}'));
    TEST_ASSERT_NOT_NULL(strstr(body, "\"publicKey\""));
}

/*  server_start_session                                               */

void test_start_session_calls_http_post_once(void)
{
    server_start_session();
    TEST_ASSERT_EQUAL(1, http_post_fake.call_count);
}

void test_start_session_posts_to_session_endpoint(void)
{
    server_start_session();
    TEST_ASSERT_EQUAL_STRING("/Session", http_post_fake.arg0_val);
}

void test_start_session_body_contains_device_id(void)
{
    server_start_session();
    TEST_ASSERT_NOT_NULL(strstr(http_post_fake.arg1_val, DEVICE_PUBLIC_KEY));
}

void test_start_session_parses_id_from_response(void)
{
    inject_response = "{\"id\":42,\"status\":\"ok\"}";
    http_post_fake.custom_fake = http_post_inject;

    server_start_session();

    server_send_pulse();
    TEST_ASSERT_EQUAL(1, http_patch_fake.call_count);
    TEST_ASSERT_NOT_NULL(strstr(http_patch_fake.arg0_val, "42"));
}

void test_start_session_handles_missing_id_field(void)
{
    inject_response = "{\"error\":\"bad request\"}";
    http_post_fake.custom_fake = http_post_inject;

    server_start_session();

    server_send_pulse();
    TEST_ASSERT_EQUAL(0, http_patch_fake.call_count);
}

void test_start_session_handles_empty_response(void)
{
    inject_response = "";
    http_post_fake.custom_fake = http_post_inject;

    server_start_session();

    server_send_pulse();
    TEST_ASSERT_EQUAL(0, http_patch_fake.call_count);
}

/*  server_send_pulse                                                  */

void test_send_pulse_is_noop_without_session(void)
{
    server_send_pulse();
    TEST_ASSERT_EQUAL(0, http_patch_fake.call_count);
}

void test_send_pulse_calls_http_patch_once_with_session(void)
{
    inject_response = "{\"id\":7}";
    http_post_fake.custom_fake = http_post_inject;
    server_start_session();
    RESET_FAKE(http_post);

    server_send_pulse();
    TEST_ASSERT_EQUAL(1, http_patch_fake.call_count);
}

void test_send_pulse_endpoint_contains_session_id(void)
{
    inject_response = "{\"id\":99}";
    http_post_fake.custom_fake = http_post_inject;
    server_start_session();

    server_send_pulse();
    TEST_ASSERT_NOT_NULL(strstr(http_patch_fake.arg0_val, "99"));
}

void test_send_pulse_endpoint_contains_pulse_path(void)
{
    inject_response = "{\"id\":1}";
    http_post_fake.custom_fake = http_post_inject;
    server_start_session();

    server_send_pulse();
    TEST_ASSERT_NOT_NULL(strstr(http_patch_fake.arg0_val, "pulse"));
}

void test_send_pulse_uses_session_path_format(void)
{
    inject_response = "{\"id\":5}";
    http_post_fake.custom_fake = http_post_inject;
    server_start_session();

    server_send_pulse();
    /* Expect something like /Session/5/pulse */
    TEST_ASSERT_NOT_NULL(strstr(http_patch_fake.arg0_val, "/Session/"));
}

/*  server_send_data                                                   */

void test_send_data_is_noop_without_session(void)
{
    server_send_data(23, 5);
    TEST_ASSERT_EQUAL(0, http_post_fake.call_count);
}

void test_send_data_calls_http_post_once_with_session(void)
{
    inject_response = "{\"id\":3}";
    http_post_fake.custom_fake = http_post_inject;
    server_start_session();
    RESET_FAKE(http_post);

    server_send_data(22, 7);
    TEST_ASSERT_EQUAL(1, http_post_fake.call_count);
}

void test_send_data_body_contains_temperature_int_part(void)
{
    inject_response = "{\"id\":3}";
    http_post_fake.custom_fake = http_post_inject;
    server_start_session();
    RESET_FAKE(http_post);

    server_send_data(22, 7);
    TEST_ASSERT_NOT_NULL(strstr(http_post_fake.arg1_val, "22"));
}

void test_send_data_body_contains_temperature_dec_part(void)
{
    inject_response = "{\"id\":3}";
    http_post_fake.custom_fake = http_post_inject;
    server_start_session();
    RESET_FAKE(http_post);

    server_send_data(22, 7);
    TEST_ASSERT_NOT_NULL(strstr(http_post_fake.arg1_val, "7"));
}

void test_send_data_body_contains_session_id(void)
{
    inject_response = "{\"id\":55}";
    http_post_fake.custom_fake = http_post_inject;
    server_start_session();
    RESET_FAKE(http_post);

    server_send_data(20, 0);
    TEST_ASSERT_NOT_NULL(strstr(http_post_fake.arg1_val, "55"));
}

void test_send_data_posts_to_data_endpoint(void)
{
    inject_response = "{\"id\":3}";
    http_post_fake.custom_fake = http_post_inject;
    server_start_session();
    RESET_FAKE(http_post);

    server_send_data(10, 0);
    TEST_ASSERT_EQUAL_STRING("/Data", http_post_fake.arg0_val);
}

void test_send_data_body_contains_session_id_key(void)
{
    inject_response = "{\"id\":3}";
    http_post_fake.custom_fake = http_post_inject;
    server_start_session();
    RESET_FAKE(http_post);

    server_send_data(10, 5);
    TEST_ASSERT_NOT_NULL(strstr(http_post_fake.arg1_val, "sessionId"));
}

void test_send_data_body_contains_temperature_key(void)
{
    inject_response = "{\"id\":3}";
    http_post_fake.custom_fake = http_post_inject;
    server_start_session();
    RESET_FAKE(http_post);

    server_send_data(10, 5);
    TEST_ASSERT_NOT_NULL(strstr(http_post_fake.arg1_val, "temperature"));
}

int main(void)
{
    UNITY_BEGIN();

    /* register */
    RUN_TEST(test_register_calls_http_post_once);
    RUN_TEST(test_register_posts_to_device_endpoint);
    RUN_TEST(test_register_body_contains_public_key);
    RUN_TEST(test_register_body_is_valid_json_shape);

    /* start_session */
    RUN_TEST(test_start_session_calls_http_post_once);
    RUN_TEST(test_start_session_posts_to_session_endpoint);
    RUN_TEST(test_start_session_body_contains_device_id);
    RUN_TEST(test_start_session_parses_id_from_response);
    RUN_TEST(test_start_session_handles_missing_id_field);
    RUN_TEST(test_start_session_handles_empty_response);

    /* send_pulse */
    RUN_TEST(test_send_pulse_is_noop_without_session);
    RUN_TEST(test_send_pulse_calls_http_patch_once_with_session);
    RUN_TEST(test_send_pulse_endpoint_contains_session_id);
    RUN_TEST(test_send_pulse_endpoint_contains_pulse_path);
    RUN_TEST(test_send_pulse_uses_session_path_format);

    /* send_data */
    RUN_TEST(test_send_data_is_noop_without_session);
    RUN_TEST(test_send_data_calls_http_post_once_with_session);
    RUN_TEST(test_send_data_body_contains_temperature_int_part);
    RUN_TEST(test_send_data_body_contains_temperature_dec_part);
    RUN_TEST(test_send_data_body_contains_session_id);
    RUN_TEST(test_send_data_posts_to_data_endpoint);
    RUN_TEST(test_send_data_body_contains_session_id_key);
    RUN_TEST(test_send_data_body_contains_temperature_key);

    return UNITY_END();
}