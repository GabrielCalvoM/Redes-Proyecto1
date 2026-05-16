#include "control_flujo.h"
#include "Interfaz.h"
#include "display_LCD.h"

ControladorFlujo controlador;
Interfaz interfaz;

void setup() {
  interfaz.controlador = &controlador;
  controlador.interfaz = &interfaz;

  controlador.inicializar();
}

void loop() {
  controlador.enviarTrama();
  controlador.recibirTrama();

  // delay(50);
}
