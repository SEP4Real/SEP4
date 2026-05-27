#ifndef ARDUINO_H
#define ARDUINO_H

#include "fff.h"
#include <stdint.h>

#define HIGH 1
#define LOW 0
#define INPUT 0
#define OUTPUT 1

DECLARE_FAKE_VOID_FUNC(pinMode, int, int);
DECLARE_FAKE_VOID_FUNC(digitalWrite, int, int);
DECLARE_FAKE_VALUE_FUNC(int, digitalRead, int);
DECLARE_FAKE_VALUE_FUNC(unsigned long, millis);
DECLARE_FAKE_VOID_FUNC(delay, unsigned long);

#endif