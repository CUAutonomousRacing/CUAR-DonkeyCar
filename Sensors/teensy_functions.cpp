#include "teensy_functions.h"

// bool voltCheck(uint8_t pin, float cart_min, float cart_max, float filter_min, float filter_max){
//   int rawRead = analogRead(pin);
//   float voltage = (3.3f * rawRead) / 1023.0f;
//   bool flowError = (voltage < min) || (voltage > max);
//   static bool flow_check = false; 
//   Serial.println(voltage);
//   if(flowError && !flow_check){ 
//     Serial.println("WARNING: VOLTAGE ERROR");
//     if(min > voltage){
//       Serial.println("VOLTAGE TOO LOW AT ");
//       Serial.println(pin);
//     }
//     if(max < voltage){
//       Serial.println("VOLTAGE TOO HIGH AT ");
//       Serial.println(pin);
//     }
//     flow_check = true;
//     return false;
//   }

  if(!flowError){
    flow_check = false;
  }
  return true;
}

uint8_t tempCheck(uint8_t pin, float min, float max){
  float e = 2.718281828459045;
  int rawRead = analogRead(pin);
  float voltage = (rawRead / 1023.0f) * 3.3f;
  float R =10 *((3.3/ voltage) - 1.0);
  float sys_temp = 90*(pow(e,(-.13*R)));

  Serial.println(rawRead);
  Serial.println(voltage);
  Serial.println(R);
  Serial.println(sys_temp);
  Serial.print(" -> pin ");
  Serial.println(pin);
  if(sys_temp < min){
    sys_temp = min;
  }
  if(sys_temp > max){
    sys_temp = max;
  }
  return sys_temp;
}

