import json
import random
import time
from datetime import datetime
from kafka import KafkaProducer, KafkaAdminClient
from kafka.admin import NewTopic
from kafka.errors import TopicAlreadyExistsError

class EmergencyCallSimulator:
    def __init__(self, bootstrap_servers='kafka:9092', topic='emergency_calls'):
        self.topic = topic
        
        
        try:
            admin_client = KafkaAdminClient(bootstrap_servers=bootstrap_servers)
            existing_topics = admin_client.list_topics()
            
            if topic not in existing_topics:
                print(f"Creating topic '{topic}' with 3 partitions...")
                new_topic = NewTopic(name=topic, num_partitions=3, replication_factor=1)
                admin_client.create_topics([new_topic])
                print(f"Topic '{topic}' created successfully.")
            else:
                print(f"Topic '{topic}' already exists.")
            
            admin_client.close()
        except Exception as e:
            print(f"Warning: Could not create/verify topic via AdminClient: {e}")

        self.producer = KafkaProducer(
            bootstrap_servers=bootstrap_servers,
            value_serializer=lambda v: json.dumps(v).encode('utf-8'),
            key_serializer=lambda k: k.encode('utf-8') if k else None,
            acks='all',
            retries=3
        )
        
        self.incident_types = [
            'Theft', 'Assault', 'Burglary', 'Vandalism',
            'Fire', 'Medical Emergency', 'Domestic Disturbance',
            'Traffic Accident', 'Noise Complaint', 'Suspicious Activity'
        ]
        
        self.priorities = ['Low', 'Medium', 'High', 'Critical']
        self.statuses = ['active', 'dispatched', 'resolved']
        self.precincts = [f'Precinct-{i:02d}' for i in range(1, 11)]
        
        self.lat_range = (40.70, 40.85)
        self.lng_range = (-74.05, -73.85)
        self.total_sent = 0
        
        print("=" * 60)
        print("Emergency Call Simulator")
        print("=" * 60)
        print(f"   Broker: {bootstrap_servers}")
        print(f"   Topic: {topic}")
        print("   Press Ctrl+C to stop")
        print("=" * 60)
    
    def generate_call(self):
        timestamp = datetime.utcnow()
        call_id = f"CALL_{timestamp.strftime('%Y%m%d%H%M%S')}_{random.randint(100, 999)}"
        
        return {
            'call_id': call_id,
            'incident_type': random.choice(self.incident_types),
            'timestamp': timestamp.isoformat(),
            'location': {
                'latitude': round(random.uniform(*self.lat_range), 6),
                'longitude': round(random.uniform(*self.lng_range), 6)
            },
            'priority': random.choice(self.priorities),
            'status': random.choice(self.statuses),
            'precinct': random.choice(self.precincts),
            'caller_phone': f"{random.randint(200,999)}-{random.randint(100,999)}-{random.randint(1000,9999)}",
            'description': f"Emergency: {random.choice(self.incident_types)} reported"
        }
    
    def send_call(self, call):
        try:
            future = self.producer.send(self.topic, key=call['call_id'], value=call)
            result = future.get(timeout=10)
            self.total_sent += 1
            print(f"[OK] [{self.total_sent:04d}] {call['call_id']} - {call['incident_type']} ({call['priority']})", flush=True)
            return True
        except Exception as e:
            print(f"[FAIL]: {call['call_id']} - {str(e)}")
            return False
    
    def run(self, interval=1.0):
        try:
            while True:
                call = self.generate_call()
                self.send_call(call)
                time.sleep(random.uniform(0.5, interval))
        except KeyboardInterrupt:
            print("\n" + "=" * 60)
            print(f"[STOP] Stopped after {self.total_sent} messages")
            print("=" * 60)
        finally:
            self.producer.flush()
            self.producer.close()
            print("[CLOSE] Producer closed")

if __name__ == "__main__":
    simulator = EmergencyCallSimulator()
    simulator.run(1.0)
