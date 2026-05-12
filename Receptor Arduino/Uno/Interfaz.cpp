#include "Interfaz.h"

#include <Arduino.h>
#include "control_flujo.h"
#include "hamming.h"

void Interfaz::establecerConexion() {
  NanoSerial.end();
  NanoSerial.begin(controlador->config.velocidad);
  hammingActivo = controlador->config.hamming;
}

void Interfaz::enviarTrama(uint8_t *buffer) {
  for (uint8_t i = 0; i < controlador->response_size; i++) {
    uint16_t chain = generarHamming(buffer[i]);
    NanoSerial.write((uint8_t*)chain, 2);
  }
}

bool Interfaz::recibirTrama(uint8_t *buffer) {
  if (!NanoSerial.available()) return false;
  
  uint16_t hamming = 0;
  size_t readed_bytes = NanoSerial.readBytes((uint8_t*)&hamming, 2);
    
  if (readed_bytes != 2) return false;
  
  buffer[0] = decodificarHamming(hamming);
  uint16_t size = (buffer[0] & 0x03) == 0 ? controlador->conexion_size : controlador->datos_size;

  for (uint16_t i = 1; i < size; i++) {
    size_t readed_bytes = NanoSerial.readBytes((uint8_t*)&hamming, 2);
    
    if (readed_bytes != 2) return false;
    
    buffer[i] = decodificarHamming(hamming);
  }

  return true;
}
