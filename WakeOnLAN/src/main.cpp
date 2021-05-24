#include <arduino.h>
#include <WiFi.h>
#include <WiFiUdp.h>

#include "time.h"

#define uS_TO_S_FACTOR 1000000

// WiFi network name and password
const char * ssid = "NazwaSieci";
const char * pwd = "Haslo";

const char * ntpServer = "pool.ntp.org";
const long gmtOffset_sec = 3600;
const int daylightOffset_sec = 3600;

const char * udpAddress = "192.168.1.255";
const int udpPort = 9;
const uint8_t targetHour = 7;
const uint8_t targetMinute = 12;

const uint8_t macAddr[] = {0x01, 0x23, 0x45, 0x67, 0x89, 0xab};
uint8_t packet[102] = {0xff, 0xff, 0xff, 0xff, 0xff, 0xff};
uint8_t times[] = {60, 30, 10};
uint8_t currTime = 0;

//create UDP instance
WiFiUDP udp;
struct tm timeinfo;
void setup(){
  Serial.begin(115200);
	for (uint8_t i=6; i<102; i++){
		packet[i] = macAddr[i%6];
	}
  while (true){
    Serial.print("I'll wake up on: ");
    Serial.print(targetHour);
    Serial.print(":");
    Serial.print(targetMinute);
    Serial.println("...");
    
    // Connect to the WiFi network
    WiFi.begin(ssid, pwd);
    Serial.print("Connecting...");

    // Wait for connection
    while (WiFi.status() != WL_CONNECTED) {
      delay(500);
      Serial.print(".");
    }
    Serial.println("");
    Serial.print("Connected to ");
    Serial.println(ssid);
    Serial.print("IP address: ");
    Serial.println(WiFi.localIP());

    configTime(gmtOffset_sec, daylightOffset_sec, ntpServer);
  
    getLocalTime(&timeinfo);
    int32_t rawTime = (targetHour-timeinfo.tm_hour) * 3600 + (targetMinute - timeinfo.tm_min - 1) * 60 + 50 - timeinfo.tm_sec;
    if (rawTime > 0){
      while (currTime < sizeof(times)){
        if (rawTime < times[currTime]*60 + 60) currTime++; else break;
      }
      if (currTime < sizeof(times)) rawTime = times[currTime]*60;
    }else if (rawTime < 0) rawTime = times[0]*60;

    Serial.print(&timeinfo, "%H:%M:%S\t");
    Serial.print("Going to sleep... I'll wake up in ");
    Serial.print(rawTime/60.0);
    Serial.println(" minutes.");

    Serial.flush();
    esp_sleep_enable_timer_wakeup((uint64_t)rawTime * uS_TO_S_FACTOR);
    esp_light_sleep_start();
    Serial.println("Waking up...");
    if (currTime >= sizeof(times)) break;
  }
  Serial.println("Starting to send WoL packets...");

  WiFi.begin(ssid, pwd);
  Serial.print("Connecting...");

  // Wait for connection
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("");
  Serial.print("Connected to ");
  Serial.println(ssid);
  Serial.print("IP address: ");
  Serial.println(WiFi.localIP());

  delay(5000);
  // Initialize UDP and transfer buffer
  // Send WoL to server
  for (int i=0; i<5; i++){
    delay(500);
    do{
      udp.beginPacket(udpAddress, udpPort);
      udp.write(packet, sizeof(packet));
    }while (!udp.endPacket());

    Serial.println("Sent!");
    delay(1000);
  }
  udp.stop();

  delay(5000);
  esp_sleep_disable_wakeup_source(ESP_SLEEP_WAKEUP_ALL);
  esp_deep_sleep_start();
}

void loop(){

}