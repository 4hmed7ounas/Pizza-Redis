import redis
import json
import random
import time

r = redis.Redis(host='localhost', port=6379, db=0)
MAX_RETRIES = 3
RETRY_DELAY = 10  # seconds

def dispatch_order():
    if r.llen('order_queue') == 0:
        print("No orders in queue")
        time.sleep(5)
        return False
    
    if r.scard('available_drivers') == 0:
        print("No available drivers - will retry")
        
        # Check if any orders have exceeded retry count
        orders = [json.loads(o.decode('utf-8')) for o in r.lrange('order_queue', 0, -1)]
        for order in orders:
            retries = int(order.get('retries', 0))
            if retries >= MAX_RETRIES:
                print(f"Order {order['id']} exceeded max retries - cancelling")
                r.lrem('order_queue', 1, json.dumps(order))
                r.publish('order_updates', json.dumps({
                    'id': order['id'],
                    'event': 'cancelled',
                    'reason': 'no_drivers_available',
                    'timestamp': time.time()
                }))
        
        time.sleep(RETRY_DELAY)
        return False
    
    # Get next order
    order_data = r.rpop('order_queue')
    order = json.loads(order_data.decode('utf-8'))
    order_id = order['id']
    
    # Check if this order needs to be retried
    if 'retries' in order:
        order['retries'] += 1
    else:
        order['retries'] = 1
    
    driver = random.choice(list(r.smembers('available_drivers'))).decode('utf-8')
    
    # Record dispatch time for delivery time calculation
    order['dispatch_time'] = time.time()
    
    # Save order details
    r.hset(f'order:{order_id}', 'status', 'on_the_way')
    r.hset(f'order:{order_id}', 'driver', driver)
    r.hset(f'order:{order_id}', 'item', order['item'])
    r.hset(f'order:{order_id}', 'phone', order['phone'])
    r.hset(f'order:{order_id}', 'dispatch_time', order['dispatch_time'])
    
    r.srem('available_drivers', driver)
    
    r.publish('order_updates', json.dumps({
        'id': order_id,
        'event': 'out_for_delivery',
        'driver': driver,
        'item': order['item'],
        'timestamp': time.time()
    }))
    
    print(f"Dispatched order {order_id} to {driver}")
    return True

if __name__ == "__main__":
    while True:
        dispatch_order()