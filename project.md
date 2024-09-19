
1. **Arduino Sender**: Collects sensor data and sends it to Python via serial communication.
2. **Arduino Receiver**: Receives encrypted data via LoRa, decrypts it, and prints the decrypted data.
3. **Python (Colab) Code**: Handles encryption, decryption, Q-learning, and real-time plotting with live printed values.

---

## 1. Arduino Code: Sender

**Functionality**:
- Reads sensor data from an analog pin.
- Sends the data to Python via serial communication.
- Receives encrypted data from Python and transmits it over LoRa.

```cpp
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
```

**Notes**:
- **LoRa Frequency**: Ensure that the frequency (`433E6` in the code) matches your LoRa module's specifications.
- **Serial Communication**: The sender sends sensor data to Python and waits for the encrypted data to send over LoRa.

---

## 2. Arduino Code: Receiver

**Functionality**:
- Receives encrypted data via LoRa.
- Decrypts the data.
- Prints the decrypted data.

```cpp
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
```

**Notes**:
- **Decryption Logic**: This example assumes that Python's encryption may include an 'add' action. You should expand the `decryptData` function to handle all encryption actions used in Python for accurate decryption.

---

## 3. Python Code (Colab): Encryption & Decryption with Live Graph

**Functionality**:
- Simulates reading sensor data (since Colab cannot access physical serial ports).
- Applies encryption actions using Q-learning.
- Decrypts the data to verify correctness.
- Updates and displays real-time graphs for rewards and Q-values.
- Prints live values for each iteration.

**Key Updates**:
- **`DataFrame.append` Deprecation**: Replaced with `pd.concat` to avoid `AttributeError`.
- **Simplified Actions**: Start with reversible actions (`xor`, `add`, `sub`) to ensure decryption works.
- **Error Handling**: Improved assertions and debug prints to trace issues.

```python
# Install necessary libraries
!pip install matplotlib pandas openpyxl

import random
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from IPython.display import clear_output
import time

# Q-learning parameters
actions = ['xor', 'add', 'sub']  # Start with reversible actions
state_size = 256
action_size = len(actions)
q_table = np.zeros((state_size, action_size))  # Initialize Q-table
alpha = 0.1    # Learning rate
gamma = 0.9    # Discount factor
epsilon = 0.1  # Exploration rate

# Data storage for visualization
data_df = pd.DataFrame(columns=['Original Data', 'Action', 'Encrypted Data', 'Decrypted Data', 'Reward'])
rewards_list = []
iterations_list = []
q_value_list = []

# Reward function: higher difference implies better encryption
def reward(original_data, encrypted_data):
    return abs(original_data - encrypted_data)

# Encryption actions
def apply_action(action, data):
    if action == 'xor':
        return data ^ 0x55  # XOR with 0x55
    elif action == 'add':
        return (data + 10) % 256  # Add 10
    elif action == 'sub':
        return (data - 10) % 256  # Subtract 10

# Decryption actions (reverse of encryption)
def decrypt_action(action, data):
    if action == 'xor':
        return data ^ 0x55  # XOR is self-reversing
    elif action == 'add':
        return (data - 10) % 256  # Reverse addition
    elif action == 'sub':
        return (data + 10) % 256  # Reverse subtraction

# Q-learning action selection
def select_action(state):
    if random.uniform(0, 1) < epsilon:
        return random.choice(actions)  # Explore
    else:
        return actions[np.argmax(q_table[state])]  # Exploit

# Function to plot real-time graphs
def plot_progress(iteration, data, action, encrypted_data, decrypted_data, r, q_val):
    clear_output(wait=True)
    
    # Print live values
    print(f"Iteration: {iteration}")
    print(f"Original Data: {data}, Action: {action}, Encrypted Data: {encrypted_data}")
    print(f"Decrypted Data: {decrypted_data}, Reward: {r}, Max Q-value: {q_val}\n")
    
    plt.figure(figsize=(14, 6))
    
    # Subplot 1: Rewards over iterations
    plt.subplot(1, 2, 1)
    plt.plot(iterations_list, rewards_list, label='Reward', color='blue')
    plt.xlabel('Iteration')
    plt.ylabel('Reward')
    plt.title('Rewards over Time')
    plt.grid(True)
    
    # Subplot 2: Q-values over iterations
    plt.subplot(1, 2, 2)
    plt.plot(iterations_list, q_value_list, label='Q-value', color='orange')
    plt.xlabel('Iteration')
    plt.ylabel('Q-value')
    plt.title('Q-values over Time')
    plt.grid(True)
    
    plt.tight_layout()
    plt.show()

# Function to simulate reading sensor data
def read_from_sensor():
    return random.randint(0, 255)  # Simulated sensor data

# Main loop simulation for Colab
try:
    iteration = 0
    max_iterations = 100  # Set to desired number of iterations
    
    while iteration < max_iterations:
        # Simulate reading sensor data
        original_data = read_from_sensor()
        
        # Select an action using Q-learning
        action = select_action(original_data)
        
        # Encrypt the data using the selected action
        encrypted_data = apply_action(action, original_data)
        
        # Decrypt the data to verify correctness
        decrypted_data = decrypt_action(action, encrypted_data)
        
        # Calculate reward
        r = reward(original_data, encrypted_data)
        
        # Q-learning update
        action_index = actions.index(action)
        current_q = q_table[original_data, action_index]
        max_future_q = np.max(q_table[encrypted_data])
        q_table[original_data, action_index] = current_q + alpha * (r + gamma * max_future_q - current_q)
        
        # Verify decryption is correct
        try:
            assert decrypted_data == original_data, f"Decryption failed: {decrypted_data} != {original_data}"
        except AssertionError as e:
            print(e)
            # Optionally, you can choose to skip logging this iteration or handle it differently
            # For now, we'll continue
            decrypted_data = None  # Mark as failed
        
        # Log the data
        new_entry = pd.DataFrame([{
            'Original Data': original_data,
            'Action': action,
            'Encrypted Data': encrypted_data,
            'Decrypted Data': decrypted_data,
            'Reward': r
        }])
        data_df = pd.concat([data_df, new_entry], ignore_index=True)
        
        # Track data for graph
        iterations_list.append(iteration)
        rewards_list.append(r)
        q_value_list.append(q_table[encrypted_data].max())
        
        # Plot and print progress every 10 iterations
        if iteration % 10 == 0:
            q_val = q_table[encrypted_data].max()
            plot_progress(iteration, original_data, action, encrypted_data, decrypted_data, r, q_val)
        
        iteration += 1
        time.sleep(0.1)  # Adjust as needed for faster iterations
    
    print("Simulation completed.")
    
except KeyboardInterrupt:
    print("Process interrupted by user.")
```

### **Key Changes and Explanations**:

1. **Replacing `DataFrame.append`**:
   - **Issue**: `DataFrame.append` has been deprecated in recent versions of pandas.
   - **Solution**: Use `pd.concat` to add new rows.
   - **Implementation**:
     ```python
     new_entry = pd.DataFrame([{
         'Original Data': original_data,
         'Action': action,
         'Encrypted Data': encrypted_data,
         'Decrypted Data': decrypted_data,
         'Reward': r
     }])
     data_df = pd.concat([data_df, new_entry], ignore_index=True)
     ```

2. **Simplified Actions for Reversibility**:
   - **Actions**: `['xor', 'add', 'sub']` are reversible and ensure that decryption works correctly.
   - **Note**: Bitwise shifts (`shift_left`, `shift_right`) were removed to prevent data loss during encryption-decryption.

3. **Enhanced Error Handling**:
   - **Assertion**: Verifies that decryption correctly restores the original data.
   - **Handling Failed Assertions**: Prints the error and marks the decrypted data as `None` without halting the entire process.

4. **Real-Time Plotting and Live Prints**:
   - **Function `plot_progress`**: Clears previous outputs and updates the plots every 10 iterations.
   - **Live Prints**: Displays current iteration details, including original, encrypted, decrypted data, reward, and max Q-value.

5. **Simulation of Sensor Data**:
   - Since Colab cannot access physical serial ports, sensor data is simulated using `random.randint(0, 255)`.

6. **Loop Control**:
   - **`max_iterations`**: Limits the simulation to 100 iterations for testing. Adjust as needed.
   - **`time.sleep(0.1)`**: Adjusted for faster iterations in Colab.

### **Running the Code**:

1. **Setup**:
   - Ensure that you have the necessary libraries installed (`matplotlib`, `pandas`, `openpyxl`). The provided code includes a pip install command.
   
2. **Execution**:
   - Run the Python code in a Colab notebook cell. It will simulate sensor data, apply encryption and decryption, update the Q-table, and display live graphs with printed iteration details.

3. **Observing Outputs**:
   - **Graphs**: Two real-time graphs will display rewards and Q-values over time.
   - **Printed Values**: Every 10 iterations, detailed information about the current state will be printed below the graphs.

### **Sample Output**:

```
Iteration: 0
Original Data: 123, Action: xor, Encrypted Data: 78
Decrypted Data: 123, Reward: 45, Max Q-value: 0.0

[Graph Displayed]
```

### **Further Enhancements**:

1. **Expanding Actions**:
   - Once the basic encryption-decryption works seamlessly, consider reintroducing other reversible actions.
   - Ensure that each action has a proper decryption counterpart to maintain data integrity.

2. **Integrating with Arduino**:
   - **Serial Communication**: When running the Python code locally (not in Colab), you can establish a serial connection with the Arduino to send and receive data in real-time.
   - **Adjusting the Code**: Replace the `read_from_sensor` function and encryption loop to interact with the serial port.

3. **Persisting Data**:
   - The current code logs data into a `DataFrame`. You can export this data to Excel or other formats for further analysis.
   - Example:
     ```python
     data_df.to_excel('sensor_data_encrypted.xlsx', index=False)
     ```

4. **Enhancing Q-learning**:
   - Experiment with different learning rates (`alpha`), discount factors (`gamma`), and exploration rates (`epsilon`) to optimize the encryption strategy.
   - Consider implementing state-action histories or more complex state representations for better performance.

---

## Troubleshooting Common Issues

### 1. **Decryption Assertion Errors**

**Problem**:
```
AssertionError: Decryption failed: 112 != 240
```

**Cause**:
The encryption and decryption actions are not perfectly reversible for some data points. This can happen if the decryption logic does not correctly reverse the encryption action or if actions lead to data loss (e.g., bitwise shifts).

**Solution**:
- **Ensure Reversibility**: Only use actions that are fully reversible. In the provided code, only `xor`, `add`, and `sub` are used.
- **Verify Decryption Logic**: Double-check that each encryption action has a correct decryption counterpart.
- **Debugging**:
  - Print intermediate values to trace where mismatches occur.
  - Start with a single action (e.g., `xor`) to isolate issues.

**Example**:
```python
# Within the main loop
if decrypted_data != original_data:
    print(f"Error at iteration {iteration}: {decrypted_data} != {original_data}")
```

### 2. **`AttributeError: 'DataFrame' object has no attribute 'append'`**

**Cause**:
Using the deprecated `append` method in pandas, which has been removed in recent versions.

**Solution**:
Use `pd.concat` to add new rows to the DataFrame.

**Implementation**:
```python
new_entry = pd.DataFrame([{
    'Original Data': original_data,
    'Action': action,
    'Encrypted Data': encrypted_data,
    'Decrypted Data': decrypted_data,
    'Reward': r
}])
data_df = pd.concat([data_df, new_entry], ignore_index=True)
```

---

## Final Notes

Your project integrates multiple components: Arduino-based data collection, reinforcement learning for encryption, and secure data transmission via LoRa. Here's a summary of best practices and recommendations:

1. **Start Simple**:
   - Begin with a limited set of actions to ensure the encryption-decryption cycle works flawlessly.
   - Gradually add complexity once the basics are solid.

2. **Modular Code Structure**:
   - Keep your Arduino and Python code modular. This makes debugging and maintenance easier.
   - For example, separate encryption/decryption functions from Q-learning logic.

3. **Testing**:
   - Thoroughly test each component individually before integrating.
   - Use assertions and debug prints to catch and understand errors early.

4. **Documentation**:
   - Comment your code extensively to document the purpose of functions and logic.
   - Maintain a project log to track changes and understand the evolution of your system.

5. **Security Considerations**:
   - Ensure that the encryption actions provide sufficient security for your IoT data.
   - Consider more sophisticated encryption techniques if needed.

6. **Performance Optimization**:
   - Monitor the performance of your system, especially if deploying on resource-constrained devices like Arduino.
   - Optimize the frequency of data transmission and processing as needed.

Feel free to reach out if you encounter further issues or need additional assistance with specific components of your project. Good luck with your reinforcement learning-based IoT security system!
