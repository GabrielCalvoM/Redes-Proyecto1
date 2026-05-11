#include "Interfaz.h"

#include <Arduino.h>
#include "control_flujo.h"
#include "hamming.h"

void Interfaz::establecerConexion() {
  UnoSerial.end();
  UnoSerial.begin(controlador->config.velocidad);
  UnoSerial.setTimeout(controlador->config.calcularTimeOut());
  hammingActivo = controlador->config.hamming;
}

void Interfaz::enviarTrama(uint8_t *buffer, uint16_t size) {
  for (uint16_t i = 0; i < size; i++) {
    uint16_t chain = generarHamming(buffer[i]);
    uint8_t bytes[2];
    bytes[0] = (uint8_t) chain >> 8;
    bytes[1] = (uint8_t) chain;

    UnoSerial.write(bytes, 2);
  }
}

bool Interfaz::recibirTrama(uint8_t *buffer) {
  uint16_t hamming = 0;

  for (uint8_t i = 0; i < controlador->response_size; i++) {
    size_t readed_bytes = UnoSerial.readBytes((uint8_t*)&hamming, 2);
    
    if (readed_bytes != 2) return false;

    buffer[i] = decodificarHamming(hamming);  
  }

  return true;
}
