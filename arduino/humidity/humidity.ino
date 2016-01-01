//////////////////////////////////////////////////////////////////////////
// Arduino sketch for humidity/temp sensor and LLAP over radio
//    Adapted from Ciseco example located here: https://github.com/CisecoPlc/LLAPSerial/blob/master/examples/LLAP_DHT22/LLAP_DHT22.ino
//    DHT22 readings may be up to 2s old
//
// Libraries required in your library 
//    Ciseco LLAPSerial: https://github.com/CisecoPlc/LLAPSerial
//    Adafruit DHT: https://github.com/adafruit/DHT-sensor-library
//////////////////////////////////////////////////////////////////////////

#include <LLAPSerial.h>
#include <DHT.h>

#define DEVICE_ID   "SR"          // LLAP device ID
#define BAUD_RATE   115200
#define FREQ        90            // Sample every 15 mins (in 10000ms fragments: LLAP.sleepForaWhile() max word length)

#define SAMPLES_PER_READING 3     // No. readings to average over
#define READING_FREQ        10    // Wait 10 secs between readings

#define DHT_PIN             2     // Pin config
#define DHT_TYPE            DHT22 // Sensor config, DHT 22 (AM2302)
#define SRF_RF_ENABLE_PIN   8
#define SRF_SLEEP_PIN       4 


DHT dht(DHT_PIN, DHT_TYPE); //Humidity: 2-5% accuracy; Temperature: +/- 0.5*c

void setup() 
{

  Serial.begin(BAUD_RATE);
  
  digitalWrite(DHT_PIN, LOW); // No voltage to pin
  
  pinMode(SRF_RF_ENABLE_PIN, OUTPUT);
  digitalWrite(SRF_RF_ENABLE_PIN, HIGH); // Select radio

  // SRF sleep mode 2
  pinMode(SRF_SLEEP_PIN, OUTPUT);
  digitalWrite(SRF_SLEEP_PIN, LOW);
  delay(1000);
  Serial.print("+++");              // enter AT command mode
  delay(1500);                      // delay 1.5s
  Serial.println("ATSM2");          // enable sleep mode 2 <0.5uA
  delay(2000);
  Serial.println("ATDN");           // exit AT command mode
  delay(2000);
  
  LLAP.init(DEVICE_ID);
  dht.begin();
  LLAP.sendMessage(F("STARTED"));
}

void* readDHT(int *readings)
{  
  digitalWrite(DHT_PIN, HIGH); // Voltage to pin
  int h = dht.readHumidity() * 10;
  int t = dht.readTemperature() * 10;
  digitalWrite(DHT_PIN, LOW); // No voltage to pin

  if (isnan(t) || isnan(h)) 
  {
    return NULL;
  } 
  else 
  {
    readings[0] = h;
    readings[1] = t;
    
    Serial.flush();
  }
}

void loop() 
{
/*  // print the string when a newline arrives:
  if (LLAP.bMsgReceived) {
    Serial.print(F("msg:"));
    Serial.println(LLAP.sMessage); 
    LLAP.bMsgReceived = false;  // if we do not clear the message flag then message processing will be blocked
  }
*/

  int sumReadings[2] = {0, 0};
  word n = SAMPLES_PER_READING;
  for (word i = 0; i < SAMPLES_PER_READING; ++i)
  {
    int readings[2] = {0, 0};
    if (!readDHT(readings))
      n -= 1;
    else
    {
      sumReadings[0] += readings[0];
      sumReadings[1] += readings[1];
    }
    
    delay(READING_FREQ * 1000); // Better way of sleeping?
    
  }

  if (n == 0)
    LLAP.sendMessage(F("ERROR"));
  else 
  {
    float avReadings[2];
    avReadings[0] = sumReadings[0] / n;
    avReadings[1] = sumReadings[1] / n;

    LLAP.sendIntWithDP("HUM", avReadings[0], 1);
    LLAP.sendIntWithDP("TMP", avReadings[1], 1);
    delay(10);                         // allow radio to finish sending
  }
  
  digitalWrite(SRF_SLEEP_PIN, HIGH); // pull sleep pin high to enter SRF sleep 2

  word sc = 0;
  while (sc < FREQ)
  {
    //delay(10);
    LLAP.sleepForaWhile(10000); // Max word length => 10 seconds
    sc++;
  }
  
  digitalWrite(SRF_SLEEP_PIN, LOW);
  delay(10);
}

