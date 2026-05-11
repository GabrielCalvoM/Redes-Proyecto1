#include "control_flujo.h"

#include <Arduino.h>
#include <math.h>
#include "Interfaz.h"

uint64_t Config::calcularTimeOut() {
  double c = 100;
  double time = (payload / velocidad) * ventanas * c;
  return ceil(time * 1000);
}

void ControladorFlujo::inicializar() {
  Serial.end();
  Serial.begin(config.velocidad);

  datos_size = config.payload + 7;
  tramas = 0;
  secuencia = 0;

  interfaz->establecerConexion(); 
}

void ControladorFlujo::guardarConfig() {
  uint8_t payload = buffer[1] & 0xC0 >> 6;
  config.payload = payload == 0 ? 100 : payload == 1 ? 400 : 1000;
  
  uint8_t ventanas = buffer[1] & 0x30 >> 4;
  config.ventanas = ventanas == 0 ? 3 : ventanas == 1 ? 4 : 5;
  
  uint8_t velocidad = buffer[1] & 0x0E;
  config.velocidad = velocidad == 0 ? 4800 : velocidad == 1 ? 9600 : 19200;

  uint8_t hamming = buffer[1] & 1;
  config.hamming = hamming == 1;
  
  config.secuencias = buffer[2];
  config.secuencias <<= 8;
  config.secuencias |= buffer[3];
}

void ControladorFlujo::enviarTrama() {
  if (tramas >= config.ventanas || !Serial.available()) return;

  Serial.readBytes(buffer, datos_size);

  if (buffer[0] & 0x03 == 0) {
    guardarConfig();
    connected = false;
  }

  uint16_t size = connected ? datos_size : conexion_size;
  interfaz->enviarTrama(buffer, size);
  secuencia++;
}

void ControladorFlujo::recibirTrama() {
  if (connected && tramas < config.ventanas && secuencia < config.secuencias) return;

  tramas = 0;
  bool res = interfaz->recibirTrama(buffer);

  if (!res) {
    Serial.write(0);
    return;
  }

  Serial.write(buffer, response_size);

  if (buffer[0] & 0x03 == 3) {
    secuencia -= ((uint8_t) secuencia % 256) - buffer[1];
  }
  if (!connected) {
    delay(30);
    inicializar();
    connected = true;
  }
}
