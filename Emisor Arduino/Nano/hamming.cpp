#include "hamming.h"

#include <Arduino.h>
#include <math.h>

uint16_t matrix[4] = {
  0b0000000111110000,
  0b0001111000010000,
  0b0110011001100000,
  0b1010101010100000
};

bool hammingActivo = false;

bool esPot2(uint8_t n) {
  return (n > 0) && ((n & (n - 1)) == 0);
}

uint16_t generarHamming(uint8_t bits) {
  if (!hammingActivo) return (uint16_t)bits;
  
  uint16_t hamming = 0, bits_mask = 0x8000;
  uint8_t data_cursor = 0;

  for (uint8_t i = 0; i < 12; i++) {
    uint8_t pos = i + 1;

    if (!esPot2(pos)) {
      bool bit = (bits >> data_cursor) & 1;

      if (bit) hamming |= bits_mask >> i;
      
      data_cursor++;
    }
  }

  for (uint8_t i = 0; i < 4; i++) {
    uint16_t valuated_bits = (hamming & matrix[3 - i]) >> 4;
    bool odd = false;

    for (int b = 0; b < 12; b++) {
      odd ^= valuated_bits & 1;
      valuated_bits >>= 1;
    }

    if (odd) hamming |= bits_mask >> ((1 << i) - 1);
  }

  return hamming;
}

void verificarHamming(uint16_t &hamming) {
  uint8_t pos = 0;

  for (uint8_t i = 0; i < 4; i++) {
    uint16_t temp = matrix[i] & hamming;
    uint8_t res = 0;
    pos <<= 1;

    for (uint16_t b = 0; b < 12; b++) {
      res ^= (temp >> (15 - b)) & 1;
    }

    pos |= res;
  }

  if (pos == 0) return;

  hamming ^= (uint16_t)1 << (16 - pos);
}

uint8_t decodificarHamming(uint16_t hamming) {
  if (!hammingActivo) return (uint8_t)hamming;

  verificarHamming(hamming);
  uint8_t bits = 0, bits_mask = 0x80;
  uint16_t data_cursor = 7;

  for (uint8_t i = 0; i < 12; i++) {
    uint8_t pos = i + 1;

    if (!esPot2(pos)) {
      bool bit = (hamming >> (15 - i)) & 1;

      if (bit) bits |= bits_mask >> data_cursor;

      data_cursor--;
    }
  }

  return bits;
}
