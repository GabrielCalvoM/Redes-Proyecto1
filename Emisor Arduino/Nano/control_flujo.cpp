#include "control_flujo.h"

float ControladorFlujo::calcularTimeOut(uint8_t ventanas, uint16_t payload, uint16_t velocidad) {
  float c = 100;
  return (payload / velocidad) * ventanas * c;
}