from flask import Flask, render_template, request, jsonify
from flask_socketio import SocketIO
import redis
import json
import time
import threading
from datetime import datetime

app = Flask(__name__)
socketio = SocketIO(app)
r = redis.Redis(host='localhost', port=6379, db=0)

def redis_listener():
    pubsub = r.pubsub()
    pubsub.subscribe('order_updates')
    for message in pubsub.listen():
        if message['type'] == 'message':
            try:
                data = json.loads(message['data'].decode('utf-8'))
                socketio.emit('order_update', data)
            except:
                pass

def get_system_stats():
    stats = {
        'total_orders': r.zcard('delivery_times'),
        'orders_in_queue': r.llen('order_queue'),
        'in_progress_orders': len([key for key in r.keys('order:*') if r.exists(key)]),
        'available_drivers': r.scard('available_drivers'),
        'average_delivery_time': calculate_average_delivery_time(),
        'recent_orders': []
    }
    
    # Get recent active orders
    for key in r.keys('order:*'):
        if r.exists(key):  # Only non-expired orders
            order_data = {k.decode('utf-8'): v.decode('utf-8') for k, v in r.hgetall(key).items()}
            order_data['id'] = key.decode('utf-8').split(':')[1]
            stats['recent_orders'].append(order_data)
    
    return stats

def calculate_average_delivery_time():
    delivery_times = r.zrange('delivery_times', 0, -1, withscores=True)
    if not delivery_times:
        return 0
    
    total = sum(score for _, score in delivery_times)
    return int(total / len(delivery_times))

# Start Redis listener in a background thread
listener_thread = threading.Thread(target=redis_listener, daemon=True)
listener_thread.start()

# Initialize drivers if they don't exist
if r.scard('available_drivers') == 0:
    default_drivers = ['John', 'Sarah', 'Mike', 'Emma', 'David']
    for driver in default_drivers:
        r.sadd('available_drivers', driver)
    print(f"Initialized {len(default_drivers)} drivers")
else:
    print(f"Found {r.scard('available_drivers')} existing drivers")

@app.route('/')
def index():
    return render_template('index.html', stats=get_system_stats())

@app.route('/place_order', methods=['POST'])
def place_order():
    try:
        data = request.json
        order_id = f"ord{int(time.time())}"
        order_data = json.dumps({
            'id': order_id,
            'item': data['item'],
            'phone': data['phone'],
            'timestamp': time.time()
        })
        r.lpush('order_queue', order_data)
        return jsonify({'success': True, 'order_id': order_id})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})


@app.route('/complete_order/<order_id>', methods=['POST'])
def complete_order(order_id):
    try:
        order_key = f'order:{order_id}'
        
        # Check if order exists and has required fields
        if not r.exists(order_key):
            return jsonify({'success': False, 'message': 'Order not found'})
        
        driver = r.hget(order_key, 'driver')
        if not driver:
            return jsonify({'success': False, 'message': 'No driver assigned'})
        
        driver = driver.decode('utf-8')
        
        # Get dispatch time or use current time as fallback
        dispatch_time = r.hget(order_key, 'dispatch_time')
        if dispatch_time:
            dispatch_time = float(dispatch_time.decode('utf-8'))
            delivery_time = time.time() - dispatch_time
            r.zadd('delivery_times', {order_id: delivery_time})
        
        # Update order status
        r.hset(order_key, 'status', 'delivered')
        r.sadd('available_drivers', driver)
        r.expire(order_key, 600)  # 10 minutes
        
        # Publish update
        r.publish('order_updates', json.dumps({
            'id': order_id,
            'event': 'delivered',
            'driver': driver,
            'timestamp': time.time()
        }))
        
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})


if __name__ == "__main__":
    socketio.run(app, debug=True)