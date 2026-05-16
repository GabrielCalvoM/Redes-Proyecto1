#pragma once

#include <stdint.h>

extern uint16_t matrix[4];
extern bool hammingActivo;

uint16_t generarHamming(uint8_t bits);
void verificarHamming(uint16_t &hamming);
uint8_t decodificarHamming(uint16_t hamming);
