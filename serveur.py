from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit
import sqlite3, json, time, threading
import os

DB = "pixelwar.db"
COOLDOWN_SECONDS = 1
GRID_LOCK = threading.Lock()

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret-key'
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='eventlet')

def load_grid():
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("SELECT width, height, grid_json FROM grid_state LIMIT 1")
    row = c.fetchone()
    conn.close()
    width, height, grid_json = row
    return {"width": width, "height": height, "grid": json.loads(grid_json)}

def save_grid(grid_obj):
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("UPDATE grid_state SET grid_json = ? WHERE id = 1",
              (json.dumps(grid_obj['grid']),))
    conn.commit()
    conn.close()

@app.route("/")
def index():
    return render_template("index.html")

last_place = {}

def get_client_key():
    ip = request.remote_addr or "?"
    sid = request.sid
    return f"{ip}:{sid}"

@socketio.on("connect")
def on_connect():
    grid_obj = load_grid()
    emit("full_grid", grid_obj)

@socketio.on("place_pixel")
def place_pixel(data):
    x = int(data.get("x", -1))
    y = int(data.get("y", -1))
    color = str(data.get("color", ""))

    grid_obj = load_grid()
    w, h = grid_obj["width"], grid_obj["height"]

    if not (0 <= x < w and 0 <= y < h):
        return

    if not (color.startswith("#") and len(color) == 7):
        return

    key = get_client_key()
    now = time.time()

    if now - last_place.get(key, 0) < COOLDOWN_SECONDS:
        remaining = COOLDOWN_SECONDS - (now - last_place[key])
        emit("cooldown", {"remaining": remaining})
        return

    with GRID_LOCK:
        grid_obj = load_grid()
        grid_obj["grid"][y][x] = color
        save_grid(grid_obj)

    last_place[key] = now

    socketio.emit("pixel_update", {"x": x, "y": y, "color": color})

if __name__ == "__main__":
    # Auto-crée la DB sur Render
    if not os.path.exists(DB):
        from db_init import init_db
        init_db()

    port = int(os.environ.get("PORT", 5000))
    socketio.run(app, host="0.0.0.0", port=port)
