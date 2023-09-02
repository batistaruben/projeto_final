#include <Arduino.h>
#include <OneWire.h>
#include <DallasTemperature.h>
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"

// MQTT and WiFi
#include <WiFi.h>
#include <PubSubClient.h>

#define ONE_WIRE_BUS 25
// Setup a oneWire instance to communicate with any OneWire devices
OneWire oneWire(ONE_WIRE_BUS);
// Pass our oneWire reference to Dallas Temperature sensor 
DallasTemperature sensors(&oneWire);

const int pinPH   = 32;
const int pinEC   = 33;

float pH; 
float ec; 
float waterTemp;
float luz; 
float temp1; 
float temp2; 
float humid;

const char* ssid = "MEO-50525D";
const char* password = "C0D3B2D35F";
//const char* mqtt_server = "192.168.1.88"; //Rasp-PI
const char* mqtt_server = "192.168.1.72"; //PC
const int mqtt_port = 1883;

const char* mqtt_topic_airTemp   = "air_temperature";
const char* mqtt_topic_humidity  = "air_humidity";
const char* mqtt_topic_waterTemp = "water_temperature";
const char* mqtt_topic_ph        = "water_ph";
const char* mqtt_topic_ec        = "water_ec";

WiFiClient espClient;
PubSubClient client(espClient);

//Function to Setup The Wifi Network
void setupWiFi() {
  delay(10);
  Serial.println();
  Serial.print("Connecting to ");
  Serial.println(ssid);

  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }

  Serial.println("");
  Serial.println("WiFi connected");
  Serial.println("IP address: ");
  Serial.println(WiFi.localIP());
}

void setup() {
  Serial.begin(115200);
  Serial2.begin(115200, SERIAL_8N1, 17, 16); // UART2: TX = 17, RX = 16

  pinMode(pinPH, INPUT);
  pinMode(pinEC, INPUT);

  // Start up the library
  Serial.println();
  Serial.print("Locating Devices...");
  sensors.begin();
  Serial.print("Found ");
  Serial.print(sensors.getDeviceCount(),DEC);
  Serial.println(" devices.");

  // MQTT CONNECTION
  setupWiFi(); // Implement the WiFi connection setup function
  client.setServer(mqtt_server, 1883);
}

void loop() {
  Serial2.println("ReqData"); // Send data to the slave
  delay(5000);

  float phSum = 0;
  float ecSum = 0;
  float waterTempSum = 0;

  while (Serial2.available()) {
    String data = Serial2.readStringUntil('\n');
    Serial.println("Received from Slave: " + data);
    
    // Remove square brackets from the received data
    data.remove('[');
    data.remove(']');
    
    // Split the data into individual values based on commas
    int commaIndex = data.indexOf(',');
    if (commaIndex != -1) {
      String luzStr = data.substring(0, commaIndex);
      data = data.substring(commaIndex + 1);

      commaIndex = data.indexOf(',');
      if (commaIndex != -1) {
        String temp1Str = data.substring(0, commaIndex);
        data = data.substring(commaIndex + 1);

        commaIndex = data.indexOf(',');
        if (commaIndex != -1) {
          String temp2Str = data.substring(0, commaIndex);
          String humidStr = data.substring(commaIndex + 1);

          // Convert the parsed strings to float values
          luz = luzStr.toFloat();
          temp1 = temp1Str.toFloat();
          temp2 = temp2Str.toFloat();
          humid = humidStr.toFloat();
        }
      }
    }


    // Read Local Sensors - Make an Average
    for (int i = 0; i < 10; i++){
      // PH
      pH = (float)(analogRead(pinPH)* 14.0 / 4095.0);
      phSum += pH;
      // EC
      ec = (float)(1000.0 * analogRead(pinEC) / 2855.0);
      ecSum += ec;
      // TEMP
      sensors.requestTemperatures();
      waterTemp = sensors.getTempCByIndex(0);
      waterTempSum += waterTemp;
    }
    pH = (float)(analogRead(pinPH)* 14.0 / 4095.0);
    ec = ecSum / 10.0;
    waterTemp = waterTempSum / 10.0;

    String payload = "Light: " + String(luz, 2) +
                " | Air Temperature1: " + String(temp1, 2) +
                " | Air Temperature2: " + String(temp2, 2) +
                " | Humidity: " + String(humid, 2) +
                " | pH: " + String(pH, 2) +
                " | EC: " + String(ec, 2) +
                " | Water Temperature: " + String(waterTemp, 2); 
    Serial.println("Data:"+payload);

    if (client.connect("ESP32Client")) {
      Serial.println("Connected to MQTT broker");

      String lightValue = String(luz, 2);
      float avgAirTemp = (temp1+temp2)/2;
      String avgAirTempStr = String(avgAirTemp, 2);
      String humidityValue = String(humid, 2);
      String waterTempValue= String(waterTemp, 2);
      String phValue = String(pH, 2);
      String ecValue = String(ec, 2);

      client.publish(mqtt_topic_ec, ecValue.c_str());
      client.publish(mqtt_topic_ph, phValue.c_str());
      client.publish(mqtt_topic_waterTemp, waterTempValue.c_str());
      client.publish(mqtt_topic_humidity, humidityValue.c_str());
      client.publish(mqtt_topic_airTemp, avgAirTempStr.c_str());
  
      Serial.println("Data Sent");                 
    }
    else {
      Serial.println("MQTT connection failed");
    }
    client.loop();
  }

}