#include <AFMotor.h>
#include <Servo.h>

/* --- Prototypes --- */
void forward(void);
void backward(void);
void right(void);
void left(void);
void boom_right(void);
void boom_left(void);
void boom_center(void);
void drop(void);

/* --- Constants --- */
const int BOOT_DELAY = 10000;
const int LEFT_TREAD_MOTOR = 1;
const int RIGHT_TREAD_MOTOR = 2;
const int BAUD_RATE = 9600;
const int MOTOR_SPEED = 100;
const char FORWARD_COMMAND = 'F';
const char BACKWARD_COMMAND = 'B';
const char LEFT_COMMAND = 'L';
const char RIGHT_COMMAND = 'R';
const char BOOM_RIGHT_COMMAND = 'S';
const char BOOM_LEFT_COMMAND = 'P';
const char BOOM_CENTER_COMMAND = 'C';
const char DROP_COMMAND = 'D';
const int TURN_DELAY = 1000;
const int MOVE_DELAY = 500;
const int BOOM_PIN = 10;
const int DEGREES_RIGHT = 141;
const int DEGREES_LEFT = 25;
const int DEGREES_CENTER = 83;
const int BOOM_DELAY = 100;
const int DROP_DELAY = 100;

/* --- Objects --- */
AF_DCMotor left_tread(LEFT_TREAD_MOTOR);
AF_DCMotor right_tread(RIGHT_TREAD_MOTOR);
Servo boom;
int COMMAND;

/* --- Setup --- */
void setup() {
  delay(BOOT_DELAY);
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
    case BOOM_RIGHT_COMMAND:
      boom_right();
      break;
    case BOOM_LEFT_COMMAND:
      boom_left();
      break;  
    case BOOM_CENTER_COMMAND:
      boom_center();
      break;  
    case DROP_COMMAND:
      drop();
      break; 
    default:
      break;
  }
}

/* --- Tread Functions --- */
void forward() {
  left_tread.run(FORWARD);
  right_tread.run(FORWARD);
  delay(MOVE_DELAY);
  left_tread.run(RELEASE); // initialize motor off
  right_tread.run(RELEASE); // initialize motor off
}

void backward() {
  left_tread.run(BACKWARD);
  right_tread.run(BACKWARD);
  delay(MOVE_DELAY);
  left_tread.run(RELEASE); // initialize motor off
  right_tread.run(RELEASE); // initialize motor off
}

void right() {
  left_tread.run(FORWARD);
  right_tread.run(BACKWARD);
  delay(TURN_DELAY);
  left_tread.run(RELEASE); // initialize motor off
  right_tread.run(RELEASE); // initialize motor off
}

void left() {
  left_tread.run(BACKWARD);
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

void drop() {
  delay(DROP_DELAY);
}
