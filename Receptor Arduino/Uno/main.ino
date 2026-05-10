#include "control_flujo.h"
#include "Interfaz.h"

ControladorFlujo controlador;
Interfaz interfaz;

void setup() {
  interfaz.controlador = &controlador;
  controlador.interfaz = &interfaz;

  Serial.begin(9600);
}

void loop() {
  controlador.enviarTrama();
  controlador.recibirTrama();

  delay(50);
}
