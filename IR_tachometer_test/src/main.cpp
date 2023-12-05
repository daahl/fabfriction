#include <Arduino.h>

// put function declarations here:
//int myFunction(int, int);

#define ROTPIN 13
#define TRANPIN 14
#define BAUDRATE 115200

// brighter = lower analog value
#define TOL 10
#define MID 2000

#define LINEWIDTH 0.8726389

int incomingByte = 0; // for incoming serial data

float rotReading = 0;
float rotVel = 0;
unsigned long rotLastMillis = 0;
unsigned long rotNewMillis = 0;
unsigned long rotDeltaT = 0;
unsigned long rotLastDeltaT = 0;

float tranReading = 0;
float tranVel = 0;
unsigned long tranLastMillis = 0;
unsigned long tranNewMillis = 0;
unsigned long tranDeltaT = 0;
unsigned long tranLastDeltaT = 0;

unsigned long bootTime = 0;

bool rotTrig = false;
bool tranTrig = false;

String msg;

void setup() {
  Serial.begin(BAUDRATE);
  pinMode(ROTPIN, INPUT);
  pinMode(TRANPIN, INPUT);
}

void loop() {
  // ##### ROTATION
  rotReading = analogRead(ROTPIN);

  if(rotReading < (MID - TOL) and not rotTrig){
    rotTrig = true;
    rotLastMillis = micros();
  }
  if(rotReading > (MID + TOL) and rotTrig){
    rotTrig = false;

    rotNewMillis = micros();
    rotDeltaT = rotNewMillis - rotLastMillis;
  }

  // ##### TRANSLATION
  tranReading = analogRead(TRANPIN);

  if(tranReading < (MID - TOL) and not tranTrig){
    tranTrig = true;
    tranLastMillis = micros();
  }
  if(tranReading > (MID + TOL) and tranTrig){
    tranTrig = false;

    tranNewMillis = micros();
    tranDeltaT = tranNewMillis - tranLastMillis;
  }

  // Reset on new value
  if(rotDeltaT != rotLastDeltaT){
    rotLastDeltaT = rotDeltaT;
    rotDeltaT = 0;
  }
  if(tranDeltaT != tranLastDeltaT){
    tranLastDeltaT = tranDeltaT;
    tranDeltaT = 0;
  }

  // ##### PRINT ON REQUEST
  if (Serial.available() > 0) {
    // read the incoming byte:
    incomingByte = Serial.parseInt();

    if(incomingByte == 1){
      bootTime = millis();

      rotVel = LINEWIDTH / rotDeltaT;
      tranVel = LINEWIDTH / tranDeltaT;

      msg = (String)bootTime + "," + (String)rotVel + "," + (String)tranVel;
      Serial.println(msg);
    }
  }
}