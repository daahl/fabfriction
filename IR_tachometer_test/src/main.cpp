#include <Arduino.h>

// put function declarations here:
//int myFunction(int, int);

#define ROTPIN 13
#define TRANPIN 14
#define BAUDRATE 115200

// brighter = lower analog value
#define TOL 5
#define MID 2024

#define LINEWIDTH 0.8726389

String incomingByte; // for incoming serial data

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

    rotLastDeltaT = rotDeltaT;
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

    tranLastDeltaT = tranDeltaT;
  }

  // Assume stand still if no value change in 500 milliseconds
  if(rotLastMillis > rotNewMillis + 500*1000){
    rotLastDeltaT = 0;
  }
  if(tranLastMillis > tranNewMillis + 500*1000){
    tranLastDeltaT = 0;
  }

  // ##### PRINT ON REQUEST
  if (Serial.available() > 0) {
    // read the incoming byte:
    incomingByte = Serial.parseInt();

    if(incomingByte == "1"){
      bootTime = millis();

      // Prevent div by 0
      if(rotLastDeltaT == 0){
        rotVel = 0;
      }else{
        rotVel = LINEWIDTH / (rotLastDeltaT / 1000);
      }
      if(tranLastDeltaT == 0){
        tranVel = 0;
      }else{
        tranVel = LINEWIDTH / (tranLastDeltaT / 1000);
      }
      

      msg = (String)bootTime + "," + String(rotVel,7) + "," + String(tranVel,7);
      Serial.println(msg);
    }
  }
}