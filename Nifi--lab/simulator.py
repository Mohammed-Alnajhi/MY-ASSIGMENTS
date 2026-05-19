import json
import random
import time
import os
from datetime import datetime

INPUT_DIR = r"C:\nifi_work\input"
os.makedirs(INPUT_DIR, exist_ok=True)


first_names = ["Ahmed", "Sara", "Mohamed", "Fatima", "Khalid", "Nora"]
last_names = ["Ali", "Hassan", "Omar", "Youssef", "Ibrahim"]
products = ["Laptop", "Mobile", "Tablet", "Headphones", "Charger", "Mouse"]
statuses = ["active", "inactive", "pending", "unknown", "?"]

def generate_record(seq_id):
    """يولد سجل واحد مع أخطاء متعمدة"""
    error_type = random.choice(["clean", "clean", "clean", "clean", "missing", "wrong_format"])
    
    if error_type == "missing":
        return {
            "id": seq_id,
            "first_name": "",
            "last_name": random.choice(last_names),
            "product": random.choice(products),
            "amount": None,
            "status": random.choice(statuses),
            "timestamp": datetime.now().isoformat()
        }
    elif error_type == "wrong_format":
        return {
            "id": str(seq_id) + "ERR",
            "first_name": random.choice(first_names),
            "last_name": random.choice(last_names),
            "product": random.choice(products),
            "amount": "invalid_amount",
            "status": random.choice(statuses),
            "timestamp": "invalid_date"
        }
    else:
        return {
            "id": seq_id,
            "first_name": random.choice(first_names),
            "last_name": random.choice(last_names),
            "product": random.choice(products),
            "amount": round(random.uniform(10, 5000), 2),
            "status": random.choice(["active", "inactive", "pending"]),
            "timestamp": datetime.now().isoformat()
        }

def generate_file(file_num):
    """يولد ملف JSON يحتوي على 2-5 سجلات"""
    num_records = random.randint(2, 5)
    records = []
    
    for i in range(num_records):
        records.append(generate_record(file_num * 100 + i))
        
       
        if random.random() < 0.2 and len(records) > 0:
            records.append(records[-1].copy())
    
    filename = os.path.join(INPUT_DIR, f"data_{int(time.time())}_{file_num}.json")
    with open(filename, 'w') as f:
        json.dump(records, f, indent=2)
    
    print(f"[{datetime.now().strftime('%H:%M:%S')}] Created: {filename} ({len(records)} records)")
    return filename

if __name__ == "__main__":
    print("=" * 50)
    print(" Data Simulator Started")
    print(f" Output directory: {INPUT_DIR}")
    print("  Generating files every 5 seconds...")
    print("=" * 50)
    
    counter = 0
    try:
        while True:
            generate_file(counter)
            counter += 1
            time.sleep(5)
    except KeyboardInterrupt:
        print("\n Simulator stopped.")