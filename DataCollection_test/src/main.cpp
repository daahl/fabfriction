#include <Arduino.h>
#include <math.h>

#define LEDPIN 5
int incomingByte = 0; // for incoming serial data
unsigned long measTime;
int velocity;
String msg;

void setup() {
  Serial.begin(115200);
  pinMode(LEDPIN, OUTPUT);
  digitalWrite(LEDPIN, HIGH);
}

void loop() {
  measTime = micros();
  velocity = random(0, 100);

  msg = (String)measTime + "," + (String)velocity;

  // send data only when you receive data:
  if (Serial.available() > 0) {
    // read the incoming byte:
    incomingByte = Serial.parseInt();

    if(incomingByte == 1){
      digitalWrite(LEDPIN, LOW);
      Serial.println();
    }else if(incomingByte == 2){
      digitalWrite(LEDPIN, HIGH);
      Serial.println();
    }
  }

  Serial.println(msg);
}