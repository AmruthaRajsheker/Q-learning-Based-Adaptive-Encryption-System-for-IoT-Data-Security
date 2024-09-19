// arduino sender

#include <LoRa.h>

const int sensorPin = A0;  // Analog pin connected to the sensor
int sensorValue = 0;       // Variable to store sensor value

void setup() {
  Serial.begin(9600);           // Initialize serial communication
  while (!Serial);              // Wait for serial port to connect
  if (!LoRa.begin(433E6)) {     // Initialize LoRa at 433 MHz
    Serial.println("Starting LoRa failed!");
    while (1);
  }
  Serial.println("LoRa Initializing OK!");
}

void loop() {
  // Read sensor data
  sensorValue = analogRead(sensorPin);
  
  // Send data over Serial to Python for encryption
  Serial.println(sensorValue);
  
  // Wait for encrypted data from Python
  if (Serial.available() > 0) {
    String encryptedStr = Serial.readStringUntil('\n');
    int encryptedData = encryptedStr.toInt();
    
    // Transmit encrypted data over LoRa
    LoRa.beginPacket();
    LoRa.print(encryptedData);
    LoRa.endPacket();
    
    Serial.print("Sent Encrypted Data: ");
    Serial.println(encryptedData);
  }
  
  delay(1000); // Delay to prevent overwhelming the serial port
}
