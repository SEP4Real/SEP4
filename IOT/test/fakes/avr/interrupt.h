#pragma once

#define ISR(vector) void vector(void)
#define sei() ((void)0)
#define cli() ((void)0)
// SREG is defined in avr/io.h — do not redefine here