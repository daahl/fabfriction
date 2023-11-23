#include <Arduino.h>
#include <math.h>

#define LEDPIN 5
int incomingByte = 0; // for incoming serial data

void setup() {
  Serial.begin(115200);
  pinMode(LEDPIN, OUTPUT);
  digitalWrite(LEDPIN, HIGH);
}

void loop() {
  // send data only when you receive data:
  if (Serial.available() > 0) {
    // read the incoming byte:
    incomingByte = Serial.parseInt();

    if(incomingByte == 1){
      digitalWrite(LEDPIN, LOW);
      Serial.println("LED on!");
    }else if(incomingByte == 2){
      digitalWrite(LEDPIN, HIGH);
      Serial.println("LED off!");
    }
  }
  delay(100);
}