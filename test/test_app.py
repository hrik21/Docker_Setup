import sys
import os
import unittest
import tempfile
import shutil
import sqlite3
import json
from unittest.mock import patch, MagicMock

# Add the parent directory to sys.path so modules can be imported
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import database
import file_handler
from app import app

class TestDatabase(unittest.TestCase):
    """Test all database functions"""
    
    def setUp(self):
        """Set up test database before each test"""
        self.test_db = 'test_pdfs.db'
        self.original_db = database.DATABASE_NAME
        database.DATABASE_NAME = self.test_db
        database.init_database()
    
    def tearDown(self):
        """Clean up after each test"""
        database.DATABASE_NAME = self.original_db
        if os.path.exists(self.test_db):
            os.remove(self.test_db)
    
    def test_init_database(self):
        """Test database initialization"""
        self.assertTrue(os.path.exists(self.test_db))
        
        conn = sqlite3.connect(self.test_db)
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='pdfs'")
        table_exists = cursor.fetchone()
        conn.close()
        
        self.assertIsNotNone(table_exists)
    
    def test_save_and_get_pdf(self):
        """Test saving and retrieving PDF"""
        pdf_id = database.save_pdf_to_db('test.pdf', 'original.pdf', '/path/test.pdf')
        
        self.assertIsInstance(pdf_id, int)
        self.assertGreater(pdf_id, 0)
        
        pdf = database.get_pdf_by_id(pdf_id)
        self.assertIsNotNone(pdf)
        self.assertEqual(pdf[1], 'test.pdf')
    
    def test_get_database_stats(self):
        """Test database statistics"""
        database.save_pdf_to_db('test1.pdf', 'orig1.pdf', '/path1.pdf')
        database.save_pdf_to_db('test2.pdf', 'orig2.pdf', '/path2.pdf')
        
        stats = database.get_database_stats()
        
        self.assertIn('table_name', stats)
        self.assertIn('total_records', stats)
        self.assertEqual(stats['total_records'], 2)
        self.assertEqual(len(stats['columns']), 5)


class TestFlaskApp(unittest.TestCase):
    """Test Flask application routes"""
    
    def setUp(self):
        """Set up Flask test client"""
        app.config['TESTING'] = True
        self.client = app.test_client()
        
        self.test_db = 'test_flask.db'
        self.original_db = database.DATABASE_NAME
        database.DATABASE_NAME = self.test_db
        database.init_database()
    
    def tearDown(self):
        """Clean up test database"""
        database.DATABASE_NAME = self.original_db
        if os.path.exists(self.test_db):
            os.remove(self.test_db)
    
    def test_home(self):
        """Test home page"""
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
    
    def test_list_pdfs(self):
        """Test PDF list page"""
        response = self.client.get('/list')
        self.assertEqual(response.status_code, 200)
    
    def test_admin_db(self):
        """Test admin database page"""
        response = self.client.get('/admin/db')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Database Admin', response.data)
    
    def test_api_stats(self):
        """Test API stats endpoint"""
        response = self.client.get('/api/stats')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content_type, 'application/json')
        
        data = json.loads(response.data)
        self.assertIn('table_name', data)
        self.assertIn('total_records', data)
    
    def test_pdf_not_found(self):
        """Test non-existent PDF handling"""
        response = self.client.get('/pdf/999')
        self.assertEqual(response.status_code, 404)


class TestFileHandler(unittest.TestCase):
    """Test file handler functions"""
    
    def setUp(self):
        """Set up test environment"""
        self.test_upload_dir = 'test_uploads'
        self.original_upload_folder = file_handler.UPLOAD_FOLDER
        file_handler.UPLOAD_FOLDER = self.test_upload_dir
    
    def tearDown(self):
        """Clean up test files"""
        file_handler.UPLOAD_FOLDER = self.original_upload_folder
        if os.path.exists(self.test_upload_dir):
            shutil.rmtree(self.test_upload_dir)
    
    def test_setup_upload_folder(self):
        """Test upload folder creation"""
        file_handler.setup_upload_folder()
        self.assertTrue(os.path.exists(self.test_upload_dir))
    
    def test_is_allowed_file(self):
        """Test file type validation"""
        self.assertTrue(file_handler.is_allowed_file('test.pdf'))
        self.assertFalse(file_handler.is_allowed_file('test.txt'))
        self.assertFalse(file_handler.is_allowed_file('test'))


if __name__ == '__main__':
    unittest.main()