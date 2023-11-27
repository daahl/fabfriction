#include <Arduino.h>

// put function declarations here:
//int myFunction(int, int);

#define APIN 13
#define BAUDRATE 115200
// brighter = lower analog value
#define UPPERB 3000
#define LOWERB 1000
#define MEASTIME 1000 // measure for 1 seconds
#define TAPEWIDTH 0.018 //m, 18 mm
#define DRILLDIAM 0.0425 //m, 42.5 mm
#define DRILLCIRCUM DRILLDIAM*3.1415 // drill circumference

float reading = 0;
float lastMillis = 0;
float newMillis = 0;
float deltaT = 0;
float RPM = 0;
float velocity = 0;
float circum = 0;
float drillT = 0;
bool triggered = false;
String msg;

void setup() {
  Serial.begin(BAUDRATE);
  pinMode(APIN, INPUT);
}

void loop() {
  reading = analogRead(APIN);

  // Measure times between triggers and calculate velocity and RPM
  if(reading < LOWERB and not triggered){
    triggered = true;
    lastMillis = millis();
  }
  if(reading > UPPERB and triggered){
    triggered = false;

    // Get time across white stripe
    newMillis = millis();
    deltaT = newMillis - lastMillis;
    deltaT = deltaT / 1000; // now in seconds

    // Time around drill
    drillT = deltaT * (DRILLCIRCUM/TAPEWIDTH);

    // Rotations per minute
    RPM = 60/drillT;
  }

  msg = "RPM: " + (String)RPM + " | dT: " + (String)deltaT; 

  Serial.println(msg);
}