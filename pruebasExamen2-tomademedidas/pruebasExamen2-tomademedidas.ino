#include <Wire.h>
#include <AP3216_WE.h>
#include "Adafruit_HDC1000.h"
#include <TinyGPS.h>
#include <SoftwareSerial.h>
#include <ESP8266WiFi.h>
//#include <Hash.h>

WiFiClient client; 
TinyGPS gps;
SoftwareSerial ss(2, 0);
AP3216_WE lightSensor = AP3216_WE();
Adafruit_HDC1000 tempHumSensor = Adafruit_HDC1000();

String server ="34.205.147.56";
bool control = false;
char* ssid = "MARTINEZ_M";
char* password = "8M5^*t/a%1";
uint32_t previousMillis = 0;
const uint8_t numSamples=20, temperature=0, humidity=1,
              light=2, positionGPS=3;
uint8_t sensor;
float samples[numSamples], measures[4]; 
uint16_t id;
char date[32];
long latitude, longitude;
enum class machineState {SLEEP_TIME, READ_TEMPERATURE, READ_HUMIDITY, READ_LIGHT, 
                          READ_GPS,CHECK_CONNECTION, PRINT_PACKET};
machineState state = machineState::SLEEP_TIME;

void setup() {
  Serial.begin(115200);
  wifiConnect();
  Wire.begin();
  ss.begin(9600);
  lightSensor.init();
  lightSensor.setMode(AP3216_ALS_PS);
  lightSensor.setLuxRange(RANGE_20661);
  lightSensor.setPSGain(2);
  lightSensor.setNumberOfLEDPulses(1);
  lightSensor.setPSMeanTime(PS_MEAN_TIME_50);
  lightSensor.setPSThresholds(0, 100);
  lightSensor.setPSIntegrationTime(1);
  lightSensor.setPSInterruptMode(INT_MODE_HYSTERESIS);
  
  if(!tempHumSensor.begin()) {
    Serial.println("No es posible establecer la comunicación con el sensor de temperatura.");
  }
  else {
    Serial.println("Conectado al sensor de temperatura.");
  }
  delay(1000);
} 


void loop() {
  switch(state)
  {
    case machineState::SLEEP_TIME:
       state = machineState::READ_TEMPERATURE;
      smartdelay(1000);
    break;
    
    case machineState::READ_TEMPERATURE:
      getMeasures(temperature);
      state = machineState::READ_HUMIDITY;
      break;
    
    case machineState::READ_HUMIDITY:
      getMeasures(humidity);
      state = machineState::READ_LIGHT;
      break;
    
    case machineState::READ_LIGHT:
      getMeasures(light);
      state = machineState::READ_GPS;
      break;
    
    case machineState::READ_GPS:
      smartdelay(1000);
      readDate(gps);
      gps.get_position(&longitude, &latitude);
      state = machineState::CHECK_CONNECTION;
      break;

    case machineState::CHECK_CONNECTION:
      checkConnection();
    break;
    
    case machineState::PRINT_PACKET:
      if (waitTime(13000)){
        packet();
        messageToServer();  
      }
      state = machineState::SLEEP_TIME;
      break;

  }
}

void chirp (uint8_t sensor) {
  for (uint8_t sample=0; sample < numSamples; sample++) {
    switch(sensor) {
      case temperature:
        samples[sample] = tempHumSensor.readTemperature();
        delay(15);
        break;
      
      case humidity:
        samples[sample] = tempHumSensor.readHumidity();
        delay(15);
        break;
      
      case light:
        samples[sample] = lightSensor.getAmbientLight();;
        delay(15);
        break;
    }
  }
}

float prunning() {
  float sum;
  for (uint8_t sample = 0; sample < numSamples; sample++) {
     sum +=samples[sample];
  }
  return sum/numSamples;
}

void getMeasures(uint8_t sensor) {
  chirp(sensor);
  measures[sensor] = prunning();
}

void packet() {
  Serial.print("packet ID:\t");Serial.println(id);
  Serial.print("Date: \t\t");Serial.println(date);
  Serial.print("Temperature:\t");Serial.print(measures[temperature]);Serial.println(" °C");
  Serial.print("Humidity:   \t");Serial.print(measures[humidity]);Serial.println(" %");
  Serial.print("Light:\t\t");Serial.println(measures[light]);
  Serial.print("Position:   \t\n");
  Serial.print("   Latitude:\t");Serial.println(latitude);
  Serial.print("   Longitude:\t");Serial.println(longitude); 
  
  id++;
}
void readDate(TinyGPS &gps) {
  int year;
  byte month, day, hour, minute, second, hundredths;
  unsigned long age;
  gps.crack_datetime(&year, &month, &day, &hour, &minute, &second, &hundredths, &age);
  if (age == TinyGPS::GPS_INVALID_AGE) {
    
  }
  else {  
    sprintf(date, "%02d/%02d/%02d %02d:%02d:%02d ",
        month, day, year, hour, minute, second);
  }
  smartdelay(0);
}
void smartdelay(unsigned long ms)
{
  unsigned long start = millis();
  do 
  {
    while (ss.available())
      gps.encode(ss.read());
  } while (millis() - start < ms);
}

void parseToDegrees(long decimal) {
  bool isNeg = decimal<0 ? true : false;
  int hours, minutes;
  float sec, resHours, resMinutes;
  if (isNeg) decimal * -1;
  //decimal/=100000;
  resHours = decimal - (int)(decimal)<0 ? 1+(decimal - (int)decimal) : decimal - (int)decimal;
  hours = (int)(decimal - resHours);
  resMinutes = (resHours * 60)<1 ? 0 : (resHours * 60);
  resMinutes = minutes - (int)(minutes)<0 ? 1+(minutes - (int)minutes) : minutes - (int)minutes;
  minutes = (int)(minutes - resMinutes);
  sec = resMinutes*60;
  Serial.print(hours);Serial.print(minutes);Serial.println(sec);
}

void wifiConnect()
{
  IPAddress staticIP(192,168,1,50);
  IPAddress gateway(192,168,1,254);
  IPAddress subnet(255,255,255,0);
  Serial.println();
  Serial.printf("Connecting to %s\n", ssid);
  WiFi.config(staticIP, gateway, subnet);
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED)
  {
    delay(500);
    Serial.print(WiFi.status());
  }
  Serial.println();
  Serial.print("Connected, IP address: ");
  Serial.println(WiFi.localIP());
}
void messageToServer() {
  String PostData = String("sensorID: 000373460;packetID: "+String(id)+";Temperature: "+String(measures[0])+";Humidity: "+String(measures[1])+
                    ";Light: "+String(measures[2])+";Longitude: "+String(latitude)+
                    ";Latitude: "+String(longitude)) ;
    client.connect(server,80);
    client.println("POST /data HTTP/1.1");
    // poner la direccion IP del servidor
    client.print("Host: "+ server +"\n");
    client.println("User-Agent: Arduino/1.0");
    client.println("Connection: close");
    client.println("Content-Type: text/plain");
    client.print("Content-Length: ");
    client.println(PostData.length());
    client.println();
    client.println(PostData);
}
bool waitTime (uint32_t timeToAwait) {
  uint32_t currentMillis = millis();
  if (currentMillis - previousMillis > timeToAwait) {
    previousMillis = currentMillis;
    control = true;
  }
  else {
    control = false;
  }
  return control;
}
void checkConnection() {
  if(WiFi.status() == WL_CONNECTED) {
    if(!client.connected()) {
      while(!client.connect(server,80)) {
        Serial.print(".");
        delay(500);
      }
    } 
    state = machineState::PRINT_PACKET;
  }
  else {
    wifiConnect();
  }
}
  
