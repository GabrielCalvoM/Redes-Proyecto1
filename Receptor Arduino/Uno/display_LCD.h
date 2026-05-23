#pragma once

#include <LiquidCrystal.h>
#include <stdint.h>

const uint8_t rs = 7, en = 6, d4 = 5, d5 = 4, d6 = 3, d7 = 2;

class DisplayLCD {
private:
  LiquidCrystal lcd = LiquidCrystal(rs, en, d4, d5, d6, d7);

public:
  void inicializar();
  void clear();
  void setError(bool is_error);
  void setSecuencias(uint16_t actual, uint16_t total);
  void finalizar(uint16_t errores, uint16_t total);
};
