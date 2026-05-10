#pragma once
#include <stdint.h>

union HammingChaing {
  uint16_t chain;

};

uint16_t matrix[4] = {
  0b0000000111110000,
  0b0001111000010000,
  0b0110011001100000,
  0b1010101010100000
};

uint16_t generarHamming(uint8_t bits);
bool verificarHamming(uint16_t hamming);
uint8_t decodificarHamming(uint16_t hamming);
