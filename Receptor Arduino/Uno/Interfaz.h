#pragma once

#include <AltSoftSerial.h>
#include <stdint.h>

class ControladorFlujo;

class Interfaz {
private:
  AltSoftSerial NanoSerial = AltSoftSerial();

public:
  ControladorFlujo *controlador = nullptr;

  void establecerConexion();
  void enviarTrama(uint8_t *buffer);
  bool recibirTrama(uint8_t *buffer);
};