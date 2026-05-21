// #include <SoftwareSerial.h>

// #define RX 10
// #define TX 11

// SoftwareSerial NanoSerial(RX, TX);
// long speed = 9600;
// const size_t size = 6;
// char buffer[size] = {0};
// char ter = '\0';

// void setup() {
//   Serial.begin(speed);

//   while (!Serial) {


//     ; // wait for serial port to connect. Needed for native USB port only
//   }

//   NanoSerial.begin(speed);
// }

// void loop() {
//   if (Serial.available()) {
//     Serial.readBytes(buffer, size);
//     NanoSerial.write(buffer, size);
//   }
//   if (NanoSerial.available()) {
//     NanoSerial.readBytes(buffer, size);
//     Serial.write(buffer, size);
//   }
  
//   delay(200);
// }
