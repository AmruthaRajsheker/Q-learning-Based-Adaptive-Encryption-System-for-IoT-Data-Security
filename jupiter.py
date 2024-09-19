# 3. Python Code (Colab): Encryption & Decryption with Live Graph

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
