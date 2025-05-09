# Pizza-Redis Delivery System

A real-time pizza delivery management system using Flask, Redis, and Socket.IO.

## Features
- Place pizza orders via a web dashboard
- Real-time updates for order status
- Automatic driver dispatching
- Order completion and delivery time tracking
- CLI dashboard for live stats
- Redis Pub/Sub for real-time event logs

## Requirements
- Python 3.7+
- Redis server (running locally or accessible via network)
- pip (Python package manager)

## Python Dependencies
See `requirements.txt` for full list. Main packages:
- flask
- flask_socketio
- redis

## Setup Instructions

1. **Install Redis**
   - Download and install Redis from https://redis.io/download or use your OS package manager.
   - Start the Redis server (default port 6379).

2. **Clone this repository**
   ```bash
   git clone [<your-repo-url>](https://github.com/4hmed7ounas/Pizza-Redis.git)
   cd Pizza-Redis
   ```

3. **Install Python dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Start the Flask web app**
   ```bash
   python app.py
   ```
   - The app will run at http://127.0.0.1:5000

5. **(Optional) Start the dispatcher in a new terminal**
   ```bash
   python dispatch.py
   ```
   - This will automatically assign drivers to new orders.

6. **(Optional) Start the CLI dashboard in a new terminal**
   ```bash
   python dashboard.py
   ```
   - See live stats in your terminal.

## File Structure
- `app.py` - Main Flask web app
- `dispatch.py` - Driver assignment/dispatch logic
- `dashboard.py` - CLI dashboard for stats
- `complete.py` - Mark order as delivered via CLI
- `listener.py` - Listen to order events via CLI
- `templates/index.html` - Web dashboard UI
- `static/style.css` - Web dashboard styling

## Notes
- Make sure Redis is running before starting the app.
- Orders and drivers are managed in Redis. Delivered orders expire automatically after 10 minutes (configurable in `app.py`).
- For production, use a production-ready web server and secure your Redis instance.

## License
MIT
