#include <AFMotor.h>
#include <Servo.h>

/* --- Constants --- */
const int LEFT_TREAD_MOTOR = 1;
const int RIGHT_TREAD_MOTOR = 2;
const int BAUD_RATE = 9600;
const int MOTOR_SPEED = 200;
const char MOVE_FORWARD = '1';
const char MOVE_BACKWARD = '2';
const char TURN_LEFT = '3';
const char TURN_RIGHT = '4';
const char BOOM_RIGHT = '5';
const char BOOM_LEFT = '6';
const char BOOM_CENTER = '7';
const int TURN_DELAY = 1000;
const int MOVE_DELAY = 500;
const int BOOM_PIN = 10;
const int DEGREES_RIGHT=141;
const int DEGREES_LEFT=25;
const int DEGREES_CENTER=83;
const int BOOM_DELAY = 100;

/* --- Objects --- */
AF_DCMotor left_tread(LEFT_TREAD_MOTOR);
AF_DCMotor right_tread(RIGHT_TREAD_MOTOR);
Servo boom;
int COMMAND;

/* --- Setup --- */
void setup() {
  Serial.begin(BAUD_RATE);
  left_tread.setSpeed(MOTOR_SPEED);
  right_tread.setSpeed(MOTOR_SPEED);
  left_tread.run(RELEASE); // initialize motor off
  right_tread.run(RELEASE); // initialize motor off
  boom.attach(BOOM_PIN);
}

void loop() {
  
  // Check for incoming byte from USB
  COMMAND = Serial.read();
  
  // Execute command
  switch (COMMAND) {
    case MOVE_FORWARD:
      move_forward();
      break;
    case MOVE_BACKWARD:
      move_backward();
      break;
    case TURN_RIGHT:
      turn_right();
      break;
    case TURN_LEFT:
      turn_left();
      break;
    case BOOM_RIGHT:
      boom_right();
      break;
    case BOOM_LEFT:
      boom_left();
      break;  
    case BOOM_CENTER:
      boom_center();
      break;   
    default:
      break;
  }
}

/* --- Tread Functions --- */
void move_forward() {
  left_tread.run(FORWARD);
  right_tread.run(BACKWARD);
  delay(MOVE_DELAY);
  left_tread.run(RELEASE); // initialize motor off
  right_tread.run(RELEASE); // initialize motor off
}

void move_backward() {
  left_tread.run(BACKWARD);
  right_tread.run(FORWARD);
  delay(MOVE_DELAY);
  left_tread.run(RELEASE); // initialize motor off
  right_tread.run(RELEASE); // initialize motor off
}

void turn_right() {
  left_tread.run(BACKWARD);
  right_tread.run(BACKWARD);
  delay(TURN_DELAY);
  left_tread.run(RELEASE); // initialize motor off
  right_tread.run(RELEASE); // initialize motor off
}

void turn_left() {
  left_tread.run(FORWARD);
  right_tread.run(FORWARD);
  delay(TURN_DELAY);
  left_tread.run(RELEASE); // initialize motor off
  right_tread.run(RELEASE); // initialize motor off
}

/* --- Boom --- */
void boom_right() {
  boom.write(DEGREES_RIGHT);
  delay(BOOM_DELAY);
}

void boom_left() {
  boom.write(DEGREES_LEFT);
  delay(BOOM_DELAY);  
}

void boom_center() {
  boom.write(DEGREES_CENTER);
  delay(BOOM_DELAY);  
}

