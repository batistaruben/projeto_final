#include <Arduino.h>
#include <DFRobot_DHT11.h>
#include <OneWire.h>
#include <DallasTemperature.h>

#define DHT_PIN 32 
#define LDR_PIN 33 
#define ONE_WIRE_BUS 25

// Setup a oneWire instance to communicate with any OneWire devices
OneWire oneWire(ONE_WIRE_BUS);

// Pass our oneWire reference to Dallas Temperature sensor 
DallasTemperature sensors(&oneWire);

float luz; 
float temp1; 
float temp2; 
float humid;
DFRobot_DHT11 DHT;

void setup() {
  Serial.begin(115200);
  Serial2.begin(115200, SERIAL_8N1, 17, 16); // UART2: TX = 17, RX = 16
}

void loop() {
  if (Serial2.available()) {
    String data = Serial2.readStringUntil('\n');
    Serial.println("Received from Master: " + data);
    String newData = "";
    for (char c : data) {
      if (isPrintable(c)) { 
        newData += c;
      }
    }
    if(newData == "ReqData"){
      float luzSum = 0; 
      float humidSum = 0; 
      float temp1Sum = 0; 
      float temp2Sum = 0;

      // Calculate Values Average to reduce Error
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
      float temperature1 = (DHT.temperature); 
      float temperature2 = (temp2Sum/10.0);
      float humidity = (DHT.humidity);
      String dataToSend = "["+String(luzAvg,2)+","+String(temperature1,2)+","+String(temperature2,2)+","+String(humidity,2)+"]";
      Serial.println(dataToSend);
      Serial2.println(dataToSend);
    }else{
      Serial.println("No Data Requested");
    }
  }
}