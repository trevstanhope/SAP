#include <Servo.h>

/* --- --- */
int BAUD = 9600;
int SERVO_PIN = 9;
int SERVO_SPEED = 200;
int INTERVAL_ON = 30;
int INTERVAL_OFF = 40;
int SERVO_OFF = 100;

/* --- --- */
Servo rotator;

/* --- --- */
void setup() {
  Serial.begin(BAUD);
  rotator.attach(SERVO_PIN);
  rotator.write(SERVO_SPEED);
}

/* --- --- */
void loop() {
  unsigned int time = millis();
  Serial.println(time);
  rotator.write(SERVO_SPEED);
  delay(INTERVAL_ON);
  rotator.write(SERVO_OFF);
  delay(INTERVAL_OFF);
}
