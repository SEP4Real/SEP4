#include "unity/unity.h"
#include "fakes/fff.h"
#include "../src/display_status.h"

DEFINE_FFF_GLOBALS;


FAKE_VOID_FUNC(display_setDecimals, uint8_t);
FAKE_VOID_FUNC(display_setValues, uint8_t, uint8_t, uint8_t, uint8_t);

#define CH_DASH 16

void setUp(void)
{
    RESET_FAKE(display_setDecimals);
    RESET_FAKE(display_setValues);
    FFF_RESET_HISTORY();
}

void tearDown(void) {}


void test_boot_calls_setDecimals_once(void)
{
    display_status_boot();
    TEST_ASSERT_EQUAL(1, display_setDecimals_fake.call_count);
}

void test_boot_calls_setValues_once(void)
{
    display_status_boot();
    TEST_ASSERT_EQUAL(1, display_setValues_fake.call_count);
}

void test_boot_clears_decimals(void)
{
    display_status_boot();
    TEST_ASSERT_EQUAL(0, display_setDecimals_fake.arg0_val);
}

void test_boot_shows_four_dashes(void)
{
    display_status_boot();
    TEST_ASSERT_EQUAL(CH_DASH, display_setValues_fake.arg0_val);
    TEST_ASSERT_EQUAL(CH_DASH, display_setValues_fake.arg1_val);
    TEST_ASSERT_EQUAL(CH_DASH, display_setValues_fake.arg2_val);
    TEST_ASSERT_EQUAL(CH_DASH, display_setValues_fake.arg3_val);
}


void test_idle_clears_decimals(void)
{
    display_status_idle();
    TEST_ASSERT_EQUAL(0, display_setDecimals_fake.arg0_val);
}

void test_idle_shows_expected_pattern(void)
{
    display_status_idle();
    TEST_ASSERT_EQUAL(1,  display_setValues_fake.arg0_val);
    TEST_ASSERT_EQUAL(13, display_setValues_fake.arg1_val);
    TEST_ASSERT_EQUAL(1,  display_setValues_fake.arg2_val);
    TEST_ASSERT_EQUAL(14, display_setValues_fake.arg3_val);
}


void test_session_clears_decimals(void)
{
    display_status_session();
    TEST_ASSERT_EQUAL(0, display_setDecimals_fake.arg0_val);
}

void test_session_shows_expected_pattern(void)
{
    display_status_session();
    TEST_ASSERT_EQUAL(5, display_setValues_fake.arg0_val);
    TEST_ASSERT_EQUAL(14, display_setValues_fake.arg1_val);
    TEST_ASSERT_EQUAL(5, display_setValues_fake.arg2_val);
    TEST_ASSERT_EQUAL(5, display_setValues_fake.arg3_val);
}


void test_instant_clears_decimals(void)
{
    display_status_instant();
    TEST_ASSERT_EQUAL(0, display_setDecimals_fake.arg0_val);
}

void test_instant_shows_four_eights(void)
{
    display_status_instant();
    TEST_ASSERT_EQUAL(8, display_setValues_fake.arg0_val);
    TEST_ASSERT_EQUAL(8, display_setValues_fake.arg1_val);
    TEST_ASSERT_EQUAL(8, display_setValues_fake.arg2_val);
    TEST_ASSERT_EQUAL(8, display_setValues_fake.arg3_val);
}


void test_each_status_produces_distinct_pattern(void)
{
    uint8_t boot[4], idle[4], session[4], instant[4];

    display_status_boot();
    boot[0] = display_setValues_fake.arg0_val;
    boot[1] = display_setValues_fake.arg1_val;
    boot[2] = display_setValues_fake.arg2_val;
    boot[3] = display_setValues_fake.arg3_val;

    display_status_idle();
    idle[0] = display_setValues_fake.arg0_val;
    idle[1] = display_setValues_fake.arg1_val;
    idle[2] = display_setValues_fake.arg2_val;
    idle[3] = display_setValues_fake.arg3_val;

    display_status_session();
    session[0] = display_setValues_fake.arg0_val;
    session[1] = display_setValues_fake.arg1_val;
    session[2] = display_setValues_fake.arg2_val;
    session[3] = display_setValues_fake.arg3_val;

    display_status_instant();
    instant[0] = display_setValues_fake.arg0_val;
    instant[1] = display_setValues_fake.arg1_val;
    instant[2] = display_setValues_fake.arg2_val;
    instant[3] = display_setValues_fake.arg3_val;

    TEST_ASSERT_NOT_EQUAL(0, memcmp(boot, idle, 4));
    TEST_ASSERT_NOT_EQUAL(0, memcmp(boot, session, 4));
    TEST_ASSERT_NOT_EQUAL(0, memcmp(boot, instant, 4));
    TEST_ASSERT_NOT_EQUAL(0, memcmp(idle, session, 4));
    TEST_ASSERT_NOT_EQUAL(0, memcmp(idle, instant, 4));
    TEST_ASSERT_NOT_EQUAL(0, memcmp(session, instant, 4));
}

int main(void)
{
    UNITY_BEGIN();

    RUN_TEST(test_boot_calls_setDecimals_once);
    RUN_TEST(test_boot_calls_setValues_once);
    RUN_TEST(test_boot_clears_decimals);
    RUN_TEST(test_boot_shows_four_dashes);

    RUN_TEST(test_idle_clears_decimals);
    RUN_TEST(test_idle_shows_expected_pattern);

    RUN_TEST(test_session_clears_decimals);
    RUN_TEST(test_session_shows_expected_pattern);

    RUN_TEST(test_instant_clears_decimals);
    RUN_TEST(test_instant_shows_four_eights);

    RUN_TEST(test_each_status_produces_distinct_pattern);

    return UNITY_END();
}