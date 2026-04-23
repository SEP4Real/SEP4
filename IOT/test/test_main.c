#include "unity/unity.c"
#include "fakes/Arduino.h"
#include "../src/main.h"
#include "../src/main.c"

DEFINE_FFF_GLOBALS;

DEFINE_FAKE_VOID_FUNC(pinMode, int, int);
DEFINE_FAKE_VOID_FUNC(digitalWrite, int, int);
DEFINE_FAKE_VALUE_FUNC(int, digitalRead, int);
DEFINE_FAKE_VALUE_FUNC(unsigned long, millis);
DEFINE_FAKE_VOID_FUNC(delay, unsigned long);

void setUp(void)
{
    RESET_FAKE(pinMode);
    RESET_FAKE(digitalWrite);
    RESET_FAKE(digitalRead);
    RESET_FAKE(millis);
    FFF_RESET_HISTORY();
}

void tearDown(void) {}

void test_add(void)
{
    TEST_ASSERT_EQUAL(5, add(2, 3));
    TEST_ASSERT_EQUAL(0, add(-1, 1));
}

void test_subtract(void)
{
    TEST_ASSERT_EQUAL(1, subtract(3, 2));
    TEST_ASSERT_EQUAL(-2, subtract(0, 2));
}

int main(void)
{
    UNITY_BEGIN();
    RUN_TEST(test_add);
    RUN_TEST(test_subtract);
    return UNITY_END();
}