import csv
import random
import time
import os
from datetime import datetime

os.makedirs("nifi_input", exist_ok=True)

customers = [f"CUST{i:05d}" for i in range(1, 101)]
types = ['DEPOSIT', 'WITHDRAWAL', 'TRANSFER', 'PAYMENT']
statuses = ['COMPLETED', 'PENDING', 'FAILED']

print("Starting data generator...")

while True:
    filename = f"transactions_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    filepath = f"nifi_input/{filename}"
    
    with open(filepath, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['transaction_id', 'customer_id', 'amount', 'timestamp', 'transaction_type', 'status'])
        
        for i in range(50):
            row = [
                f"T{datetime.now().strftime('%Y%m%d%H%M%S')}{i:04d}",
                random.choice(customers),
                round(random.uniform(10, 5000), 2),
                datetime.now().isoformat(),
                random.choice(types),
                random.choice(statuses)
            ]
            writer.writerow(row)
    
    print(f"Created: {filename}")
    time.sleep(10)