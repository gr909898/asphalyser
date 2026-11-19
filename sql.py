import sqlite3
import os


def init_db():
    conn = sqlite3.connect('fractal_results.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            filename TEXT,
            dimension REAL,
            r_squared REAL
        )
    ''')
    conn.commit()
    conn.close()

def save_result(image_path, d_val, r2_val):
    conn = sqlite3.connect('fractal_results.db')
    cursor = conn.cursor()
    filename = os.path.basename(image_path)
    
    cursor.execute('''
        INSERT INTO results (filename, dimension, r_squared) 
        VALUES (?, ?, ?)
    ''', (filename, d_val, r2_val))
    
    conn.commit()
    conn.close()
