#include "display_status.h"
#include "display.h"

#define CH_DASH 16

void display_status_boot(void)
{
    display_setDecimals(0);
    display_setValues(CH_DASH, CH_DASH, CH_DASH, CH_DASH);
}

void display_status_idle(void)
{
    display_setDecimals(0);
    display_setValues(1, 13, 1, 14);
}

void display_status_session(void)
{
    display_setDecimals(0);
    display_setValues(5, 14, 5, 5);
}

void display_status_instant(void)
{
    display_setDecimals(0);
    display_setValues(8, 8, 8, 8);
}