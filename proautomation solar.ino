#include <WiFi.h>
#include <PubSubClient.h>
#include <ArduinoJson.h>
WiFiClient client;
PubSubClient mqtt(client);
#define WIFI_STA_NAME "123"
#define WIFI_STA_PASS "1234512345"
#define MQTT_SERVER "34.143.207.104"
#define MQTT_PORT 8883
#define MQTT_USERNAME ""
#define MQTT_PASSWORD ""
#define MQTT_NAME "TeE"


DynamicJsonDocument docd(1024);
DynamicJsonDocument docs(1024);

void callback(char* topic, byte* payload, unsigned int length) {
  Serial.print("Topic =[");
  Serial.print(topic);
  Serial.print("] ");
  deserializeJson(docd, payload, length);
  serializeJson(docd, Serial);
  Serial.println();
  std::string tp = topic;
  if (tp == "inno/ProjectSolar/ganX") {
    int ganX = docd["ganX"];
    // const char* st = docd["ganX"];
    // std::string s = st;
    ledcWrite(1, ganX);
    }
    if (tp == "inno/ProjectSolar/ganY") {
    int ganY = docd["ganY"];
    // const char* st = docd["ganY"];
    // std::string s = st;
      ledcWrite(2, ganY);
    }
}
  void setup() {
    Serial.begin(115200);
    pinMode(LED_BUILTIN, OUTPUT);  //ESP32 = pin D2
    pinMode(12, OUTPUT);
    ledcSetup(1, 5000, 8);
    ledcAttachPin(12, 1);
    pinMode(13, OUTPUT);
    ledcSetup(2, 5000, 8);
    ledcAttachPin(13, 2);
    Serial.println();
    Serial.println();
    Serial.print("Connecting to ");
    Serial.println(WIFI_STA_NAME);
    WiFi.mode(WIFI_STA);
    WiFi.begin(WIFI_STA_NAME, WIFI_STA_PASS);
    while (WiFi.status() != WL_CONNECTED) {
      delay(500);
      Serial.print(".");
      digitalWrite(LED_BUILTIN, !digitalRead(LED_BUILTIN));
    }
    digitalWrite(LED_BUILTIN, HIGH);
    Serial.println("");
    Serial.println("WiFi connected");
    Serial.println("IP address: ");
    Serial.println(WiFi.localIP());
    mqtt.setServer(MQTT_SERVER, MQTT_PORT);
    mqtt.setCallback(callback);
  }
void loop() {
    float temp = 30;
    float shader = 50;
    float humid = 75;
    float randNumber;
    float randNumber2;
    float randNumber3;

    randNumber = random(-100, 101);
    randNumber2 = random(-100, 101);
    randNumber3 = random(-100, 101);
    float ram = randNumber / 100;
    float ram2 = randNumber2 / 100;
    float ram3 = randNumber3 / 500;
    docs["temp"] = temp + ram;
    docs["shader"] = shader + ram2;
    docs["humid"] = humid + ram3;
    char output[128];
    docs.shrinkToFit();
    serializeJson(docs, output);
    if (mqtt.connected() == false) {
      Serial.print("MQTT connecting... ");
      if (mqtt.connect(MQTT_NAME, MQTT_USERNAME, MQTT_PASSWORD)) {
        Serial.println("connected");
        mqtt.subscribe("inno/ProjectSolar/ganX");
        mqtt.subscribe("inno/ProjectSolar/ganY");
        // mqtt.subscribe("inno/b6310578/lab04/pwm");
      } else {
        Serial.println("failed");
        delay(1000);
      }
    } else {
      mqtt.loop();
      delay(10);
      mqtt.publish("inno/ProjectSolar/Sensor", output);

    }
    delay(1000);
  }