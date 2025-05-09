import redis
import json

r = redis.Redis(host='localhost', port=6379, db=0)

def listen_for_updates():
    pubsub = r.pubsub()
    pubsub.subscribe('order_updates')
    
    print("Listening for order updates...")
    for message in pubsub.listen():
        if message['type'] == 'message':
            data = json.loads(message['data'])
            print(f"\nNew Order Event: {data}\n")

if __name__ == "__main__":
    listen_for_updates()