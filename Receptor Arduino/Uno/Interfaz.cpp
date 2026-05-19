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
  
  auto read_hamming_byte = [&](uint8_t &out_byte) -> bool {
    uint16_t hamming = 0;
    if (NanoSerial.readBytes((uint8_t*)&hamming, 2) != 2) return false;
    out_byte = decodificarHamming(hamming);
    return true;
  };

  // Read the first byte (Header)
  if (!read_hamming_byte(buffer[0])) return false;

  uint8_t type = buffer[0] & 0x03;
  uint16_t size = 0;

  if (type == 0) {
    // Connection Frame: Total 6 bytes. We read 1, need 5 more.
    size = controlador->conexion_size;
    for (uint16_t i = 1; i < size; i++) {
      if (!read_hamming_byte(buffer[i])) return false;
    }
  } else if (type == 1) {
    // Data Frame: Read Seq (1) and Size (2)
    for (uint16_t i = 1; i <= 3; i++) {
      if (!read_hamming_byte(buffer[i])) return false;
    }
    uint16_t payload_length = ((uint16_t)buffer[2] << 8) | buffer[3];
    size = 7 + payload_length;
    // Read the remaining bytes
    for (uint16_t i = 4; i < size; i++) {
      if (!read_hamming_byte(buffer[i])) return false;
    }
  } else {
    return false; // Unknown frame type
  }

  // Pass back the total read size so control_flujo knows how many to send to PC.
  // We'll update control_flujo to use this.
  controlador->datos_size = size;

  return true;
}
