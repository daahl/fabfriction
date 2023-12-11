#include <Arduino.h>

// Function declarations
void ISR1();
//void ISR2();

#define ROTPIN 13
#define TRANPIN 14
#define BAUDRATE 115200

// brighter = lower analog value
const int trigValue = 2024;
const float lineWidth = 0.8726389;

volatile float rotReading = 0;
volatile float rotLastReading = 0;
volatile int rotCount = 0;
volatile unsigned long rotTime = 0;
volatile float rotVel = 0;

volatile float tranReading = 0;
volatile int tranCount = 0;
volatile unsigned long tranTime = 0;

volatile unsigned long startTime = 0;
volatile unsigned long stopTime = 0;
volatile unsigned long countTime = 0;

String incomingByte; // for incoming serial data

String msg;

unsigned long bootTime = 0;

void setup() {
  Serial.begin(BAUDRATE);
  pinMode(ROTPIN, INPUT);
  attachInterrupt(digitalPinToInterrupt(ROTPIN), ISR1, CHANGE);
}

void loop() {
  rotReading = analogRead(ROTPIN);

  // Process measurement
  noInterrupts();
  stopTime = micros();
  countTime = stopTime - startTime;

  rotVel = (rotCount * lineWidth)/countTime;

  // Prepare next measurement loop
  rotCount = 0;
  tranCount = 0;
  startTime = micros();
  interrupts();

  // ##### PRINT ON REQUEST
  if (Serial.available() > 0) {
    // read the incoming byte:
    incomingByte = Serial.parseInt();

    if(incomingByte == "1"){
      bootTime = millis();
      
      msg = (String)bootTime + "," + String(rotVel,7);
      Serial.println(msg);
    }
  }
  
}

void ISR1() {
  /*rotLastReading = rotReading;

  if (rotReading > trigValue && rotLastReading <= trigValue) {
    // Rising edge detected
    rotCount++;
  }*/

  Serial.println("foobar");
}
