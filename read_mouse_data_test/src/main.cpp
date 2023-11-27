#include <Arduino.h>
#include "PS2Mouse.h"
#define DATA_PIN 5
#define CLOCK_PIN 4
#define INTELLI_MOUSE 3
#define SCALING_1_TO_1 0xE6
#define RESOLUTION_8_COUNTS_PER_MM 3

PS2Mouse mouse(CLOCK_PIN, DATA_PIN);


void setup() {
  Serial.begin(115200);
  delay(50);
  mouse.high(CLOCK_PIN);
  mouse.high(DATA_PIN);
  delay(50);
  Serial.println("HIGH");

  //mouse.reset();
  //mouse.writeAndReadAck(0xFF);
  mouse.writeByte((char) 0xFF);
  Serial.println("RESET0");
  delay(50);
  // TEST
  mouse.low(CLOCK_PIN);
  Serial.println("RESET0.5");
  delay(50);
  // TEST

  mouse.readByte();
  Serial.println("RESET1");
  delay(50);

  mouse.readByte();  // self-test status
  Serial.println("RESET2");
  delay(50);

  mouse.readByte();  // mouse ID
  Serial.println("RESET3");
  delay(50);

  mouse.checkIntelliMouseExtensions();
  Serial.println("CHECK");
  delay(50);

  mouse.setResolution(RESOLUTION_8_COUNTS_PER_MM);
  Serial.println("RES");
  delay(50);

  mouse.setScaling(SCALING_1_TO_1);
  Serial.println("SCALE");
  delay(50);

  mouse.setSampleRate(40);
  Serial.println("RATE");
  delay(50);

  mouse.setRemoteMode();
  Serial.println("MODE");
  delay(50);

  delayMicroseconds(100);
}

void loop() {

    /*MouseData data = mouse.readData();
    Serial.print(data.status, BIN);
    Serial.print("\tx=");
    Serial.print(data.position.x);
    Serial.print("\ty=");
    Serial.print(data.position.y);
    Serial.print("\twheel=");
    Serial.print(data.wheel);
    Serial.println();
    delay(20);*/
}
