import sqlite3
import json

DB = "pixelwar.db"
WIDTH = 200
HEIGHT = 200

def init_db():
    conn = sqlite3.connect(DB)
    c = conn.cursor()

    c.execute("""
        CREATE TABLE IF NOT EXISTS grid_state (
            id INTEGER PRIMARY KEY,
            width INTEGER,
            height INTEGER,
            grid_json TEXT
        )
    """)

    c.execute("SELECT COUNT(*) FROM grid_state")
    if c.fetchone()[0] == 0:
        grid = [["#ffffff" for _ in range(WIDTH)] for _ in range(HEIGHT)]
        c.execute("INSERT INTO grid_state (width, height, grid_json) VALUES (?, ?, ?)",
                  (WIDTH, HEIGHT, json.dumps(grid)))

    conn.commit()
    conn.close()

if __name__ == "__main__":
    init_db()
    print("Base de données initialisée ✔")
