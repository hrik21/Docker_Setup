#!/usr/bin/env python3
import unittest
import os
import sqlite3
import json
import sys

# Import your database module
import database

class TestDatabase(unittest.TestCase):
    """Test all database functions"""
    
    def setUp(self):
        """Set up test database before each test"""
        # Create a temporary database for testing
        self.test_db = 'test_pdfs.db'
        # Backup original database name
        self.original_db = database.DATABASE_NAME
        # Use test database
        database.DATABASE_NAME = self.test_db
        # Initialize test database
        database.init_database()
    
    def tearDown(self):
        """Clean up after each test"""
        # Restore original database name
        database.DATABASE_NAME = self.original_db
        # Remove test database
        if os.path.exists(self.test_db):
            os.remove(self.test_db)
    
    def test_init_database(self):
        """Test database initialization"""
        print("Testing database initialization...")
        self.assertTrue(os.path.exists(self.test_db))
        
        # Check if table was created
        conn = sqlite3.connect(self.test_db)
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='pdfs'")
        table_exists = cursor.fetchone()
        conn.close()
        
        self.assertIsNotNone(table_exists)
        print("✓ Database and table created successfully")
    
    def test_save_pdf_to_db(self):
        """Test saving PDF to database"""
        print("Testing PDF save to database...")
        pdf_id = database.save_pdf_to_db(
            'test.pdf', 
            'original_test.pdf', 
            '/path/to/test.pdf'
        )
        
        self.assertIsInstance(pdf_id, int)
        self.assertGreater(pdf_id, 0)
        print(f"✓ PDF saved with ID: {pdf_id}")
    
    def test_get_pdf_by_id(self):
        """Test retrieving PDF by ID"""
        print("Testing PDF retrieval by ID...")
        # First save a PDF
        pdf_id = database.save_pdf_to_db(
            'test.pdf', 
            'original_test.pdf', 
            '/path/to/test.pdf'
        )
        
        # Then retrieve it
        pdf = database.get_pdf_by_id(pdf_id)
        
        self.assertIsNotNone(pdf)
        self.assertEqual(pdf[1], 'test.pdf')  # filename
        self.assertEqual(pdf[2], 'original_test.pdf')  # original_filename
        self.assertEqual(pdf[3], '/path/to/test.pdf')  # file_path
        print(f"✓ PDF retrieved: {pdf[1]}")
    
    def test_get_pdf_by_id_not_found(self):
        """Test retrieving non-existent PDF"""
        print("Testing non-existent PDF retrieval...")
        pdf = database.get_pdf_by_id(999)
        self.assertIsNone(pdf)
        print("✓ Correctly returned None for non-existent PDF")
    
    def test_get_pdf_file_path(self):
        """Test getting PDF file path"""
        print("Testing PDF file path retrieval...")
        # Save a PDF first
        pdf_id = database.save_pdf_to_db(
            'test.pdf', 
            'original_test.pdf', 
            '/path/to/test.pdf'
        )
        
        # Get file path
        file_path = database.get_pdf_file_path(pdf_id)
        self.assertEqual(file_path, '/path/to/test.pdf')
        print(f"✓ File path retrieved: {file_path}")
    
    def test_get_pdf_file_path_not_found(self):
        """Test getting file path for non-existent PDF"""
        print("Testing file path for non-existent PDF...")
        file_path = database.get_pdf_file_path(999)
        self.assertIsNone(file_path)
        print("✓ Correctly returned None for non-existent PDF path")
    
    def test_get_all_pdfs(self):
        """Test getting all PDFs"""
        print("Testing get all PDFs...")
        # Save multiple PDFs
        id1 = database.save_pdf_to_db('test1.pdf', 'orig1.pdf', '/path1.pdf')
        id2 = database.save_pdf_to_db('test2.pdf', 'orig2.pdf', '/path2.pdf')
        
        pdfs = database.get_all_pdfs()
        
        self.assertEqual(len(pdfs), 2)
        # Check that we got both PDFs (order may vary due to timing)
        filenames = [pdf[1] for pdf in pdfs]
        self.assertIn('test1.pdf', filenames)
        self.assertIn('test2.pdf', filenames)
        print(f"✓ Retrieved {len(pdfs)} PDFs: {filenames}")
    
    def test_get_database_stats(self):
        """Test database statistics"""
        print("Testing database statistics...")
        # Add some test data
        database.save_pdf_to_db('test1.pdf', 'orig1.pdf', '/path1.pdf')
        database.save_pdf_to_db('test2.pdf', 'orig2.pdf', '/path2.pdf')
        
        stats = database.get_database_stats()
        
        # Check structure
        self.assertIn('table_name', stats)
        self.assertIn('columns', stats)
        self.assertIn('total_records', stats)
        self.assertIn('database_size_bytes', stats)
        self.assertIn('database_size_mb', stats)
        
        # Check values
        self.assertEqual(stats['table_name'], 'pdfs')
        self.assertEqual(stats['total_records'], 2)
        self.assertEqual(len(stats['columns']), 5)
        self.assertGreater(stats['database_size_bytes'], 0)
        
        print(f"✓ Stats: {stats['total_records']} records, {stats['database_size_mb']} MB")
        print(f"✓ Columns: {[col['name'] for col in stats['columns']]}")
    
    def test_database_stats_json_format(self):
        """Test that database stats can be converted to JSON"""
        print("Testing JSON serialization...")
        # Add test data
        database.save_pdf_to_db('json_test.pdf', 'orig_json.pdf', '/json/path.pdf')
        
        stats = database.get_database_stats()
        
        # Try to convert to JSON
        try:
            json_str = json.dumps(stats, indent=2)
            parsed_back = json.loads(json_str)
            
            self.assertEqual(parsed_back['table_name'], 'pdfs')
            self.assertEqual(parsed_back['total_records'], 1)
            
            print("✓ JSON serialization successful")
            print(f"Sample JSON output:\n{json_str[:200]}...")
            
        except Exception as e:
            self.fail(f"JSON serialization failed: {e}")


class TestDatabaseIntegration(unittest.TestCase):
    """Integration tests for database operations"""
    
    def setUp(self):
        """Set up integration test environment"""
        self.test_db = 'test_integration.db'
        self.original_db = database.DATABASE_NAME
        database.DATABASE_NAME = self.test_db
        database.init_database()
    
    def tearDown(self):
        """Clean up integration test environment"""
        database.DATABASE_NAME = self.original_db
        if os.path.exists(self.test_db):
            os.remove(self.test_db)
    
    def test_full_pdf_workflow(self):
        """Test complete PDF workflow"""
        print("Testing complete PDF workflow...")
        
        # Step 1: Save PDF to database
        pdf_id = database.save_pdf_to_db(
            'workflow_test.pdf',
            'original_workflow_test.pdf',
            '/uploads/workflow_test.pdf'
        )
        print(f"Step 1: PDF saved with ID {pdf_id}")
        
        # Step 2: Retrieve PDF by ID
        pdf = database.get_pdf_by_id(pdf_id)
        self.assertIsNotNone(pdf)
        self.assertEqual(pdf[1], 'workflow_test.pdf')
        print(f"Step 2: PDF retrieved: {pdf[1]}")
        
        # Step 3: Get file path
        file_path = database.get_pdf_file_path(pdf_id)
        self.assertEqual(file_path, '/uploads/workflow_test.pdf')
        print(f"Step 3: File path: {file_path}")
        
        # Step 4: Check in all PDFs list
        all_pdfs = database.get_all_pdfs()
        self.assertEqual(len(all_pdfs), 1)
        self.assertEqual(all_pdfs[0][0], pdf_id)
        print(f"Step 4: Found in all PDFs list")
        
        # Step 5: Check stats
        stats = database.get_database_stats()
        self.assertEqual(stats['total_records'], 1)
        print(f"Step 5: Stats show {stats['total_records']} record")
        
        print("✓ Complete workflow test passed!")
    
    def test_multiple_pdfs_workflow(self):
        """Test workflow with multiple PDFs"""
        print("Testing multiple PDFs workflow...")
        
        # Add multiple PDFs
        pdf_ids = []
        for i in range(5):
            pdf_id = database.save_pdf_to_db(
                f'test_{i}.pdf',
                f'original_test_{i}.pdf',
                f'/uploads/test_{i}.pdf'
            )
            pdf_ids.append(pdf_id)
        
        print(f"Added {len(pdf_ids)} PDFs")
        
        # Check all are retrievable
        for pdf_id in pdf_ids:
            pdf = database.get_pdf_by_id(pdf_id)
            self.assertIsNotNone(pdf)
        
        # Check total count
        all_pdfs = database.get_all_pdfs()
        self.assertEqual(len(all_pdfs), 5)
        
        # Check stats
        stats = database.get_database_stats()
        self.assertEqual(stats['total_records'], 5)
        
        print(f"✓ All {len(pdf_ids)} PDFs working correctly")


def run_tests():
    """Run all tests with detailed output"""
    print("="*60)
    print("COMPREHENSIVE DATABASE TESTING")
    print("="*60)
    
    # Create test suite
    suite = unittest.TestSuite()
    
    # Add test classes
    suite.addTest(unittest.makeSuite(TestDatabase))
    suite.addTest(unittest.makeSuite(TestDatabaseIntegration))
    
    # Run tests with detailed output
    runner = unittest.TextTestRunner(verbosity=0, stream=sys.stdout)
    result = runner.run(suite)
    
    # Print summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    
    if result.testsRun > 0:
        success_rate = ((result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100)
        print(f"Success rate: {success_rate:.1f}%")
    
    if result.failures:
        print(f"\nFAILURES:")
        for test, traceback in result.failures:
            print(f"- {test}")
            print(f"  {traceback}")
    
    if result.errors:
        print(f"\nERRORS:")
        for test, traceback in result.errors:
            print(f"- {test}")
            print(f"  {traceback}")
    
    if len(result.failures) == 0 and len(result.errors) == 0:
        print("\n🎉 ALL TESTS PASSED! Your database functions are working perfectly.")
    else:
        print(f"\n⚠️  Some tests failed. Check the details above.")
    
    return result


if __name__ == '__main__':
    run_tests()