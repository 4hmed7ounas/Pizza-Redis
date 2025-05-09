import redis
import sys
import time
import json

r = redis.Redis(host='localhost', port=6379, db=0)

def complete_delivery(order_id):
    r.hset(f'order:{order_id}', 'status', 'delivered')
    driver = r.hget(f'order:{order_id}', 'driver').decode('utf-8')
    r.sadd('available_drivers', driver)
    
    r.publish('order_updates', json.dumps({
        'id': order_id,
        'event': 'delivered',
        'driver': driver,
        'timestamp': int(time.time())
    }))
    
    r.expire(f'order:{order_id}', 1800)
    print(f"Order {order_id} completed. Driver {driver} available.")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python complete.py <order_id>")
        sys.exit(1)
    complete_delivery(sys.argv[1])