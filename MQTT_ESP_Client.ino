#include <WiFi.h>
#include <PubSubClient.h>

// WiFi
const char *ssid = "MEO-50525D"; // Enter your WiFi name
const char *password = "C0D3B2D35F";  // Enter WiFi password

// MQTT Broker
const char *mqtt_broker = "192.168.1.72"; //IP do pc
const char *topic = "test/topic";
const int mqtt_port = 1883;

WiFiClient espClient;
PubSubClient client(espClient);

bool shouldRespond = false;

void setup() {
  //LED built-in do esp
  pinMode (LED_BUILTIN, OUTPUT);

  Serial.begin(115200);

  // connecting to a WiFi network
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.println("Connecting to WiFi..");
  }

  Serial.println("Connected to the WiFi network");

  //connecting to a mqtt broker
  client.setServer(mqtt_broker, mqtt_port);
  client.setCallback(callback);

  while (!client.connected()) {
    String client_id = "esp8266-client-";
    client_id += String(WiFi.macAddress());

    Serial.printf("The client %s connects to mosquitto mqtt broker\n", client_id.c_str());

    if (client.connect(client_id.c_str())) {
      Serial.println("Public emqx mqtt broker connected");
    } else {
      Serial.print("failed with state ");
      Serial.print(client.state());
      delay(2000);
    }
  }

  // publish and subscribe
  client.publish(topic, "Sensor Connected");
  client.subscribe(topic);
}


void callback(char *topic, byte *payload, unsigned int length) {
  Serial.println();
  Serial.print("Message arrived in topic: ");
  Serial.println(topic);
  Serial.print("Message:");

  String msg = "";
  for (int i = 0; i < length; i++) {
    msg += (char)payload[i];
    //Serial.print((char) payload[i]);
  }

  digitalWrite (LED_BUILTIN, HIGH);	// turn on the LED
  delay(1500);	// wait for half a second or 500 milliseconds
  digitalWrite (LED_BUILTIN, LOW);	// turn off the LED

  Serial.println(msg);
  Serial.println(" - - - - - - - - - - - -");

  if(msg.equals("hi")){
    shouldRespond = true;
  }
}


void loop() {
  client.loop();

  if (shouldRespond) {
    client.publish(topic, "How are you?");
    shouldRespond = false;
  }

}

/*
Para obter a resposta do "How are you?" numa consola, já com o broker ligado, executar o comando: mosquitto_pub -h localhost -p 1883 -t test/topic -m "hi"
*/
