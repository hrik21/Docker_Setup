import sqlite3
import os

DATABASE_NAME = 'pdfs.db'

def init_database():
    """Create the database and tables if they don't exist"""
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS pdfs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            filename TEXT NOT NULL,
            original_filename TEXT NOT NULL,
            file_path TEXT NOT NULL,
            upload_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()
    print("Database initialized successfully")

def save_pdf_to_db(filename, original_filename, file_path):
    """Save PDF information to database and return the new PDF ID"""
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO pdfs (filename, original_filename, file_path)
        VALUES (?, ?, ?)
    ''', (filename, original_filename, file_path))
    conn.commit()
    pdf_id = cursor.lastrowid
    conn.close()
    print(f"PDF saved to database with ID: {pdf_id}")
    return pdf_id

def get_pdf_by_id(pdf_id):
    """Get PDF information by ID"""
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM pdfs WHERE id = ?', (pdf_id,))
    pdf = cursor.fetchone()
    conn.close()
    return pdf

def get_pdf_file_path(pdf_id):
    """Get just the file path for a PDF by ID"""
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    cursor.execute('SELECT file_path FROM pdfs WHERE id = ?', (pdf_id,))
    result = cursor.fetchone()
    conn.close()
    return result[0] if result else None

def get_all_pdfs():
    """Get all PDFs ordered by upload date (newest first)"""
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM pdfs ORDER BY upload_date DESC')
    pdfs = cursor.fetchall()
    conn.close()
    return pdfs

def get_database_stats():
    """Get database statistics"""
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    
    # Get table info and format it nicely
    cursor.execute("PRAGMA table_info(pdfs)")
    raw_columns = cursor.fetchall()
    
    # Format columns into readable structure
    columns = []
    for col in raw_columns:
        columns.append({
            'name': col[1],
            'type': col[2],
            'required': bool(col[3]),
            'default': col[4],
            'primary_key': bool(col[5])
        })
    
    # Get total count
    cursor.execute('SELECT COUNT(*) FROM pdfs')
    total_count = cursor.fetchone()[0]
    
    # Get database file size
    db_size = os.path.getsize(DATABASE_NAME) if os.path.exists(DATABASE_NAME) else 0
    
    conn.close()
    return {
        'table_name': 'pdfs',
        'columns': columns,
        'total_records': total_count,
        'database_size_bytes': db_size,
        'database_size_mb': round(db_size / (1024 * 1024), 2)
    }