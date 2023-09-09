#include <HardwareSerial.h>
#include <OneWire.h>
#include <DallasTemperature.h>
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "driver/uart.h"

// Data wire is conntec to the Arduino digital pin 4
#define ONE_WIRE_BUS 25

// Setup a oneWire instance to communicate with any OneWire devices
OneWire oneWire(ONE_WIRE_BUS);

// Pass our oneWire reference to Dallas Temperature sensor 
DallasTemperature sensors(&oneWire);

const int pinPH   = 32;
const int pinEC   = 33;

float phSum;
float ecSum;
float waterTempSum;

float pH; 
float ec; 
float waterTemp;

#define UART_NUM UART_NUM_1
#define UART_BUF_SIZE (1024)
QueueHandle_t uart_event_queue;
#define RX_PIN 3
#define TX_PIN 1
#define UART_BAUD_RATE 115200

bool requestSlaveData = false; // Flag to request data from the slave
unsigned long lastRequestTime = 0;

// MQTT BROKER
#include <WiFi.h>
#include <PubSubClient.h>

const char* ssid = "WIFI NAME";
const char* password = "password";
const char* mqtt_server = "RASP PI IP";
const int mqtt_port = 1883;


const char* mqtt_topic_airTemp   = "air_temperature";
const char* mqtt_topic_humidity  = "air_humidity";
const char* mqtt_topic_waterTemp = "water_temperature";
const char* mqtt_topic_ph        = "water_ph";
const char* mqtt_topic_ec        = "water_ec";

WiFiClient espClient;
PubSubClient client(espClient);

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
  Serial.begin(UART_BAUD_RATE);
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

  phSum   = 0;
  waterTempSum = 0;
  ecSum   = 0;

  // Send a request to the slave
  Serial.println("RequestData");

  // Wait for a response from the slave
  while (!Serial.available()) {
    // Wait for data
  }

  String receivedData = Serial.readStringUntil(']'); // Read until ']'
  int startIdx = receivedData.indexOf('['); // Find the position of '['
  
  if (startIdx != -1) {
    // Extract the substring between '[' and ']'
    String valuesString = receivedData.substring(startIdx + 1);

    // Split the substring by commas to get individual values
    int numOfValues = 4; // Assuming there are 4 values (Luz, Temperatura1, Temperatura2, Humidade)

    float values[numOfValues];
    int commaIdx;
    for (int i = 0; i < numOfValues; i++) {
      commaIdx = valuesString.indexOf(',');
      if (commaIdx == -1) {
        commaIdx = valuesString.length(); // If there is no comma, use the length of the string
      }
      values[i] = valuesString.substring(0, commaIdx).toFloat();
      valuesString = valuesString.substring(commaIdx + 1); // Move to the next value
    }

    float luz = values[0];
    float temp1 = values[1];
    float temp2 = values[2];
    float humid = values[3];
    Serial.println(luz);
    Serial.println(temp1);
    Serial.println(temp2);
    Serial.println(humid);
    
    // Ler Sensores Locais - Fazer média de 10 leituras
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

    client.loop();
  }
  
}



