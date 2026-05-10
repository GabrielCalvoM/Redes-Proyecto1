#include "Interfaz.h"

#include <Arduino.h>
#include "control_flujo.h"
#include "hamming.h"

void Interfaz::establecerConexion() {
  NanoSerial.end();
  NanoSerial.begin(controlador->config.velocidad);
}

void Interfaz::enviarTrama(uint8_t *buffer) {
  for (uint8_t i = 0; i < controlador->response_size; i++) {
    uint16_t chain = generarHamming(buffer[i]);
    uint8_t bytes[2];
    bytes[0] = (uint8_t) chain >> 8;
    bytes[1] = (uint8_t) chain;

    NanoSerial.write(bytes, 2);
  }
}

bool Interfaz::recibirTrama(uint8_t *buffer) {
  if (!NanoSerial.available()) return false;
  
  uint16_t hamming = 0;
  size_t readed_bytes = NanoSerial.readBytes((uint8_t*)&hamming, 2);
    
  if (readed_bytes != 2) return false;
  if (!verificarHamming(hamming)) return false;
  
  buffer[0] = decodificarHamming(hamming);
  uint16_t size = buffer[0] & 0x03 == 0 ? controlador->conexion_size : controlador->datos_size;

  for (uint16_t i = 1; Serial.available() && i < size; i++) {
    size_t readed_bytes = NanoSerial.readBytes((uint8_t*)&hamming, 2);
    
    if (readed_bytes != 2) return false;
    if (!verificarHamming(hamming)) return false;
    
    buffer[i] = decodificarHamming(hamming);
  }

  return true;
}
