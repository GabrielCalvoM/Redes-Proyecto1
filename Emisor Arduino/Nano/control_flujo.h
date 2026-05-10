#pragma once
#include <stdint.h>

class Interfaz;

class ControladorFlujo {
private:
  Interfaz *interfaz = nullptr;
  uint16_t tramas = 0;
  uint8_t trama_size = 0;
  uint8_t trama[1007] = {0};

public:
  float calcularTimeOut(uint8_t ventanas, uint16_t payload, uint16_t velocidad);
};
