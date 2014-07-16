/* --- Libraries --- */
#include <Servo.h>

/* --- Prototypes --- */
void align_left(void);
void align_center(void);
void align_right(void);

/* --- Pin Constants --- */
const int LEFT_WHEEL_PIN = 2;
const int RIGHT_WHEEL_PIN = 3;

/* --- Time Constants ---*/
const int BOOT_DELAY = 10000;
const int BAUD_RATE = 9600;

/* --- Commands --- */
const char ALIGN_RIGHT_COMMAND = 'R';
const char ALIGN_CENTER_COMMAND = 'C';
const char ALIGN_LEFT_COMMAND = 'L';

/* --- Servo Constants --- */
const int LEFT = 160;
const int CENTER = 130;
const int RIGHT = 90;

/* --- Objects --- */
Servo left_wheel;
Servo right_wheel;
int command;

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

/* --- Alignments --- */
void align_left() {
  left_wheel.write(LEFT);
  right_wheel.write(LEFT);
}

void align_center() {
  left_wheel.write(CENTER);
  right_wheel.write(CENTER);
}

void align_right() {
  left_wheel.write(RIGHT);
  right_wheel.write(RIGHT);
}
