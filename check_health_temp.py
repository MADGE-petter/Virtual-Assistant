#!/usr/bin/env python3
import sqlite3
import os
from datetime import datetime, timedelta

db_path = r'c:\Users\TUAN NGUYEN\Desktop\TLA\database\conversations.db'

if os.path.exists(db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    print("=== HEALTH SNAPSHOTS TEMPERATURE CHECK ===")
    
    # Check schema
    cursor.execute("PRAGMA table_info(health_snapshots)")
    columns = cursor.fetchall()
    print("Columns:")
    for col in columns:
        print(f"  {col[1]} {col[2]}")
    
    # Check sample data with temperature
    start_date = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
    user_name = "tuấn"
    
    print(f"\nQuery for user '{user_name}' from {start_date}:")
    
    cursor.execute("""
        SELECT cpu_percent, ram_percent, disk_percent, temperature, timestamp
        FROM health_snapshots
        WHERE date >= ? AND tenNguoiDung = ?
        ORDER BY timestamp DESC
        LIMIT 5
    """, (start_date, user_name))
    
    results = cursor.fetchall()
    print(f"Raw health data ({len(results)} rows):")
    for i, row in enumerate(results, 1):
        print(f"  {i}. CPU: {row[0]}%, RAM: {row[1]}%, Disk: {row[2]}%, Temp: {row[3]}°C, Time: {row[4]}")
    
    # Test the exact get_health_trends query
    print(f"\nTesting get_health_trends query:")
    cursor.execute('''
        SELECT AVG(cpu_percent), AVG(ram_percent), AVG(disk_percent), AVG(temperature),
               MAX(cpu_percent), MAX(ram_percent), MAX(disk_percent), MAX(temperature), COUNT(*)
        FROM health_snapshots
        WHERE date >= ? AND tenNguoiDung = ?
    ''', (start_date, user_name))
    
    row = cursor.fetchone()
    if row:
        print(f"Query result: {row}")
        print(f"AVG temperature: {row[3]}")
        print(f"MAX temperature: {row[7]}")
        print(f"COUNT: {row[8]}")
    else:
        print("No results from query")
    
    conn.close()
else:
    print(f"Database not found: {db_path}")
