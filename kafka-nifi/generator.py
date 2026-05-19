import csv
import time
import random
import uuid
import os
from datetime import datetime

OUTPUT_DIR = "nifi_input"

if not os.path.exists(OUTPUT_DIR):
    os.makedirs(OUTPUT_DIR)

customers = [f"CUST{str(i).zfill(3)}" for i in range(1, 101)]
statuses = ["COMPLETED", "PENDING", "FAILED", "REFUNDED"]

def generate_record():
    """Generates a single order record with intentional anomalies to simulate real-world messy data."""
    transaction_id = random.randint(1000, 99999)
    customer_id = random.choice(customers)
    amount = round(random.uniform(10.0, 5000.0), 2)
    status = random.choice(statuses)
    
    ts_choice = random.randint(1, 3)
    if ts_choice == 1:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    elif ts_choice == 2:
        timestamp = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    else:
        timestamp = str(int(time.time()))  

   
    anomaly_choice = random.random()
    if anomaly_choice < 0.05:
       
        amount = ""
    elif anomaly_choice < 0.10:
      
        amount = "INVALID_AMT"
    elif anomaly_choice < 0.15:
        
        return [transaction_id, customer_id]
    elif anomaly_choice < 0.20:
      
        customer_id = None
        
    return [transaction_id, customer_id, amount, timestamp, status]

def generate_data_stream():
    print(f"Starting real-time data generator. Writing to ./{OUTPUT_DIR}/")
    print("Press Ctrl+C to stop.")
    
    file_counter = 1
    
    try:
        while True:
          
            filename = f"orders_{int(time.time())}.csv"
            filepath = os.path.join(OUTPUT_DIR, filename)
            
            num_records = random.randint(50, 200)
            records = []
            
            for _ in range(num_records):
                record = generate_record()
                records.append(record)
                
                if random.random() < 0.05:
                    records.append(record)
            
            with open(filepath, mode='w', newline='') as file:
                writer = csv.writer(file)
                writer.writerow(["transaction_id", "customer_id", "amount", "timestamp", "status"])
                for row in records:
                    writer.writerow(row)
                    
            print(f"Generated {filepath} with {len(records)} records.")
            
            file_counter += 1
            time.sleep(5)
            
    except KeyboardInterrupt:
        print("\nData generation stopped by user.")

if __name__ == "__main__":
    generate_data_stream()
