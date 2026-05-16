#include "display_LCD.h"

void DisplayLCD::inicializar() {
  lcd.begin(16, 2);
  lcd.display();
  lcd.print("Iniciando");
  lcd.setCursor(0, 1);
  lcd.print("transmision...");
  lcd.setCursor(0, 0);
}

void DisplayLCD::clear() {
  lcd.clear();
}

void DisplayLCD::setError(bool is_error) {
  lcd.setCursor(0, 1);
  lcd.print(is_error ?
            "  Estado optimo" :
            "  Estado ruidoso");
}

void DisplayLCD::setSecuencias(uint16_t actual, uint16_t total) {
  lcd.setCursor(0, 0);
  
  char buffer[17];
  float percentage = actual * 100 / total;
  sprintf(buffer, "En curso: %5s%%\0", String(percentage).begin());

  lcd.print(buffer);
}

void DisplayLCD::finalizar(uint16_t errores, uint16_t total) {
  lcd.setCursor(0, 0);
  lcd.print("Finalizado");
  
  char buffer[17];
  float percentage = errores * 100 / total;
  sprintf(buffer, "Errores:  %5s%%\0", String(percentage).begin());

  lcd.setCursor(0, 1);
  lcd.print(buffer);
}
