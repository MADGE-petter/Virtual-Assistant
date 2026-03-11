#!/usr/bin/env python3
"""
Create admin_users table in database
"""
import sqlite3
import hashlib
import os

def create_admin_table():
    """Create admin_users table and insert default admin"""
    
    # Database path
    db_path = os.path.join(os.path.dirname(__file__), '..', 'conversations.db')
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Create admin_users table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS admin_users (
                maAdmin INTEGER PRIMARY KEY AUTOINCREMENT,
                tenAdmin TEXT UNIQUE NOT NULL,
                matKhauMaHoa TEXT NOT NULL,
                thoiGianTao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                thoiGianCapNhat TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Insert default admin user
        default_password = "admin123"
        password_hash = hashlib.sha256(default_password.encode()).hexdigest()
        
        cursor.execute('''
            INSERT OR IGNORE INTO admin_users (tenAdmin, matKhauMaHoa)
            VALUES (?, ?)
        ''', ('admin', password_hash))
        
        conn.commit()
        print("Admin table created successfully!")
        print("Default admin user: admin / admin123")
        
    except Exception as e:
        print(f"Error creating admin table: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    create_admin_table()
