#include <SPI.h>
#include <RF24.h>

RF24 radio(7, 8); // CE, CSN pins
uint8_t address[][6] = { "1Node", "2Node" };

void setup() {
  Serial.begin(115200);
  radio.begin();
  radio.openWritingPipe(1, address[0]);
  radio.setPALevel(RF24_PA_LOW);
}

void loop() {
  if (Serial.available()) {
    char data = Serial.read();
    radio.write(&data, sizeof(data));
  }
}
