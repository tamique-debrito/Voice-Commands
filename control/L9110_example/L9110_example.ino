const int pinA = 12;
const int pinB = 13;

int turnState = 1;

unsigned long previousMillis = 0;

const long interval = 1000;

void setup() {
  pinMode(pinA, OUTPUT);
  pinMode(pinB, OUTPUT);
}

void loop() {
  unsigned long currentMillis = millis();

  if (currentMillis - previousMillis >= interval) {
    previousMillis = currentMillis;

    if (turnState == 1) {
      turnState = -1;
      digitalWrite(pinA, HIGH);
      digitalWrite(pinB, LOW);
    } else {
      turnState = 1;
      digitalWrite(pinA, LOW);
      digitalWrite(pinB, HIGH);
    }
  }
}
