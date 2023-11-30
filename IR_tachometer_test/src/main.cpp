#include <Arduino.h>

// put function declarations here:
//int myFunction(int, int);

#define APIN 13
#define BAUDRATE 115200

// brighter = lower analog value
#define TOL 50
#define MID 600

#define LINEWIDTH 0.872639 //mm

float reading = 0;
float lastMillis = 0;
float newMillis = 0;
float deltaT = 0;

bool triggered = false;

String msg;

void setup() {
  Serial.begin(BAUDRATE);
  pinMode(APIN, INPUT);
}

void loop() {

  // Measure times between triggers and calculate velocity and RPM
  while(deltaT == 0){

    reading = analogRead(APIN);

    if(reading < (MID - TOL) and not triggered){
      triggered = true;
      lastMillis = millis();
    }
    if(reading > (MID + TOL) and triggered){
      triggered = false;

      // Get time across white stripe
      newMillis = millis();
      deltaT = newMillis - lastMillis;
    }
    
  }

  Serial.println(deltaT);
  deltaT = 0;
}