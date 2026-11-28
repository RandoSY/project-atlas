// Atlas Echo Lab v1.0: Arduino Uno, HC-SR04, no libraries.
// A4/A5 chosen to avoid common multifunction-shield display pins.
// Check your shield schematic: do not use these pins if occupied.
const byte TRIG=A4,ECHO=A5;
unsigned long n=0;
void setup(){Serial.begin(115200);pinMode(TRIG,OUTPUT);digitalWrite(TRIG,LOW);pinMode(ECHO,INPUT);}
void loop(){
  digitalWrite(TRIG,LOW);delayMicroseconds(3);
  digitalWrite(TRIG,HIGH);delayMicroseconds(10);digitalWrite(TRIG,LOW);
  unsigned long us=pulseIn(ECHO,HIGH,30000UL);
  Serial.print(n++);Serial.print(',');Serial.print(millis());Serial.print(',');Serial.println(us);
  delay(100);
}
