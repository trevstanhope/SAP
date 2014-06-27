#include <AFMotor.h>
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
void boom_right(void);
void boom_left(void);
void boom_center(void);

/* --- Constants --- */
const int BOOT_DELAY = 10000;
const int LEFT_TREAD_MOTOR = 1;
const int RIGHT_TREAD_MOTOR = 2;
const int BAUD_RATE = 9600;
const int MOTOR_SPEED = 100;
const char FORWARD_COARSE = 'F';
const char FORWARD_FINE = 'f';
const char BACKWARD_COARSE = 'B';
const char BACKWARD_FINE = 'b';
const char LEFT_COARSE = 'L';
const char LEFT_FINE = 'l';
const char RIGHT_COARSE = 'R';
const char RIGHT_FINE = 'r';
const char BOOM_RIGHT = 'S';
const char BOOM_LEFT = 'P';
const char BOOM_CENTER = 'C';
const int COARSE_TURN_DELAY = 2000;
const int FINE_TURN_DELAY = 1000;
const int COARSE_MOVE_DELAY = 1000;
const int FINE_MOVE_DELAY = 500;
const int BOOM_PIN = 10;
const int DEGREES_RIGHT = 141;
const int DEGREES_LEFT = 25;
const int DEGREES_CENTER = 83;
const int BOOM_DELAY = 100;

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
void forward_coarse() {
  left_tread.run(FORWARD);
  right_tread.run(FORWARD);
  delay(COARSE_MOVE_DELAY);
  left_tread.run(RELEASE); // initialize motor off
  right_tread.run(RELEASE); // initialize motor off
}

void forward_fine() {
  left_tread.run(FORWARD);
  right_tread.run(FORWARD);
  delay(FINE_MOVE_DELAY);
  left_tread.run(RELEASE); // initialize motor off
  right_tread.run(RELEASE); // initialize motor off
}

void backward_coarse() {
  left_tread.run(BACKWARD);
  right_tread.run(BACKWARD);
  delay(COARSE_MOVE_DELAY);
  left_tread.run(RELEASE); // initialize motor off
  right_tread.run(RELEASE); // initialize motor off
}

void backward_fine() {
  left_tread.run(BACKWARD);
  right_tread.run(BACKWARD);
  delay(FINE_MOVE_DELAY);
  left_tread.run(RELEASE); // initialize motor off
  right_tread.run(RELEASE); // initialize motor off
}

void right_coarse() {
  left_tread.run(FORWARD);
  delay(COARSE_TURN_DELAY);
  left_tread.run(RELEASE); // initialize motor off
  right_tread.run(BACKWARD);
  delay(COARSE_TURN_DELAY);
  right_tread.run(RELEASE); // initialize motor off
}

void right_fine() {
  left_tread.run(FORWARD);
  delay(FINE_TURN_DELAY);
  left_tread.run(RELEASE); // initialize motor off
  right_tread.run(BACKWARD);
  delay(FINE_TURN_DELAY);
  right_tread.run(RELEASE); // initialize motor off
}

void left_coarse() {
  left_tread.run(BACKWARD);
  delay(COARSE_TURN_DELAY);
  left_tread.run(RELEASE); // initialize motor off
  right_tread.run(FORWARD);
  delay(COARSE_TURN_DELAY);
  right_tread.run(RELEASE); // initialize motor off
}

void left_fine() {
  left_tread.run(BACKWARD);
  delay(FINE_TURN_DELAY);
  left_tread.run(RELEASE); // initialize motor off
  right_tread.run(FORWARD);
  delay(FINE_TURN_DELAY);
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

