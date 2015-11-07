
// Arduino sketch for humidity/temp sensor and LLAP over radio
// Adapted from Ciseco example

#include "LLAPSerial.h"
#include "DHT.h"

#define CONST 10 // Necessary to scale readings for some reason

#define DHTPIN 2
#define DHTTYPE DHT22

#define BAUD_RATE 115200

#define DEVICE_ID "SR"
#define MSG_STARTED "STARTED"
#define MSG_ERROR_TEMPERATURE "ERR_TMP"
#define MSG_ERROR_HUMIDITY "ERR_HUM"
#define MSG_HUMIDITY "HUM"
#define MSG_TEMPERATURE "TMP"

#define SAMPLE_FREQ 30000 // 30 seconds

DHT dht(DHTPIN, DHTTYPE);

void setup() 
{
  Serial.begin(BAUD_RATE);
  pinMode(8, OUTPUT);
  digitalWrite(8, HIGH);
  pinMode(4, OUTPUT);
  digitalWrite(4, LOW);
  delay(1000); // Radio startup time

  LLAP.init(DEVICE_ID);
  dht.begin();
  LLAP.sendMessage(F(MSG_STARTED));
}

void loop()
{
  if (LLAP.bMsgReceived)
  {
    Serial.print(F("msg:"));
    Serial.println(LLAP.sMessage);
    LLAP.bMsgReceived = false;
  }


  static unsigned long lastTime = millis();
  if (millis() - lastTime >= SAMPLE_FREQ)
  {
    int hum = dht.readHumidity() * CONST,
        temp = dht.readTemperature() * CONST;

    if (isnan(temp))
      LLAP.sendMessage(F(MSG_ERROR_TEMPERATURE));
    else
      LLAP.sendIntWithDP(MSG_TEMPERATURE, temp, 1);
    if (isnan(hum))
      LLAP.sendMessage(F(MSG_ERROR_HUMIDITY));
    else
      LLAP.sendIntWithDP(MSG_HUMIDITY, hum, 1);
      
    lastTime = millis();
  }
}
