import redis
import time

r = redis.Redis(host='localhost', port=6379, db=0)

def show_dashboard():
    while True:
        print("\n--- Pizza Delivery Dashboard ---")
        print(f"Orders in queue: {r.llen('order_queue')}")
        print(f"Available drivers: {r.scard('available_drivers')}")
        
        # Count in-progress orders (simplified)
        keys = r.keys('order:*')
        in_progress = 0
        delivered = 0
        
        for key in keys:
            status = r.hget(key, 'status')
            if status:
                status = status.decode('utf-8')
                if status == 'on_the_way':
                    in_progress += 1
                elif status == 'delivered':
                    delivered += 1
        
        print(f"Orders in progress: {in_progress}")
        print(f"Recently delivered: {delivered}")
        
        time.sleep(3)

if __name__ == "__main__":
    show_dashboard()