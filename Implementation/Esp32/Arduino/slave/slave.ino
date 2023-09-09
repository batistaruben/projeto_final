#include <HardwareSerial.h>
#include <DFRobot_DHT11.h>
DFRobot_DHT11 DHT;

#define RX2_PIN 16
#define TX2_PIN 17
#define UART_BAUD_RATE 115200

const int analogPin = 34; // Replace this with your actual analog pin
const char* delimiter = "\n"; // End of line delimiter

#include <OneWire.h>
#include <DallasTemperature.h>

#define DHT_PIN 32 
#define LDR_PIN 33 
#define ONE_WIRE_BUS 25

#include <HardwareSerial.h>

float luz; float temp1; float temp2; float humid;
float luzSum; float humidSum; float temp1Sum; float temp2Sum;

// Setup a oneWire instance to communicate with any OneWire devices
OneWire oneWire(ONE_WIRE_BUS);

// Pass our oneWire reference to Dallas Temperature sensor 
DallasTemperature sensors(&oneWire);

void setup() {
  Serial.begin(UART_BAUD_RATE);
}

void loop() {

  luzSum   = 0;
  humidSum = 0;
  temp1Sum = 0;
  temp2Sum = 0;
  String resposta = Serial.readString();
  Serial.println(resposta);
  Serial.println("ESP Slave");
  
  if (Serial.available()) {
      String receivedData = Serial.readStringUntil('\n');
      if (receivedData == "RequestData") {
        for (int i = 0; i < 10; i++) {
          luz = analogRead(LDR_PIN);
          sensors.requestTemperatures();
          temp2 = sensors.getTempCByIndex(0);
          luzSum += luz;
          humidSum += humid;
          temp2Sum += temp2;
          delay(100); // Delay between readings
        }
        DHT.read(DHT_PIN);
        float luzAvg = (luzSum/10.0);
        float temp2Avg = (temp2Sum/10.0);
        String sendData = "["+String(luzAvg,2)+","+String(DHT.temperature,2)+","+String(temp2Avg,2)+","+String(DHT.humidity,2)+"]";
        Serial.print(sendData);
      }   
  }
  
  delay(1000);
}
