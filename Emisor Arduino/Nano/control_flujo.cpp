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
  uint8_t payload = (buffer[1] & 0xC0) >> 6;
  config.payload = payload == 0 ? 100 : payload == 1 ? 400 : 1000;

  uint8_t ventanas = (buffer[1] & 0x30) >> 4;
  config.ventanas = ventanas == 0 ? 3 : ventanas == 1 ? 4 : 5;

  uint8_t velocidad = (buffer[1] & 0x0E) >> 1;
  config.velocidad = velocidad == 0 ? 4800 : velocidad == 1 ? 9600 : 19200;

  uint8_t hamming = buffer[1] & 1;
  config.hamming = hamming == 1;

  config.secuencias = buffer[2];
}

void ControladorFlujo::enviarTrama() {
  if (!Serial.available()) return;

  // Read the first byte (Header)
  buffer[0] = Serial.read();

  uint8_t type = buffer[0] & 0x03;
  uint16_t size = 0;

  if (type == 0) { 
    // Connection Frame: Total 6 bytes. We read 1, need 5 more.
    size = conexion_size;
    Serial.readBytes(&buffer[1], size - 1);
    guardarConfig();
    connected = false;
  } else if (type == 1) { 
    // Data Frame: We need to read Sequence (1) and Size (2) to know payload length.
    Serial.readBytes(&buffer[1], 3);
    uint16_t payload_length = ((uint16_t)buffer[2] << 8) | buffer[3];
    size = 7 + payload_length;
    // Read the remaining bytes (payload + checksum(2) + EOF(1))
    Serial.readBytes(&buffer[4], payload_length + 3);
  } else {
    return; // Ignore other frames
  }

  interfaz->enviarTrama(buffer, size);
  secuencia++;
}

void ControladorFlujo::recibirTrama() {
  // Simplificamos: ignorar ventanas/secuencias por ahora, solo pasar respuestas al PC
  bool res = interfaz->recibirTrama(buffer);
  if (!res) return;

  // Assuming response from Receptor is ACK(10) or NACK(11) which are 5 bytes long.
  Serial.write(buffer, response_size);

  if (!connected) {
    delay(30);
    inicializar();
    connected = true;
  }
}
