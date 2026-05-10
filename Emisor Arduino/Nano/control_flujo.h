#pragma once

#include <stdint.h>

class Interfaz;

struct Config {
  uint16_t payload    = 0;
  uint8_t  ventanas   = 0;
  uint16_t velocidad  = 0;
  uint16_t secuencias = 0;
  
  uint64_t calcularTimeOut();
};

class ControladorFlujo {
private:
  bool connected        = false;

  uint8_t tramas        = 0;
  uint16_t secuencia    = 0;
  uint8_t buffer[1007]  = {0};

public:
  Interfaz *interfaz = nullptr;
  Config config;

  const uint8_t conexion_size = 6;
  uint16_t datos_size   = 0;
  const uint8_t response_size = 5;

  void inicializar();
  void guardarConfig();
  void enviarTrama();
  void recibirTrama();
};
