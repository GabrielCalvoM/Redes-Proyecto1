#include "control_flujo.h"

#include <Arduino.h>
#include <math.h>
#include "Interfaz.h"

void ControladorFlujo::inicializar() {
  Serial.end();
  Serial.begin(config.velocidad);
  while (!Serial);

  datos_size = config.payload + 7;
  // tramas    = 0;
  secuencia = 0;
  errores   = 0;

  interfaz->establecerConexion();
}

void ControladorFlujo::guardarConfig() {
  uint8_t payload = (buffer[1] & 0xC0) >> 6;
  config.payload = payload == 0 ? 100 : payload == 1 ? 400 : 1000;

  uint8_t ventanas = (buffer[1] & 0x30) >> 4;
  config.ventanas = ventanas == 0 ? 3 : ventanas == 1 ? 4 : 5;

  uint8_t velocidad = (buffer[1] & 0x0E) >> 1;
  config.velocidad = velocidad == 0 ? 4800 : velocidad == 1 ? 9600 : 19200;

  uint8_t hamming = buffer[1] & 1;
  config.hamming = hamming == 1;

  config.secuencias = ((uint16_t)buffer[2] << 8) | buffer[3];
}

void ControladorFlujo::enviarTrama() {
  if (!Serial.available()) return;

  Serial.readBytes(buffer, response_size);
  interfaz->enviarTrama(buffer);

  if (!connected) {
    delay(30);
    inicializar();
    connected = true;
    lcd->clear();
  }

  bool is_error = false;

  if (buffer[0] & 0x03 == 3) {
    secuencia -= ((uint8_t) secuencia % 256) - buffer[1];
    errores++;
    is_error = true;
  }

  if (secuencia < config.secuencias) {
    lcd->setSecuencias(secuencia, config.secuencias);
    lcd->setError(is_error);
  }
  else {
    lcd->clear();
    lcd->finalizar(errores, config.secuencias);
  }
}

void ControladorFlujo::recibirTrama() {
  bool res = interfaz->recibirTrama(buffer);

  if (!res) return;

  uint8_t type = buffer[0] & 0x03;
  if (type == 0) {
    lcd->inicializar();
    guardarConfig();
    connected = false;
  }
  if (type == 1) {
    secuencia++;
  }

  // The total frame size was populated by Interfaz::recibirTrama into datos_size
  uint16_t size = datos_size;
  Serial.write(buffer, size);
}
