#pragma once
#include <stdint.h>

class ControladorFlujo;

class Interfaz {
private:
  ControladorFlujo *controlador = nullptr;

public:
  void enviarTrama();
};