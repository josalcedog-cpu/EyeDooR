#include <WiFi.h>
#include <time.h> 


#define WIFI_SSID "A16 de Daniel"
#define WIFI_PASSWORD "12345678"


#include "FirebaseESP32.h"
#include <addons/TokenHelper.h>
#include <addons/RTDBHelper.h>

#define API_KEY "AIzaSyDQ9Vq0xYg_e82XKOKajuLtlt8YRanxVdw"
#define DATABASE_URL "https://eyedoor-49c27-default-rtdb.firebaseio.com/"
#define USER_EMAIL "esp32@test.com"
#define USER_PASSWORD "123456789"

FirebaseData firebaseData;
FirebaseAuth auth;
FirebaseConfig config;


const int PUSH_BUTTON_PIN = 4; 
unsigned long lastPressTime = 0; 
const unsigned long debounceDelay = 2000; 


const char* ntpServer = "pool.ntp.org";
const long gmtOffset_sec = -18000; 
const int daylightOffset_sec = 0;

String getFormattedDateTime() {
  struct tm timeinfo;
  if (!getLocalTime(&timeinfo)) {
    Serial.println("Fallo al obtener la hora");
    return "Error: Sin hora";
  }
  

  char timeString[50];
  strftime(timeString, sizeof(timeString), "%Y-%m-%d %H:%M:%S", &timeinfo);
  
  return String(timeString);
}


void setup() {
  Serial.begin(115200);

  pinMode(PUSH_BUTTON_PIN, INPUT_PULLUP);

  WiFi.begin(WIFI_SSID, WIFI_PASSWORD);
  while (WiFi.status() != WL_CONNECTED) {
    Serial.print(".");
    delay(300);
  }
  Serial.println("\nWiFi conectado.");

  Serial.println("Configurando hora desde NTP...");
  configTime(gmtOffset_sec, daylightOffset_sec, ntpServer);

  config.api_key = API_KEY;
  auth.user.email = USER_EMAIL;
  auth.user.password = USER_PASSWORD;
  config.database_url = DATABASE_URL;

  config.token_status_callback = tokenStatusCallback;

  firebaseData.setBSSLBufferSize(4096, 1024);

  Firebase.begin(&config, &auth);
  Firebase.setDoubleDigits(5);


  Serial.println("Conectando a Firebase...");
  while (!Firebase.ready()) {
    delay(200);
  }
  Serial.println("Conectado a Firebase:)");
}

void loop() {

  int buttonState = digitalRead(PUSH_BUTTON_PIN);

  if (buttonState == LOW) {
    

    if (millis() - lastPressTime > debounceDelay) {
      
      lastPressTime = millis(); 
      
      Serial.println("¡TIMBRE PRESIONADO! Enviando a Firebase...");

      String timestamp = getFormattedDateTime();
      Serial.println("Timestamp: " + timestamp);

      FirebaseJson json;
      json.set("evento", "Timbre presionado");
      json.set("timestamp", timestamp);

      String path = "/timbres";
      
      if (Firebase.setJSON(firebaseData, path, json)) {
        Serial.println("¡Datos enviados a Firebase exitosamente!");

      } else {
        Serial.println("Error al enviar datos a Firebase.");
        Serial.println("RAZÓN: " + firebaseData.errorReason());
      }
    }
  }
}