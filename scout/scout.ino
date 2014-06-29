/*
  Scout Arduino Controller
*/

#include <Servo.h>

/* --- Prototypes --- */
void forward(void);
void backward(void);
void right(void);
void left(void);

/* --- Constants --- */
const int BOOT_DELAY = 10000;
const int LEFT_WHEEL_PIN = 9;
const int RIGHT_WHEEL_PIN = 10;
const int BAUD_RATE = 9600;
const int CLOCKWISE = 180;
const int OFF = 90;
const int COUNTER_CLOCKWISE = 0;
const char FORWARD_COMMAND = 'F';
const char BACKWARD_COMMAND = 'B';
const char LEFT_COMMAND = 'L';
const char RIGHT_COMMAND = 'R';
const int TURN_DELAY = 1000;
const int MOVE_DELAY = 500;

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
    case FORWARD_COMMAND:
      forward();
      break;
    case RIGHT_COMMAND:
      right();
      break;     
    case LEFT_COMMAND:
      left();
      break;
    case BACKWARD_COMMAND:
      backward();
      break; 
    default:
      break;
  }
}

/* --- Tread Functions --- */
void forward() {
  left_wheel.write(CLOCKWISE);
  right_wheel.write(COUNTER_CLOCKWISE);
  delay(MOVE_DELAY);
  left_wheel.write(OFF); // initialize motor off
  right_wheel.write(OFF); // initialize motor off
}

void backward() {
  left_wheel.write(COUNTER_CLOCKWISE);
  right_wheel.write(COUNTER_CLOCKWISE);
  delay(MOVE_DELAY);
  left_wheel.write(OFF); // initialize motor off
  right_wheel.write(OFF); // initialize motor off
}

void right() {
  left_wheel.write(CLOCKWISE);
  right_wheel.write(COUNTER_CLOCKWISE);
  delay(TURN_DELAY);
  left_wheel.write(OFF); // initialize motor off
  right_wheel.write(OFF); // initialize motor off
}

void left() {
  left_wheel.write(COUNTER_CLOCKWISE);
  right_wheel.write(CLOCKWISE);
  delay(TURN_DELAY);
  left_wheel.write(OFF); // initialize motor off
  right_wheel.write(OFF); // initialize motor off
}
