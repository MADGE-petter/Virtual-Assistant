#!/usr/bin/env python3
"""
Create users table and migrate data from users.json
"""
import sqlite3
import json
import os

def create_users_table():
    """Create users table and migrate from JSON"""
    
    # Database path
    db_path = os.path.join(os.path.dirname(__file__), '..', 'conversations.db')
    json_path = os.path.join(os.path.dirname(__file__), '..', 'users.json')
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Create users table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                maKhachHang INTEGER PRIMARY KEY AUTOINCREMENT,
                tenKhachHang TEXT UNIQUE NOT NULL,
                matKhauMaHoa TEXT NOT NULL,
                thoiGianTao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                thoiGianCapNhat TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Migrate from JSON if exists
        if os.path.exists(json_path):
            with open(json_path, 'r', encoding='utf-8') as f:
                users_data = json.load(f)
            
            for username, user_info in users_data.items():
                password_hash = user_info.get('password', '')
                created_at = user_info.get('created_at', '')
                
                cursor.execute('''
                    INSERT OR IGNORE INTO users (tenKhachHang, matKhauMaHoa, thoiGianTao)
                    VALUES (?, ?, ?)
                ''', (username, password_hash, created_at))
            
            print(f"Migrated {len(users_data)} users from JSON to database")
        
        conn.commit()
        print("Users table created successfully!")
        
        # Show users
        cursor.execute('SELECT tenKhachHang, thoiGianTao FROM users')
        users = cursor.fetchall()
        print("Users in database:")
        for user in users:
            print(f"  - {user[0]} (created: {user[1]})")
        
    except Exception as e:
        print(f"Error creating users table: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    create_users_table()
