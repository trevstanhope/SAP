/*
  Scout Arduino Controller
*/

#include <Servo.h>

/* --- Prototypes --- */
void forward_coarse(void);
void forward_fine(void);
void backward_coarse(void);
void backward_fine(void);
void right_coarse(void);
void right_fine(void);
void left_coarse(void);
void left_fine(void);

/* --- Constants --- */
const int BOOT_DELAY = 10000;
const int LEFT_WHEEL_PIN = 9;
const int RIGHT_WHEEL_PIN = 10;
const int BAUD_RATE = 9600;
const int CLOCKWISE = 180;
const int OFF = 90;
const int COUNTER_CLOCKWISE = 0;
const char FORWARD_COARSE = 'F';
const char FORWARD_FINE = 'f';
const char BACKWARD_COARSE = 'B';
const char BACKWARD_FINE = 'b';
const char LEFT_COARSE = 'L';
const char LEFT_FINE = 'l';
const char RIGHT_COARSE = 'R';
const char RIGHT_FINE = 'r';
const int COARSE_TURN_DELAY = 2000;
const int FINE_TURN_DELAY = 1000;
const int COARSE_MOVE_DELAY = 1000;
const int FINE_MOVE_DELAY = 500;

/* --- Objects --- */
Servo left_wheel;
Servo right_wheel;
int COMMAND;

/* --- Setup --- */
void setup() {
  delay(BOOT_DELAY);
  Serial.begin(BAUD_RATE);
  left_wheel.attach(LEFT_WHEEL_PIN);
  right_wheel.attach(RIGHT_WHEEL_PIN);
}

void loop() {
  
  // Check for incoming byte from USB
  COMMAND = Serial.read();
  
  // Execute command
  switch (COMMAND) {
    case FORWARD_COARSE:
      forward_coarse();
      break;
    case FORWARD_FINE:
      forward_fine();
      break;
    case RIGHT_COARSE:
      right_coarse();
      break;
    case RIGHT_FINE:
      right_fine();
      break;      
    case LEFT_COARSE:
      left_coarse();
      break;
    case LEFT_FINE:
      left_fine();
      break;
    case BACKWARD_COARSE:
      backward_coarse();
      break;
    case BACKWARD_FINE:
      backward_fine();
      break;  
    default:
      break;
  }
}

/* --- Tread Functions --- */
void forward_coarse() {
  left_wheel.write(CLOCKWISE);
  right_wheel.write(COUNTER_CLOCKWISE);
  delay(COARSE_MOVE_DELAY);
  left_wheel.write(OFF); // initialize motor off
  right_wheel.write(OFF); // initialize motor off
}

void forward_fine() {
  left_wheel.write(CLOCKWISE);
  right_wheel.write(COUNTER_CLOCKWISE);
  delay(FINE_MOVE_DELAY);
  left_wheel.write(OFF); // initialize motor off
  right_wheel.write(OFF); // initialize motor off
}

void backward_coarse() {
  left_wheel.write(COUNTER_CLOCKWISE);
  right_wheel.write(COUNTER_CLOCKWISE);
  delay(COARSE_MOVE_DELAY);
  left_wheel.write(OFF); // initialize motor off
  right_wheel.write(OFF); // initialize motor off
}

void backward_fine() {
  left_wheel.write(COUNTER_CLOCKWISE);
  right_wheel.write(COUNTER_CLOCKWISE);
  delay(FINE_MOVE_DELAY);
  left_wheel.write(OFF); // initialize motor off
  right_wheel.write(OFF); // initialize motor off
}

void right_coarse() {
  left_wheel.write(CLOCKWISE);
  right_wheel.write(COUNTER_CLOCKWISE);
  delay(COARSE_TURN_DELAY);
  left_wheel.write(OFF); // initialize motor off
  right_wheel.write(OFF); // initialize motor off
}

void right_fine() {
  left_wheel.write(CLOCKWISE);
  right_wheel.write(COUNTER_CLOCKWISE);
  delay(FINE_TURN_DELAY);
  left_wheel.write(OFF); // initialize motor off
  right_wheel.write(OFF); // initialize motor off
}

void left_coarse() {
  left_wheel.write(COUNTER_CLOCKWISE);
  right_wheel.write(CLOCKWISE);
  delay(COARSE_TURN_DELAY);
  left_wheel.write(OFF); // initialize motor off
  right_wheel.write(OFF); // initialize motor off
}

void left_fine() {
  left_wheel.write(COUNTER_CLOCKWISE);
  right_wheel.write(CLOCKWISE);
  delay(FINE_TURN_DELAY);
  left_wheel.write(OFF); // initialize motor off
  right_wheel.write(OFF); // initialize motor off
}
