/* --- Libraries --- */
#include <Servo.h>

/* --- Prototypes --- */
void align_left(void);
void align_right(void);
void align_center(void);
void left(void);
void right(void);

/* --- Pin Constants --- */
const int LEFT_WHEEL_PIN = 2;
const int RIGHT_WHEEL_PIN = 3;

/* --- Time Constants ---*/
const int BOOT_DELAY = 10000;
const int BAUD_RATE = 9600;
const int TURN_DELAY = 200;

/* --- Commands --- */
const char ALIGN_RIGHT_COMMAND = 'R';
const char ALIGN_LEFT_COMMAND = 'L';
const char ALIGN_CENTER_COMMAND = 'C';

/* --- Servo Constants --- */
const int CLOCKWISE = 104;
const int COUNTERCLOCKWISE = 90;
const int OFF = 100;
const int LEFT = 90;
const int CENTER = 50;
const int RIGHT = 20;

/* --- Objects --- */
Servo left_wheel;
Servo right_wheel;
int command;
int orientation = 90;

/* --- Setup --- */
void setup() {
  delay(BOOT_DELAY);
  Serial.begin(BAUD_RATE);
  left_wheel.attach(LEFT_WHEEL_PIN);
  right_wheel.attach(RIGHT_WHEEL_PIN);
}

void loop() {
  if (Serial.available() > 0) {
    command = Serial.read();
    switch (command) {
      case ALIGN_LEFT_COMMAND:
        align_left();
        break;
      case ALIGN_RIGHT_COMMAND:
        align_right();
        break;
      case ALIGN_CENTER_COMMAND:
        align_center();
        break;
      default:
        break;
    }
    Serial.println("0");
    Serial.flush();
  }
}

/* --- Functions --- */
void align_center() {
  while (orientation > CENTER) {
    right();
  }
  while (orientation < CENTER) {
    left();
  }
}

void align_left() {
  while (orientation > LEFT) {
    right();
  }
  while (orientation < LEFT) {
    left();
  }
}

/* --- Functions --- */
void align_right() {
  while (orientation > RIGHT) {
    right();
  }
  while (orientation < RIGHT) {
    left();
  }
}


/* --- Movement --- */
void left() {
  left_wheel.write(CLOCKWISE);
  right_wheel.write(CLOCKWISE);
  delay(TURN_DELAY);
  left_wheel.write(OFF);
  right_wheel.write(OFF);
  orientation = orientation + 10;
}

void right() {
  left_wheel.write(COUNTERCLOCKWISE);
  right_wheel.write(COUNTERCLOCKWISE);
  delay(TURN_DELAY);
  left_wheel.write(OFF);
  right_wheel.write(OFF);
  orientation = orientation - 10;
}
