/* 
  Spooler
*/

/* --- Headers --- */
#include <SoftwareSerial.h>
#include <Servo.h>
#define SERVO_LEFT_PIN 9
#define SERVO_RIGHT_PIN 10

/* --- Actions ---*/
const char MOVE_FORWARD = 'F';
const char MOVE_BACKWARD = 'B';
const char TURN_LEFT = 'L';
const char TURN_RIGHT = 'R';

/* --- Errors --- */
const char ERROR_NONE = 0;
const char ERROR_ACTION = 9;

/* --- Constants --- */
const int TIME_WAIT = 1000;
const int CR_SERVO_CCW = 50;
const int CR_SERVO_CW = 150;
const int CR_SERVO_STOP = 100;
const int BAUD = 9600;

/* --- Variables --- */
char action;
char error;
Servo servo_left;
Servo servo_right;

/* --- Setup --- */
void setup() {
  // Left
  servo_left.attach(SERVO_RIGHT_PIN);
  servo_left.write(CR_SERVO_STOP);
  // Right
  servo_right.attach(SERVO_LEFT_PIN);
  servo_right.write(CR_SERVO_STOP);
  // Serial
  Serial.begin(BAUD);
}

/* --- Loop --- */
void loop() {
  action = Serial.read();
  switch(action) {
    case MOVE_FORWARD:
      break;
    case MOVE_BACKWARD:
      break;
    case TURN_LEFT:
      break;
    case TURN_RIGHT:
      break;
    default:
      break;
  }
  if (error != ERROR_ACTION) {
    Serial.flush();
    delay(TIME_WAIT);
    Serial.println(error);
  }
  else {
    Serial.flush();
  }
}
