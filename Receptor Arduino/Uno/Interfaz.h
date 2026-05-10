#pragma once

#include <SoftwareSerial.h>
#include <stdint.h>

#define RX 10
#define TX 11

class ControladorFlujo;

class Interfaz {
private:
  SoftwareSerial NanoSerial = SoftwareSerial(RX, TX);

public:
  ControladorFlujo *controlador = nullptr;

  void establecerConexion();
  void enviarTrama(uint8_t *buffer);
  bool recibirTrama(uint8_t *buffer);
};