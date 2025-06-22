#include <ESP32Servo.h>

Servo myServo;
int servoPin = 13;

void setup() {
  Serial.begin(115200);
  myServo.attach(servoPin);
}

void loop() {
  if (Serial.available()) {
    String input = Serial.readStringUntil('\n');  // Read full line
    int angle = input.toInt();  // Convert to integer
    if (angle >= 0 && angle <= 180) { // Valid angle range
      myServo.write(angle);
      Serial.println("Moved to: " + String(angle)); // Debug message
    }
  }
}
