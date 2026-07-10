import json
from kafka import KafkaConsumer

class EmergencyCallConsumer:
    def __init__(self, bootstrap_servers='kafka:9092', topic='emergency_calls'):
        self.topic = topic
        self.consumer = KafkaConsumer(
            topic,
            bootstrap_servers=bootstrap_servers,
            auto_offset_reset='latest',
            enable_auto_commit=True,
            group_id='test-consumer-group',
            value_deserializer=lambda x: json.loads(x.decode('utf-8')),
            key_deserializer=lambda x: x.decode('utf-8') if x else None
        )
        
        print("=" * 60)
        print(" Kafka Consumer (Test)")
        print("=" * 60)
        print(f"   Broker: {bootstrap_servers}")
        print(f"   Topic: {topic}")
        print("   Press Ctrl+C to stop")
        print("=" * 60)
    
    def run(self, max_messages=10):
        print(f"\n Reading up to {max_messages} messages...\n")
        count = 0
        
        try:
            for msg in self.consumer:
                count += 1
                print(f"[{count}] Key: {msg.key}")
                print(f"    Value: {json.dumps(msg.value, indent=2)}")
                print("-" * 40)
                if count >= max_messages:
                    break
        except KeyboardInterrupt:
            print("\n Stopped by user")
        finally:
            self.consumer.close()
            print(f"\n Read {count} messages")

if __name__ == "__main__":
    consumer = EmergencyCallConsumer()
    consumer.run(10)