#ifndef TEENSY_FUNCTIONS_H
#define TEENSY_FUNCTIONS_H
#include <Arduino.h>

bool voltCheck(uint8_t pin, float min, float max);
uint8_t tempCheck(uint8_t pin, float cart_min, float cart_max, float filter_min, float filter_max);

#endif