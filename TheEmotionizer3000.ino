#include <SPI.h>
#include "printf.h"
#include "RF24.h"

#include <stdlib.h>
#include "Talkie.h"
#include "Vocab_US_Large.h"
#include "Vocab_Special.h"
#include "Vocab_US_TI99.h"
#include "Vocab_US_Acorn.h"
#include "Vocab_Soundbites.h"

Talkie voice(true, false);
RF24 radio(7, 8);

uint8_t address[][6] = { "1Node", "2Node" };
char emotion;

void setup() {
  Serial.begin(115200);
  while (!Serial) {
    // some boards need to wait to ensure access to serial over USB
  }
  if (!radio.begin()) {
    Serial.println(F("radio hardware is not responding!!"));
    while (1) {}  // hold in infinite loop
  }

  // Set the PA Level low to try preventing power supply related problems
  // because these examples are likely run with nodes in close proximity to
  // each other.
  radio.setPALevel(RF24_PA_LOW);  // RF24_PA_MAX is default.

  // save on transmission time by setting the radio to only transmit the
  // number of bytes we need to transmit a float
  radio.setPayloadSize(sizeof(emotion));  // float datatype occupies 4 bytes

  // set the RX address of the TX node into a RX pipe
  radio.openReadingPipe(1, address[0]);  // using pipe 1

  radio.startListening(); // put radio in RX mode
  Serial.println("Start Receiving!");
}
void loop() {
    uint8_t pipe;
    if(radio.available(&pipe)) {
      uint8_t bytes = radio.getPayloadSize();
      radio.read(&emotion, sizeof(emotion));

      Serial.print(F("Received Emotion: "));
      Serial.println(emotion);

      if(emotion=='n') { // neutral
        voice.say(spPAUSE2);
        voice.say(sp2_I);
        voice.say(spt_AM);
        voice.say(spt_GOOD);
      }

      if(emotion=='h') { // happy
        voice.say(spPAUSE2);
        voice.say(sp2_I);
        voice.say(spa_WANT);
        voice.say(sp4_TO);
        voice.say(spa_THANK);
        voice.say(sp4_YOU);
      }

      if(emotion=='s') { // sad
        voice.say(spPAUSE2);
        voice.say(sp2_I);
        voice.say(spt_AM);
        voice.say(spa_VERY);
        voice.say(sp2_NOT);
        voice.say(spt_GOOD);
      }

      if(emotion=='f') { // fear
        voice.say(spPAUSE2);
        voice.say(sp2_I);
        voice.say(spa_WANT);
        voice.say(sp4_TO);
        voice.say(spa_RUN);
      }

      if(emotion=='a') { // anger
        voice.say(spPAUSE2);
        voice.say(sp2_I);
        voice.say(spt_AM);
        voice.say(spa_VERY);
        voice.say(spa_BAD);
      }

      if(emotion=='d') { // disgust
        voice.say(spPAUSE2);
        voice.say(spa_THIS);
        voice.say(spa_IS);
        voice.say(spa_BAD);
      }

      if(emotion=='r') { // surprise
        voice.say(spPAUSE2);
        voice.say(spHMMM_BEER);
      }
    }
}
