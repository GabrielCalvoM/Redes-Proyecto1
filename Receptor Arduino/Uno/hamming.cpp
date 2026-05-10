#include "hamming.h"
#include <math.h>

uint16_t generarHamming(uint8_t bits) {
  uint16_t hamming = 0, extended_bits = bits, bits_mask = 0xF000;
  extended_bits <<= 8;

  for (uint8_t i = 0; i < 12; i++) {
    double exp = log((double) i + 1) / log(2.0);

    if (exp - trunc(exp) != 0.0) hamming |= extended_bits & (bits_mask >> i + 1);
  }

  for (uint8_t i = 0; i < 4; i++) {
    uint16_t valuated_bits = (extended_bits & matrix[3 - i]) >> 4;
    bool odd = false;

    for (int i = 0; i < 12; i++) {
      odd ^= valuated_bits & 1;
      valuated_bits >> 1;
    }

    if (odd) extended_bits |= bits_mask >> (uint8_t) pow(2, i);
  }

  return extended_bits;
}

bool verificarHamming(uint16_t hamming) {
  uint16_t res = 0;

  for (uint8_t i = 0; i < 4; i++) {
    uint16_t temp = matrix[i] & hamming;
    res ^= temp;
  }

  return res == 0;
}

uint8_t decodificarHamming(uint16_t hamming) {
  uint16_t bits = 0, bits_mask = 0xF000;

  for (uint8_t i = 0; i < 12; i++) {
    double exp = log((double) i + 1) / log(2.0);

    if (exp - trunc(exp) != 0.0) {
      bits |= hamming & bits_mask;
      bits_mask >>= 1;
    }
    else hamming <<= 1;
  }

  return (uint8_t) bits >> 8;
}
