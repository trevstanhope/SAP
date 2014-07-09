#include <AFMotor.h>
#include <Servo.h>
#include <Wire.h>
#include <HMC6352.h>

/* --- Prototypes --- */
void forward(int);
void backward(int);
void right(int);
void left(int);
void boom_right(void);
void boom_left(void);
void boom_center(void);
void fork_down(void);
void fork_up(void);

/* --- Constants --- */
const int BOOT_DELAY = 10000;
const int LEFT_TREAD_MOTOR = 1;
const int RIGHT_TREAD_MOTOR = 2;
const int BAUD_RATE = 9600;
const int MOTOR_SPEED = 255;
const char FORWARD_COMMAND = 'F';
const char BACKWARD_COMMAND = 'B';
const char LEFT_COMMAND = 'L';
const char RIGHT_COMMAND = 'R';
const char BOOM_RIGHT_COMMAND = 'S';
const char BOOM_LEFT_COMMAND = 'P';
const char BOOM_CENTER_COMMAND = 'C';
const char FORK_UP_COMMAND = 'U';
const char FORK_DOWN_COMMAND = 'D';
const int TURN_DELAY = 100;
const int MOVE_DELAY = 150;
const int FORK_PIN = 9;
const int BOOM_PIN = 10;
const int BOOM_RIGHT = 50;
const int BOOM_LEFT = 116;
const int BOOM_CENTER = 83;
const int BOOM_DELAY = 500;
const int FORK_UP = 0;
const int FORK_DOWN = 180;
const int FORK_DELAY = 500;
const int INIT_DELAY = 100;
const int BUFFER = 128;
const int SERIAL_DELAY = 10;
const int RELEASE_DELAY = 5;
const int LEFT_CORRECTION = 10;
const int RIGHT_CORRECTION = 10;

/* --- Objects --- */
AF_DCMotor left_tread(LEFT_TREAD_MOTOR);
AF_DCMotor right_tread(RIGHT_TREAD_MOTOR);
Servo boom;
Servo fork;
char output[BUFFER];
int command;
int counter;
int heading;

/* --- Setup --- */
void setup() {
  delay(BOOT_DELAY);
  Wire.begin();
  delay(INIT_DELAY);
  Serial.begin(BAUD_RATE);
  delay(INIT_DELAY);
  left_tread.setSpeed(MOTOR_SPEED);
  right_tread.setSpeed(MOTOR_SPEED);
  left_tread.run(RELEASE); // initialize motor off
  right_tread.run(RELEASE); // initialize motor off
  boom.attach(BOOM_PIN);
  boom_center(); // center boom
  fork.attach(FORK_PIN);
  fork_up();
}

void loop() {
  
  // Check for incoming byte from USB
  if (Serial.available() > 0) {
    command = Serial.read();
    delay(SERIAL_DELAY);
    // Reset counter
    counter = 1;
    while (Serial.available() > 0) {
      Serial.read();
      counter++;
      delay(SERIAL_DELAY);
    }
    // Execute command
    switch (command) {
      case FORWARD_COMMAND:
        forward(counter);
        break;
      case RIGHT_COMMAND:
        right(counter);
        break;    
      case LEFT_COMMAND:
        left(counter);
        break;
      case BACKWARD_COMMAND:
        backward(counter);
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
      case FORK_UP_COMMAND:
        fork_up();
        break;  
      case FORK_DOWN_COMMAND:
        fork_down();
        break;  
      default:
        break;
    }
    // Get new heading
    HMC6352.Wake();
    heading = HMC6352.GetHeading();
    HMC6352.Sleep();
    sprintf(output, "{heading:%d, counter:%d, command:%d}", heading, counter, command);
    Serial.println(output);
    Serial.flush();
  }
}

/* --- Tread Functions --- */
void forward(int steps) {
  left_tread.run(FORWARD);
  right_tread.run(FORWARD);
  delay(steps * MOVE_DELAY);
  left_tread.run(RELEASE); // initialize motor off
  right_tread.run(RELEASE);
}

void backward(int steps) {
  left_tread.run(BACKWARD);
  right_tread.run(BACKWARD);
  delay(steps * MOVE_DELAY);
  left_tread.run(RELEASE);
  right_tread.run(RELEASE); // initialize motor off
}

void right(int degs) {
  HMC6352.Wake();
  int heading_a = HMC6352.GetHeading();
  HMC6352.Sleep();
  int heading_b = heading_a;
  while (abs(heading_a - heading_b) < (degs - RIGHT_CORRECTION)) {
    right_tread.run(BACKWARD);
    left_tread.run(FORWARD);    
    delay(TURN_DELAY);
    right_tread.run(RELEASE);
    left_tread.run(RELEASE);
    delay(RELEASE_DELAY);
    HMC6352.Wake();
    heading_b = HMC6352.GetHeading();
    HMC6352.Sleep();
    if (heading_a > heading_b + 180) {
      heading_b = heading_b + 360; // add 360 if heading B is less than heading A (North rollover clockwise)
    }
  }
}

void left(int degs) {
  HMC6352.Wake();
  int heading_a = HMC6352.GetHeading();
  HMC6352.Sleep();
  int heading_b = heading_a;
  while (abs(heading_a - heading_b) < (degs - LEFT_CORRECTION)) {
    right_tread.run(FORWARD);
    left_tread.run(BACKWARD);
    delay(TURN_DELAY);
    right_tread.run(RELEASE);
    left_tread.run(RELEASE);
    delay(RELEASE_DELAY);
    HMC6352.Wake();
    heading_b = HMC6352.GetHeading();
    HMC6352.Sleep();
    if (heading_b > heading_a + 180) {
      heading_b = heading_b - 360; // add 360 if heading A is less than heading B (North rollover counter-clockwise)
    }
  }
}

/* --- Boom --- */
void boom_right() {
  boom.write(BOOM_RIGHT);
  delay(BOOM_DELAY);
}

void boom_left() {
  boom.write(BOOM_LEFT);
  delay(BOOM_DELAY);  
}

void boom_center() {
  boom.write(BOOM_CENTER);
  delay(BOOM_DELAY);  
}

void fork_up() {
  fork.write(FORK_UP);
  delay(FORK_DELAY);
}

void fork_down() {
  fork.write(FORK_DOWN);
  delay(FORK_DELAY);
}
