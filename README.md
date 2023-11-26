# Supermarket Counter Management System

## Overview

This Python program simulates a counter management system for a supermarket. It uses a multi-threaded approach to manage customer entries, exits, and counter load balancing. The system provides a graphical user interface (GUI) for the manager to monitor and control the counters.

## Features

- **Customer Entry and Exit:**
  - New customers can enter the supermarket and be assigned to a counter.
  - Existing customers can exit the supermarket, updating counter statistics.

- **Load Balancing:**
  - The program dynamically balances the load across open counters based on a custom weightage metric.

- **Graphical User Interface (GUI):**
  - The GUI provides a visual representation of counter details, including weightage and queue length.
  - Managers can change the status of counters and adjust the threshold for load balancing.


## Pre-requisites

- Python 3.x
- Required Python packages: `tkinter` (included in standard Python distribution)

## Running the Program

1. Clone the repository:

    **git clone <repository-url>
    cd supermarket-counter-management**
    

2. Run the main script:

    **python Counter-management.py**
  

3. Follow the on-screen instructions to interact with the program.

## Configuration

- The program prompts the user for configuration settings such as the maximum length for each counter, the maximum number of counters, and the initial number of counters.

## Structure

- **customer_map function :** This function runs on the main thread and looks after the mapping of customers to the counters
- **poller function** : This function periodically polls each counter, seeks the exit frequency and calculates the rate at which customers are leaving that counter (to facilitate the load balancing)
- **gui_thread** :Implements the graphical user interface using tkinter.

# Authors
1. **Pavan R Kashyap** : In-charge of load balancing function codebase and threads (custom_map)
2. **Phaneesh R Katti**: In-charge of load balancing function codebase and threads (main)
3. **Niveditha K**: In-charge of poller and threads
4. **Prajwal V Bhat** : In-charge of GUI and threads


# Future Improvements

1. **Enhanced GUI:**
   - Address existing issues with the GUI to improve user-friendliness.
   - Implement design improvements for a more intuitive and visually appealing interface.
   - Ensure seamless thread passing for better communication and synchronization.

2. **Database Integration:**
   - Explore the integration of SQL and databases into the Supermarket Counter Management System.
   - Implement a database to store and retrieve data related to customer transactions, counter status, and load balancing metrics.
   - Leverage the database for historical analytics, reporting, and persistent data storage.



