//arduino receiver 

#include <LoRa.h>

void setup() {
  Serial.begin(9600);           // Initialize serial communication
  while (!Serial);              // Wait for serial port to connect
  if (!LoRa.begin(433E6)) {     // Initialize LoRa at 433 MHz
    Serial.println("Starting LoRa failed!");
    while (1);
  }
  Serial.println("LoRa Receiver Initialized!");
}

void loop() {
  // Check for LoRa packets
  int packetSize = LoRa.parsePacket();
  if (packetSize) {
    String receivedStr = "";
    while (LoRa.available()) {
      receivedStr += (char)LoRa.read();
    }
    int encryptedData = receivedStr.toInt();
    
    // Decrypt the data
    int decryptedData = decryptData(encryptedData);
    
    // Print decrypted data
    Serial.print("Received Encrypted Data: ");
    Serial.print(encryptedData);
    Serial.print(" | Decrypted Data: ");
    Serial.println(decryptedData);
  }
}

int decryptData(int encryptedData) {
  // Example decryption logic (must match Python's encryption)
  // Assuming Python uses 'add' as one of the actions
  // Replace this with comprehensive decryption based on encryption actions
  // For simplicity, using inverse of 'add' action here
  return (encryptedData - 10) % 256;
}
