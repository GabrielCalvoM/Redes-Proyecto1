#pragma once

#include <stdint.h>
#include "display_LCD.h"

class Interfaz;

struct Config {
  uint16_t payload    = 100;
  uint8_t  ventanas   = 3;
  uint16_t velocidad  = 9600;
  bool hamming = true;
  uint16_t secuencias = 0;
};

class ControladorFlujo {
private:
  bool connected        = false;
  // uint8_t tramas        = 0;
  uint16_t secuencia    = 0;
  uint16_t errores      = 0;
  uint8_t buffer[1007]  = {0};

public:
  Interfaz *interfaz = nullptr;
  DisplayLCD *lcd = nullptr;
  Config config;

  const uint8_t conexion_size = 6;
  uint16_t datos_size   = 0;
  const uint8_t response_size = 5;

  void inicializar();
  void guardarConfig();
  void enviarTrama();
  void recibirTrama();
};