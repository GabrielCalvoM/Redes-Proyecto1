#pragma once

#include <stdint.h>

union HammingChaing {
  uint16_t chain;

};

extern uint16_t matrix[4];

uint16_t generarHamming(uint8_t bits);
bool verificarHamming(uint16_t hamming);
uint8_t decodificarHamming(uint16_t hamming);
