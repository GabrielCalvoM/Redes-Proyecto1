#include "control_flujo.h"
#include "Interfaz.h"

ControladorFlujo controlador;
Interfaz interfaz;

void setup() {
  interfaz.controlador = &controlador;
  controlador.interfaz = &interfaz;

  controlador.config.velocidad = 9600;
  controlador.inicializar();
}

void loop() {
  controlador.enviarTrama();
  controlador.recibirTrama();

  delay(50);
}
