// #include <SoftwareSerial.h>

// #define RX 10
// #define TX 11

// SoftwareSerial UnoSerial(RX, TX);
// long speed = 9600;
// const size_t size = 2;
// char buffer[size] = {0};
// char ter = '\0';

// void setup() {
//   Serial.begin(speed);

//   while (!Serial) {
//     ; // wait for serial port to connect. Needed for native USB port only
//   }

//   UnoSerial.begin(speed);
// }

// void loop() {
//   if (Serial.available()) {
//     Serial.readBytes(buffer, size);
//     UnoSerial.write(buffer, size);
//   }
//   if (UnoSerial.available()) {
//     UnoSerial.readBytes(buffer, size);
//     Serial.write(buffer, size);
//   }
  
//   delay(200);
// }
